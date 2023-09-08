class PrintLogger(object):
    """ Mimics ROS Logger / Python Logging System Syntax """
    def debug(self, msg):
        print(msg)

    def info(self, msg):
        print("INFO:", msg)

    def warn(self, msg):
        print("WARN:", msg)

    def error(self, msg):
        print("ERROR:", msg)

def example():
    logger = PrintLogger()
    logger.info("Regular message")
    logger.warn("There is a warning")
    logger.error("Bad thing happened")

if __name__ == "__main__":
    example()
