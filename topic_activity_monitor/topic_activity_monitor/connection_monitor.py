# Author: Dan Brooks [db] ros2@danbrooks.net
# Date: 2023-09-08
# License Apache 2
import time

from topic_activity_monitor.lib.find_current_endpoints import find_current_endpoints
from topic_activity_monitor.lib.topic_status_data import TopicStatusData, ConnectionStatus

class ConnectionMonitor(object):
    """ Watches ROS network for topic publishers and subscribers 
    Updates TopicActivityMonitor.topics dictionary
    """
    def __init__(self, ros_node, network_state_tracker):
        self.ros_node = ros_node
        self.logger = ros_node.get_logger()
        self.network_state_tracker = network_state_tracker
        
        self._update_timer = self.ros_node.create_timer(0.1, self._update)

    def _update(self):
        """  updates topic connection statuses 
        Called by _update_timer """
        publishers, subscribers = find_current_endpoints(self.ros_node)

        all_topic_names = list(publishers.keys()) + list(subscribers.keys())

        # Add New Topics
        for topic_name in all_topic_names:
            # Skip topics in blacklist
            if self.network_state_tracker.check_blacklist(topic_name):
                continue
            # Add new topics to list
            if topic_name not in self.network_state_tracker.topics.keys():
                msg_type_name = publishers[topic_name] if topic_name in publishers else subscribers[topic_name]
                self.network_state_tracker.topics[topic_name] = TopicStatusData(topic_name, msg_type_name, self.logger)
                self.logger.info("Adding topic %s" % topic_name)

        # Update topics TopicStatusData.connection_status
        for topic_name, topic_status_data in self.network_state_tracker.topics.items():
            if topic_name in publishers.keys():
                topic_status_data.connection_status = ConnectionStatus.PRESENT
            elif topic_name in subscribers.keys():
                topic_status_data.connection_status = ConnectionStatus.MISSING
            else:
                topic_status_data.connection_status = ConnectionStatus.DISCONNECTED

            # Publish update for this topic
            topic_status_data.timestamp = time.time()
            self.network_state_tracker.update_pub.publish(topic_status_data.to_msg())





