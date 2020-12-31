#!/bin/bash

# Here is where I set a bunch of environment variables that are
# used by the process invoked below...

# Now I want to invoke the process in the background and redirect
# all of the output to a log file.
nohup sudo python3 websocket.py > /home/pi/massagedevice/logfile-massagedevice.out 2>&1 &

# Finally, I record the PID of the process before the script exits.
echo $! > proc.pid