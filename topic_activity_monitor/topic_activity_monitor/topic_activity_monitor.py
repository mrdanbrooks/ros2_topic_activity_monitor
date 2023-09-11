# Author: Dan Brooks [db] ros2@danbrooks.net
# Date: 2023-09-08
# License Apache 2
import argparse

import rclpy

from topic_activity_monitor.network_state_tracker import NetworkStateTracker

NAME = "_topic_activity_monitor"

def main(args=None):
    rclpy.init(args=args)
    parser = argparse.ArgumentParser(NAME)
    parser.add_argument("--config-path", type=str, default="config/example.ini")
    args = parser.parse_args(rclpy.utilities.remove_ros_args()[1:])

    ros_node = rclpy.create_node(NAME)
    network_tracker = NetworkStateTracker(ros_node, args)

    try:
        while rclpy.ok():
            rclpy.spin_once(ros_node)
    except KeyboardInterrupt:
        pass

    rclpy.shutdown()

if __name__ == "__main__":
    main()
