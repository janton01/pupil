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
        requester.send('t') #see Pupil Remote Plugin for details
        return float(requester.recv())

    #...continued from above
    subscriber = ctx.socket(zmq.SUB)
    subscriber.connect('tcp://%s:%s'%(ip,sub_port))
    subscriber.set(zmq.SUBSCRIBE, b'pupil.0') #receive all notification messages
    subscriber.set(zmq.SUBSCRIBE, b'pupil.1') #receive all notification messages
    subscriber.set(zmq.SUBSCRIBE, b'gaze') #receive all notification messages
    subscriber.set(zmq.SUBSCRIBE, b'notify.') #receive all notification messages
    subscriber.set(zmq.SUBSCRIBE, b'logging.error') #receive logging error messages
    subscriber.set(zmq.SUBSCRIBE, b'fixations')
    subscriber.set(zmq.SUBSCRIBE, b'blink.')
    subscriber.set(zmq.SUBSCRIBE, b'Blink_Detection')
    subscriber.set(zmq.SUBSCRIBE, b'Fixation_Detector')
    #subscriber.set(zmq.SUBSCRIBE, b'fixations')

    #subscriber.set(zmq.SUBSCRIBE, '') #receive everything (don't do this)

    # you can setup multiple subscriber sockets
    # Sockets can be polled or read in different threads.

    #requester.send_string('R')
    #print(requester.recv_string())

    #time.sleep(5)
    #requester.send_string('r')
    #print(requester.recv_string())


    # send notification:
    def notify(notification):
        """Sends ``notification`` to Pupil Remote"""
        topic = 'notify.' + notification['subject']
        payload = serializer.dumps(notification, use_bin_type=True)
        requester.send_string(topic, flags=zmq.SNDMORE)
        requester.send(payload)
        return requester.recv_string()

    #test notification, note that you need to listen on the IPC to receive notifications!
    #notify({'subject':"calibration.should_start"})
    #notify({'subject':"calibration.should_stop"})

    n = {'subject':'set_detection_mapping_mode','mode':'3d', 'args':{}}
    print(send_recv_notification(n))


    # set start eye windows
    n = {'subject':'eye_process.should_start.0','eye_id':0, 'args':{}}
    print(send_recv_notification(n))

    #n = {'subject':'blink','eye_id':0, 'args':{}}
    #print(send_recv_notification(n))

    n = {'subject':'eye_process.should_start.1','eye_id':1, 'args':{}}
    print(send_recv_notification(n))
    #time.sleep(2)


    # set calibration method to hmd calibration
    #n = {'subject':'start_plugin','name':'HMD_Calibration', 'args':{}}
    #print(send_recv_notification(n))


    #time.sleep(2)
    #requester.send(b'R')
    # set calibration method to hmd calibration
    #n = {'subject':'service_process.should_stop'}
    #print(send_recv_notification(n))

    i = 0
    while i < 10000:
        i += 1
        topic,payload = subscriber.recv_multipart()
        message = serializer.loads(payload)
        print(str(topic) + ": " + str(message))

    n = {'subject':'eye_process.should_stop.0','eye_id':0, 'args':{}}
    print(send_recv_notification(n))
    time.sleep(1)
    n = {'subject':'eye_process.should_stop.1','eye_id':1, 'args':{}}
    print(send_recv_notification(n))
    #requester.send(b'r')
    return


if __name__== "__main__":
    main()
