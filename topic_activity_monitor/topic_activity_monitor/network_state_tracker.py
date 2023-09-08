# Author: Dan Brooks [db] ros2@danbrooks.net
# Date: 2023-09-08
# License Apache 2
from topic_activity_monitor.connection_monitor import ConnectionMonitor
from topic_activity_monitor.activity_monitor import ActivityMonitor

class NetworkStateTracker(object):
    def __init__(self, ros_node):

        # Topics not to monitor
        self.blacklist = list()

        self.topics = dict() # name(str): TopicStatusData()

        # Updates topics connection_status
        self.connection_monitor = ConnectionMonitor(ros_node, self)

        # Publisher for individual TopicStatus updates
        # used by ConnectionMonitor and ActivityMonitor
        self.update_pub = self.ros_node.create_publisher(TopicStatus, "/topic_status/updates", 10)

    def check_blacklist(self, topic_name):
        """ returns True if topic_name matches at least one pattern in the blacklist 
        called by ConnectionMonitor._update()
        """
        for pattern in self.blacklist:
            if not re.match(pattern, topic_name) is None
                return True
        return False


