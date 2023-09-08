# Author: Dan Brooks [db] ros2@danbrooks.net
# Date: 2023-09-08
# License Apache 2
import time

import numpy as np
from threading import Thread, RLock

import rclpy
from rosidl_runtime_py.utilities import get_message

from topic_activity_monitor.network_state_tracker import NetworkStateTracker
from topic_activity_monitor.lib.better_timer import BetterTimer

class ActivityMonitor(object):
    def __init__(self, network_state_tracker, config):
        self.ros_node = network_state_tracker.ros_node
        self.logger = ros_node.get_logger()
        self.network_state_tracker = network_state_tracker

        self._topic_name = config["TOPIC_NAME"]
        # The following memebers are made available via TopicStatusData
        # self.topic_name
        # self.msg_type_name
        # self.timestamp
        # self.valid_duration
        # self.activity_deadline
        # self.activity_slow_count
        # self.activity_timeout
        # self.activity_timeout_count
        
        # Get class type for topic
        self._msg_type = get_message(self.msg_type_name)

        # ActivityMonitoring Settings
        self._window_size = config["WINDOW_SIZE"]
        self._reconnect_wait_time = config["RECONNECT_WAIT_TIME"]


        # Connection
        self._subscription = None      # Connection to the ROS Topic
        self._reconnect_timer = None   # Reconnection Timer
        self._running = False
        self._lock = RLock()           # Lock
        self._watchdog = BetterTimer(self.ros_node, self.activity_timeout, self._timeout_callback)

        # Time Stamp Data Buffer
        self.timestamp_buffer = Buffer(config["WINDOW_SIZE"])
 
        self.logger.info("Adding monitor for %s" % self.topic_name)

    def __getattribute__(self, value_name):
        """ get certain attributes from the TopicStatusData """
        if value_name not in ["topic_name", "msg_type_name", "timestamp", "valid_duration", "activity_status",
                        "activity_deadline", "activity_slow_count", "activity_timeout", "activity_timeout_count"]:
            return getattr(self.network_state_tracker.topics[self._topic_name], value_name)
        return super().__getattribute__(value_name)

    def start_monitor(self):
        self._running = True
        self._subscribe()

    def stop_monitor(self):
        if self._subscribed():
            self._running = False
            if not self._reconnect_timer is None:
                self._reconnect_timer.cancel()
                self._reconnect_timer = None
            self._unsubscribe()


    def _subscribe(self):
        """ Subscribes to topic """
        with self._lock:
            if not self._running:
                return
            if not self._subscription is None:
                self.logger.warn("_connect(): restart subscription %s failed. Already running" % self.topic_name)
                return False

            self._subscription = self.ros_node.create_subscription(self._msg_type, self.topic_name, self._topic_callback, self._window_size)
            self._watchdog.start()
            return True

    def _unsubscribe(self):
        """ unsubscribe from topic """
        with self._lock:
            if self._subscription is None:
                self.logger.warn("Attempting to unsubscribe from %s without a subscription" % self.topic_name)
                return False

            success = self.ros_node.destroy_subscription(self._subscription)
            self._watchdog.cancel()
            self.timestamp_buffer.clear()
            if not success:
                self.logger.warn("Failed to unsubscribe from %s" % self.topic_name)
            else:
                self._subscription = None
            return success

    def _subscribed(self):
        if self._subscription is not None:
            return True
        return False

    def _topic_callback(self, msg):
        """ ROS subscription callback """
        # Reasons for ignoring messages
        # - We might still have messages in the queue after unsubscribing.
        # - We are not running
        # - timestamp buffer is already full. We don't need anymore data.
        if self._subscription is None or not self._running or self.timestamp_buffer.full():
            return

        with self._lock:
            assert(self._subscription is not None)

            # Add timestamp to buffer
            self.timestamp_buffer.push(time.time())

            # Cancel watchdog
            self._watchdog.cancel()

            # When the buffer is full, compute report, disconnect, and wait to reconnect
            if self.timestamp_buffer.full():
                intervals = np.diff(np.array(self.timestamp_buffer))
                self.logger.info("%s: %s" % (self._topic_name, intervals))

                # Compute time between messages
                if np.all(np.less(intervals, self.activity_deadline)):
                    # All the messages arrived on time
                    self.activity_status = ActivityStatus.ACTIVE
                else:
                    # Some of the messages were received after the stated deadline
                    self.activity_status = ActivityStatus.SLOW
                    self.activity_slow_count += 1

                # Empty the timestamp buffer
                self.timestamp_buffer.clear()

                # Discnonnect from topic and set a timer for when to reconnect
                self._unsubscribe()
                assert(self._reconnect_timer is None)
                self._reconnect_timer = self.ros_node.create_timer(self._reconnect_wait_time, self._reconnect_timer_callback)

                # Broadcast the current activity status
                self._publish_update()

    def _reconnect_timer_callback(self):
        with self._lock:
            self._reconnect_timer.cancel()
            self._reconnect_timer = None
            self._subscribet()

    def _timeout_callback(self):
        """ called by watchdog timer """
        # TIMEOUT STATE - we failed to receive any messages prior to the TIMEOUT watchdog timer going off
        self.logger.warn("%s Timeout!" % self._topic_name)
        self.activity_status = ActivityStatus.TIMEOUT
        self.activity_timeout_count += 1
        self._publish_update()


    def _publish_update(self):
        """ Publish TopicStatus() for this ActivityMonitor """
        self.timestamp = time.time()
        self.valid_duration = self.activity_timeout * 1.5
        topic_status_data = self.network_state_tracker.topics[self._topic_name]
        self.network_state_tracker.update_pub.publish(topic_status_data.to_msg()
