import zmq,time
# we need a serializer
import msgpack as serializer


def main():
    ctx = zmq.Context()
    # The requester talks to Pupil remote and receives the session unique IPC SUB PORT
    requester = ctx.socket(zmq.REQ)
    ip = 'localhost' #If you talk to a different machine use its IP.
    port = 50020 #The port defaults to 50020 but can be set in the GUI of Pupil Capture
    requester.connect('tcp://%s:%s'%(ip,port))
    requester.send_string('SUB_PORT')
    sub_port = requester.recv_string()
    print(sub_port)

    #convenience functions
    def send_recv_notification(n):
        # REQ REP requirese lock step communication with multipart msg (topic,msgpack_encoded dict)
        print(serializer.dumps(n))
        message = ('notify.%s'%n['subject'], serializer.dumps(n))
        test = (message[0].encode(), message[1])

        print(test)
        requester.send_multipart(test)
        #requester.send_multipart(('notify.%s'%n['subject'], serializer.dumps(n)))
        return requester.recv()

    def get_pupil_timestamp():
        requester.send(b't') #see Pupil Remote Plugin for details
        return float(requester.recv())


    subscriber = ctx.socket(zmq.SUB)
    subscriber.connect('tcp://%s:%s'%(ip,sub_port))

    subscriber.set(zmq.SUBSCRIBE, b'notify.') #receive all notification messages
    subscriber.set(zmq.SUBSCRIBE, b'logging.error') #receive logging error messages

    # send notification:
    def notify(notification):
        """Sends ``notification`` to Pupil Remote"""
        topic = 'notify.' + notification['subject']
        payload = serializer.dumps(notification, use_bin_type=True)
        requester.send_string(topic, flags=zmq.SNDMORE)
        requester.send(payload)
        return requester.recv_string()

    i = 0
    while i < 100:
        i += 1
        topic,payload = subscriber.recv_multipart()
        message = serializer.loads(payload)
        print(str(topic) + ": " + str(message))


if __name__== "__main__":
    main()
