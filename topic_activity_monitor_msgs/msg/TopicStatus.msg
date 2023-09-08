string topic_name
string msg_type

float64 timestamp             # time.time()
float64 valid_duration        # elapsed time (in seconds) from timestamp before information is invalid

uint8 connection_status       # Information regarding connectivity of topic
uint8 CONN_UNDEFINED    = 0
uint8 CONN_PRESENT      = 1   # Publisher Present
uint8 CONN_MISSING      = 2   # Publisher Missing, Subscriber Present
uint8 CONN_DISCONNECTED = 3   # No Publishers or Subscribers

uint8 activity_status         # Information regarding activity of topic
uint8 ACT_UNDEFINED     = 0
uint8 ACT_ACTIVE        = 1   # Activity Monitoring, Data Received, On Time
uint8 ACT_SLOW          = 2   # Activity Monitoring, Data Received, Slower than Deadline
uint8 ACT_TIMEOUT       = 3   # Activity Monitoring, Timeout Reached before any data was received
uint8 ACT_NOT_MONITORED = 4   # Activity Monitoring Not Being Used

int64 activity_deadline       # Upper bound on time between messages, before they are "slow"
int64 activity_slow_count     # number of missed deadlines

int64 activity_timeout        # Max delay after last message received
int64 activitY_timeout_count  # number of timeouts
