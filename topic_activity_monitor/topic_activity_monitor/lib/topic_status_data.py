# Author: Dan Brooks [db] ros2@danbrooks.net
# Date: 2023-09-08
# License Apache 2
from enum import Enum
from topic_activity_monitor_msgs.msg import TopicStatus
from topic_activity_monitor.lib.print_logger import PrintLogger

class ConnectionStatus(Enum):
# These match topic_activity_monitor_msgs/msg/TopicStatus.msg
    UNDEFINED    = 0
    PRESENT      = 1  # Publisher connected (subscriber may or may not be connected)
    MISSING      = 2  # Publisher missing, but subscriber connected
    DISCONNECTED = 3  # No publishers or subscribers

class ActivityStatus(Enum):
# These match topic_activity_monitor_msgs/msg/TopicStatus.msg
    UNDEFINED     = 0
    ACTIVE        = 1  # Data received on time
    SLOW          = 2  # Data received, but slower than deadline
    TIMEOUT       = 3  # No data received since last connection
    NOT_MONITORED = 4  # Activity not being monitored


class TopicStatusData(object):
    """ Mirrors the TopicStatus.msg
    """
    def __init__(self, name, msg_type, logger=PrintLogger()):
        self.logger = logger

        # Track if we have received any changes since the last time has_update() was called
        self._updated = False

        self._topic_name = name
        self._msg_type_name = msg_type

        self._timestamp = 0.0
        self._valid_duration = 0.0

        self._connection_status = ConnectionStatus.UNDEFINED

        self._activity_status = ActivityStatus.UNDEFINED
        self._activity_deadline = 0.0
        self._activity_slow_count = 0
        self._activity_timeout = 0.0
        self._activity_timeout_count = 0

    def __setattr__(self, name, value):
        if name in ["topic_name", "msg_type_name", "timestamp", "valid_duration", "connection_status", "activity_status", 
                    "activity_deadline", "activity_slow_count", "activity_timeout", "activity_timeout_count"]:
            setter_fun = getattr(self, "_set_" + name)
            setter_fun(value)
        else:
            super().__setattr__(name, value)

    def __getattribute__(self, name):
        if name not in ["topic_name", "msg_type_name", "timestamp", "valid_duration", "connection_status", "activity_status",
                        "activity_deadline", "activity_slow_count", "activity_timeout", "activity_timeout_count"]:
            return super().__getattribute__(name)
        return super().__getattribute__("_" + name)

    def _set_topic_name(self, value: str):
        raise Exception("TopicStatusData.topic_name is read only")

    def _set_msg_type_name(self, value: str):
        raise Exception("TopicStatusData.msg_type_name is read only")

    def _set_timestamp(self, timestamp):
        if not self._timestamp == timestamp:
            self._updated = True
            self._timestamp = timestamp

    def _set_valid_duration(self, valid_duration):
        if not self._valid_duration == valid_duration:
            self._updated = True
            self._valid_duration = valid_duration


    def _set_activity_status(self, status):
        if isinstance(status, int):
            status = ActivityStatus(status)
        if not isinstance(status, ActivityStatus):
            raise ValueError("TopicStatusData.activity_status must be type int or ActivityStatus()")
        if not self._activity_status == status:
            self._updated = True
            self._activity_status = status

    def _set_connection_status(self, status):
        if isinstance(status, int):
            status = ConnectionStatus(status)
        if not isinstance(status, ConnectionStatus):
            raise ValueError("TopicStatusData.connection_status must be type int or ConnectionStatus()")
        if not self._connection_status == status:
            self._updated = True
            self._connection_status = status

    def _set_activity_slow_count(self, count):
        if self._activity_slow_count > count:
            self._logger.warn("%s.activity_slow_count decreased from %d to %d" % (self._name, self._slow_count, count))
        if not self._activity_slow_count == count:
            self._updated = True
            self._activity_slow_count = count

    def _set_activity_deadline(self, activity_deadline):
        if not self._activity_deadline == activity_deadline:
            self._updated = True
            self._activity_deadline = activity_deadline

    def _set_activity_timeout(self, activity_timeout):
        if not self._activity_timeout == activity_timeout:
            self._updated = True
            self._activity_timeout = activity_timeout

    def _set_activity_timeout_count(self, count):
        if self._activity_timeout_count > count:
            self._logger.warn("%s.activity_timeout_count decreased from %d to %d" % (self._name, self._timeout_count, count))
        if not self._activity_timeout_count == count:
            self._updated = True
            self._activity_timeout_count = count

    def has_update(self):
        """ returns True if information was updated since last time this was called """
        if self._updated:
            self._updated = False
            return True
        return False

    def update_from_msg(self, msg):
        """ update based on TopicStatus.msg """
        assert(isinstance(msg, TopicStatus))
        assert(msg.topic_name == self._name)
        assert(msg.msg_type == self._msg_type)

        self.timestamp = msg.timestamp
        self.valid_duration = msg.valid_duration

        self.connection_status = ConnectionStatus(msg.connection_status)
        self.activity_status = ActivityStatus(msg.activity_status)

        self.activity_deadline = msg.activity_deadline
        self.activity_slow_count = msg.activity_slow_count

        self.activity_timeout = msg.activity_timeout
        self.activity_timeout_count = msg.activity_timeout_count

    def to_msg(self):
        """ returns TopicStatus.msg """
        msg = TopicStatus()
        msg.topic_name = self._topic_name
        msg.msg_type = self._msg_type_name
        msg.timestamp = self._timestamp
        msg.valid_duration = self._valid_duration
        msg.connection_status = self._connection_status.value
        msg.activity_status = self._activity_status.value
        msg.activity_deadline = self._activity_deadline
        msg.activity_slow_count = self._activity_slow_count
        msg.activity_timeout = self._activity_timeout
        msg.activity_timeout_count = self._activity_timeout_count
        return msg




def test():
    topic_status_data = TopicStatusData()

