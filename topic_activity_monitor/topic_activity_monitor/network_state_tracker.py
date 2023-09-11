# Author: Dan Brooks [db] ros2@danbrooks.net
# Date: 2023-09-08
# License Apache 2
import argparse
import configparser
import json
import time
import os
import re

from topic_activity_monitor_msgs.msg import TopicStatus

from topic_activity_monitor.lib.topic_status_data import TopicStatusData, ActivityStatus
from topic_activity_monitor.connection_monitor import ConnectionMonitor
from topic_activity_monitor.activity_monitor import ActivityMonitor

# Get script's directory so we can find relative path resources
DIR = os.path.realpath(os.path.dirname(__file__))


class NetworkStateTracker(object):
    def __init__(self, ros_node, args):
        self.ros_node =ros_node
        self.logger = ros_node.get_logger()

        # Topics not to monitor - set by _load_config_file()
        self.blacklist = list()

        # Activity Monitor List
        self.activity_monitors = dict() # name(str): ActivityMonitor()

       # TopicStatusData() List - list of all the topics we are tracking
        self.topics = dict() # name(str): TopicStatusData()
        #TODO: Send out aggregated List of TopicStatusData

        #TODO: Create watchdogs that invalidates statuses if we don't hear them updated on a regular basis (use timeout value x 1.5 ?)
        #self._topics_watchdog_timer = self.ros_node.create_timer(0.5, self._topics_watchdog_callback)

        # Load config
        self._load_config_file(os.path.join(DIR, args.config_path))
 
        # Updates topics connection_status (must be started after config has been loaded)
        self.connection_monitor = ConnectionMonitor(ros_node, self)

        # Publisher for individual TopicStatus updates
        # used by ConnectionMonitor and ActivityMonitor
        self.update_pub = self.ros_node.create_publisher(TopicStatus, "/topic_status/updates", 10)

    def check_blacklist(self, topic_name):
        """ returns True if topic_name matches at least one pattern in the blacklist 
        called by ConnectionMonitor._update()
        """
        for pattern in self.blacklist:
            if not re.match(pattern, topic_name) is None:
                return True
        return False

    def _load_config_file(self, config_file_path):
        """ 
        - loads blacklist
        - populates topics for those with activity monitoring
        """

        self.logger.info("Loading Config from '%s'" % config_file_path)
        config_file = configparser.ConfigParser(inline_comment_prefixes=('#'))
        config_file.read(config_file_path)

        # Read Settings 
        self.blacklist += json.loads(config_file.get("SETTINGS", "blacklist"))
        self.logger.info("Blacklist: %s" % self.blacklist)


        # Read Individual Topic Configurations
        for section_name in config_file.sections():
            # Skip well named sections that are not topic configs
            if section_name == "SETTINGS":
                continue

            topic_name = section_name
            try:
                config = dict()
                config["TOPIC_NAME"] = topic_name
                config["TYPE"] = config_file.get(topic_name, "TYPE")
                config["DEADLINE"] = config_file.getfloat(topic_name, "DEADLINE")
                config["TIMEOUT"] = config_file.getfloat(topic_name, "TIMEOUT")
                config["WINDOW_SIZE"] = config_file.getint(topic_name, "WINDOW_SIZE")
                config["RECONNECT_WAIT_TIME"] = config_file.getfloat(topic_name, "RECONNECT_WAIT_TIME")
            except configparser.NoOptionError as e:
                raise SystemExit("Error reading config '%s':\n%s" % (config_path, e))
            except ValueError as e:
                raise SystemExit("Error reading config '%s':\n%s" % (config_path, e))

            # Skip setting up topics in the blacklist
            if self.check_blacklist(topic_name):
                continue
 
            # Add topic, configure with settings from the config
            assert(topic_name not in self.topics.keys())
            self.topics[topic_name] = TopicStatusData(topic_name, config["TYPE"], self.logger)
            self.topics[topic_name].activity_deadline = config["DEADLINE"]
            self.topics[topic_name].activity_timeout = config["TIMEOUT"]

            # Setup Activity Monitor for topic
            activity_monitor = ActivityMonitor(self, config)
            activity_monitor.start_monitor()
            self.activity_monitors[topic_name] = activity_monitor

            # Check the values match requirements
            assert(config["WINDOW_SIZE"] >= 2), "%s: WINDOW_SIZE must be >= 2. Received %d" % (topic_name, config["WINDOW_SIZE"])

