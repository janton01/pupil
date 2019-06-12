import zmq
import msgpack as serializer
import time

from msg_receiver import *

class Subscriber():
    def __init__(self, ctx, ip, sub_port):
        # subscriber subscribes to channels and receives notifications
        self.subscriber_socket = ctx.socket(zmq.SUB)
        url = 'tcp://%s:%s'%(ip,sub_port)
        self.subscriber_socket.connect(url)
        #self.subscriber_socket2 = Msg_Receiver(ctx, url=url, topics=b'gaze', hwm=100)
        print("Subscribed")
        time.sleep(1)

    def subscribe_to_topics(self,topic_list):
        for topic in topic_list:
            self.subscribe_to_topic(topic)

    # you can setup multiple subscriber sockets
    # Sockets can be polled or read in different threads.
    def subscribe_to_topic(self,topic_name):
        self.subscriber_socket.set(zmq.SUBSCRIBE, str(topic_name).encode())

    def read_message(self):
        i = 0
        while(self.subscriber_socket.get(zmq.EVENTS)):
        #while(self.subscriber_socket2.socket.get(zmq.EVENTS)):
            #topic, message = self.subscriber_socket2.recv()
            topic,payload = self.subscriber_socket.recv_multipart()
            message = serializer.loads(payload)
            i+=1
        #print(i)
        #import pdb; pdb.set_trace()
        try:
            return topic, message
        except UnboundLocalError as e:
            return None, None
        #import pdb;pdb.set_trace()
