# Author: Dan Brooks [db] ros2@danbrooks.net
# Date: 2023-09-08
# License Apache 2

def find_current_endpoints(ros_node):
    """ returns dictionaries of all current publishers and subscribers from scratch """

    publishers = dict()   # name(str): msg_type_name(str)
    subscribers = dict()  # name(str): msg_type_name(str)

    # List nodes in the network
    nodes = ros_node.get_node_names_and_namespaces()

    # remove ourself from the list
    nodes.remove((ros_node.get_name(), ros_node.get_namespace()))

    # For each node, get list of publishers and subscribers
    for node_name, node_namespace in nodes:

        # Get Subscribers
        nodes_subscribers = ros_node.get_subscriber_names_and_types_by_node(node_name, node_namespace)
        # Look for new topics
        for topic_name, msg_type_names in nodes_subscribers:
            if not topic_name in subscribers.keys():
                # Add subscriber
                subscribers[topic_name] = msg_type_names[0]
                if len(msg_type_names) > 1:
                    ros_node.get_logger().warn("Topic %s has multiple types!" % topic_name)

        # Get Publishers
        nodes_publishers = ros_node.get_publisher_names_and_types_by_node(node_name, node_namespace)
        # Look for new topics
        for topic_name, msg_type_names in nodes_publishers:
            if not topic_name in publishers.keys():
                # Add publisher
                publishers[topic_name] = msg_type_names[0]
                # Check for type missmatch 
                if topic_name in subscribers.keys() and not subscribers[topic_name] == msg_type_names[0]:
                    ros_node.get_logger().warn("Topic %s publisher type '%s' and subscriber type '%s' mismatch" % (topic_name, publishers[topic_name], subscribers[topic_name]))
                if len(msg_type_names) > 1:
                    ros_node.get_logger().warn("Topic %s has multiple type!" % topic_name)

    return [publishers, subscribers]
