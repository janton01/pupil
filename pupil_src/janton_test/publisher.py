import zmq
import random
import msgpack as serializer
import sys
import time

port = "50021"
if len(sys.argv) > 1:
    port =  sys.argv[1]
    int(port)

context = zmq.Context()
socket = context.socket(zmq.PUB)
print("tcp://*:%s" % port)
socket.bind("tcp://*:%s" % port)

for i in range(1000000):
    topic = "counter"
    messagedata = i
    print("%s %d" % (topic, messagedata))
    n = {'subject':topic,'message':messagedata}
    socket.send_string('notify.%s'%n['subject'], flags=zmq.SNDMORE)
    socket.send(serializer.dumps(n, use_bin_type=True))
    #socket.send("%d %d" % (topic, messagedata))
    time.sleep(1)

