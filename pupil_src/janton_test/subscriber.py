import zmq
import msgpack as serializer
import time

class Subscriber():
    def __init__(self, ctx, ip, sub_port):
        # subscriber subscribes to channels and receives notifications
        self.subscriber_socket = ctx.socket(zmq.SUB)
        self.subscriber_socket.connect('tcp://%s:%s'%(ip,sub_port))
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
        topic,payload = self.subscriber_socket.recv_multipart()
        message = serializer.loads(payload)
        return topic, message
