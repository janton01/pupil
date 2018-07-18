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

    requester.send_string('R')
    print(requester.recv_string())
    #...continued from above
    subscriber = ctx.socket(zmq.SUB)
    subscriber.connect('tcp://%s:%s'%(ip,sub_port))
    subscriber.set(zmq.SUBSCRIBE, b'pupil.0') #receive all notification messages
    subscriber.set(zmq.SUBSCRIBE, b'pupil.1') #receive all notification messages
    subscriber.set(zmq.SUBSCRIBE, b'gaze') #receive all notification messages
    subscriber.set(zmq.SUBSCRIBE, b'notify.') #receive all notification messages
    subscriber.set(zmq.SUBSCRIBE, b'logging.error') #receive logging error messages
    # subscriber.set(zmq.SUBSCRIBE, b'fixations')
    # subscriber.set(zmq.SUBSCRIBE, b'blink')
    # subscriber.set(zmq.SUBSCRIBE, b'Blink_Detection')
    # subscriber.set(zmq.SUBSCRIBE, b'Fixation_Detector')

    # # set calibration method to hmd calibration
    # #n = {'subject':'start_plugin','name':'fixations', 'args':{}}
    # #print(send_recv_notification(n))    # set calibration method to hmd calibration
    # #n = {'subject':'start_plugin','name':'blink', 'args':{}}
    # #print(send_recv_notification(n))    # set calibration method to hmd calibration
    # n = {'subject':'start_plugin','name':'Blink_Detection', 'args':{}}
    # print(send_recv_notification(n))    # set calibration method to hmd calibration
    # n = {'subject':'start_plugin','name':'Fixation_Detector', 'args':{}}
    # print(send_recv_notification(n))


    # set calibration method to hmd calibration
    n = {'subject':'start_plugin','name':'HMD_Calibration', 'args':{}}
    print(send_recv_notification(n))

    # start caliration routine with params. This will make pupil start sampeling pupil data.
    n = {'subject':'calibration.should_start', 'hmd_video_frame_size':(1000,1000), 'outlier_threshold':35}
    print(send_recv_notification(n))

    # Mockup logic for sample movement:
    # We sample some reference positions (in normalized screen coords).
    # Positions can be freely defined

    ref_data = []
    for pos in ((0,0),(0,1),(1,1),(1,0)):
        print('subject now looks at position:', pos)
        for s in range(60):
            # you direct screen animation instructions here

            # get the current pupil time (pupil uses CLOCK_MONOTONIC with adjustable timebase).
            # You can set the pupil timebase to another clock and use that.
            t = get_pupil_timestamp()

            # in this mockup  the left and right screen marker positions are identical.
            datum0 = {'norm_pos':pos,'timestamp':t,'id':0}
            datum1 = {'norm_pos':pos,'timestamp':t,'id':1}
            ref_data.append(datum0)
            ref_data.append(datum1)
            time.sleep(1/60.) #simulate animation speed.


    # Send ref data to Pupil Capture/Service:
    # This notification can be sent once at the end or multiple times.
    # During one calibraiton all new data will be appended.
    n = {'subject':'calibration.add_ref_data','ref_data':ref_data}
    print(send_recv_notification(n))

    # stop calibration
    # Pupil will correlate pupil and ref data based on timestamps,
    # compute the gaze mapping params, and start a new gaze mapper.
    n = {'subject':'calibration.should_stop'}
    print(send_recv_notification(n))

    time.sleep(2)


    #subscriber.set(zmq.SUBSCRIBE, '') #receive everything (don't do this)

    # you can setup multiple subscriber sockets
    # Sockets can be polled or read in different threads.


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
    while i < 100:
        i += 1
        topic,payload = subscriber.recv_multipart()
        message = serializer.loads(payload)
        print(str(topic) + ": " + str(message))

    requester.send_string('r')
    print(requester.recv_string())

    n = {'subject':'eye_process.should_stop.0','eye_id':0, 'args':{}}
    print(send_recv_notification(n))
    time.sleep(1)
    n = {'subject':'eye_process.should_stop.1','eye_id':1, 'args':{}}
    print(send_recv_notification(n))


if __name__== "__main__":
    main()
