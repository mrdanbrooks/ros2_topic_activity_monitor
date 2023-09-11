import rclpy

class BetterTimer(object):
    """ This wrapper around rclpy.Node.create_timer that tracks the duration to allow stopping and restarting """
    def __init__(self, ros_node, time, callback):
        self._ros_node = ros_node
        self._time = time
        self._timer = None
        self._callback = callback

    def start(self):
        self._timer = self._ros_node.create_timer(self._time, self._callback)

    def cancel(self):
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

