import zmq
def setup_subscriber(ctx, ip, sub_port):
        # subscriber subscribes to channels and receives notifications
        subscriber = ctx.socket(zmq.SUB)
        subscriber.connect('tcp://%s:%s'%(ip,sub_port))
        return subscriber

def subscribe_to_topics(topic_list):
    for topic in topic_list:
        subscribe_to_topic(topic)

# you can setup multiple subscriber sockets
# Sockets can be polled or read in different threads.
def subscribe_to_topic(topic_name):
    subscriber.set(zmq.SUBSCRIBE, str(topic_name).encode())

def read_message():
    topic,payload = subscriber.recv_multipart()
    message = serializer.loads(payload)
    return topic, message
