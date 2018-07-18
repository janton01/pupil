import zmq,time
# we need a serializer
import msgpack as serializer


topic_list = ["pupil.0",
              "pupil.1",
              "gaze",
              "notify",
              "logging.error",
              "Blink_Detection",
              "blink",
              "fixations",
              "Annotation_Capture",
              "fixation_detector"]
              #''] # this would receive everything

non_calibration_plugins = ['Blink_Detection',
                           'Fixation_Detector',
                           'Annotation_Capture']

calibration_times_per_point = 60

calibration_points = ((0,0),(0,1),(1,1),(1,0))
ip = 'localhost' #If you talk to a different machine use its IP.

# is this the requester port?
port = 50020 #The port defaults to 50020 but can be set in the GUI of Pupil Capture
recording_path = "/Users/JorgeMain/Box Sync/Jorge Work/Post-Tufts/2017/Tarseer/Tech/Software/pupil/pupil_src/janton_test/recordings"
session_name = "test"

def main():
    def setup_requester(ctx, ip, port):
       # The requester talks to Pupil remote and receives the session unique IPC SUB PORT
        requester = ctx.socket(zmq.REQ)
        requester.connect('tcp://%s:%s'%(ip,port))
        return requester

    def setup_subscriber(ctx, ip, sub_port):
        # subscriber subscribes to channels and receives notifications
        subscriber = ctx.socket(zmq.SUB)
        subscriber.connect('tcp://%s:%s'%(ip,sub_port))
        return subscriber

    def setup_IPC_backbone():
        # setup IPC backbone
        ctx = zmq.Context()
        requester = setup_requester(ctx, ip, port)
        requester.send_string('SUB_PORT')
        sub_port = requester.recv_string()
        subscriber = setup_subscriber(ctx, ip, sub_port)
        return requester, subscriber

    requester, subscriber = setup_IPC_backbone()


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


    def subscribe_to_topics(topic_list):
        for topic in topic_list:
            subscribe_to_topic(topic)

    # you can setup multiple subscriber sockets
    # Sockets can be polled or read in different threads.
    def subscribe_to_topic(topic_name):
        subscriber.set(zmq.SUBSCRIBE, str(topic_name).encode())

    def start_plugin(plugin_name):
        n = {'subject':'start_plugin','name':plugin_name, 'args':{}}
        print(send_recv_notification(n))

    def start_recording(session_name, recording_path):
        print("START RECORDING!!!")
        n = {'subject': 'recording.should_start', 'session_name': session_name,
            'rec_path': recording_path, 'record_eye': True, 'compression': True}
        print(send_recv_notification(n))

    def stop_recording():
        n = {'subject': 'recording.should_stop'}
        print(send_recv_notification(n))

    def annotate(point_location, timestamp):
        n = {'subject': 'annotation', 'label': point_location, 'timestamp': timestamp,
             'duration': 0.0, 'record': True}
        print(requester.recv_string())


    def calibrate(points, times_per_point):
        # set calibration method to hmd calibration
        n = {'subject':'start_plugin','name':'HMD_Calibration', 'args':{}}
        print(send_recv_notification(n))
        time.sleep(1)
        # start caliration routine with params. This will make pupil start sampeling pupil data.
        n = {'subject':'calibration.should_start', 'hmd_video_frame_size':(1000,1000), 'outlier_threshold':35}
        print(send_recv_notification(n))

        # Mockup logic for sample movement:
        # We sample some reference positions (in normalized screen coords).
        # Positions can be freely defined

        ref_data = []
        for pos in calibration_points:
            print('subject now looks at position:', pos)
            for s in range(calibration_times_per_point):
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

    def stop_service():
        # can we just do "should start?"
        n = {'subject':'service_process.should_stop'}
        print(send_recv_notification(n))

    def eye_process_start():
        # set start eye windows
        n = {'subject':'eye_process.should_start.0','eye_id':0, 'args':{}}
        print(send_recv_notification(n))

        n = {'subject':'eye_process.should_start.1','eye_id':1, 'args':{}}
        print(send_recv_notification(n))
        time.sleep(2)

    def eye_process_end():
        n = {'subject':'eye_process.should_stop.0','eye_id':0, 'args':{}}
        print(send_recv_notification(n))

        n = {'subject':'eye_process.should_stop.1','eye_id':1, 'args':{}}
        print(send_recv_notification(n))
        time.sleep(1)

    def read_message():
        topic,payload = subscriber.recv_multipart()
        message = serializer.loads(payload)
        return topic, message

    # TODO JANTON: why args
    def setup_general_parameters():
        n = {'subject':'set_detection_mapping_mode','mode':'3d', 'args':{}}
        print(send_recv_notification(n))

    setup_general_parameters()
    return

    subscribe_to_topics(topic_list)
    eye_process_start()
    start_recording(session_name, recording_path)
    i = 0
    while i < 100:
        i += 1
        topic, message = read_message()
        print(str(topic) + ": " + str(message))

    stop_recording()
    eye_process_end()


if __name__== "__main__":
    main()

# Chose either the one above or the fone below to send/receive notification:
def notify(notification):
    """Sends ``notification`` to Pupil Remote"""
    topic = 'notify.' + notification['subject']
    payload = serializer.dumps(notification, use_bin_type=True)
    requester.send_string(topic, flags=zmq.SNDMORE)
    requester.send(payload)
    return requester.recv_string()

def setup_plugin_parameters():
    pass

def accuracy_test_start():
    n = {'subject': 'accuracy_test.should_start'}
    print(requester.recv_string())

def unsure_start_recording():
    requester.send_string('R')
    print(requester.recv_string())

def unsure_stop_recording():
    requester.send_string('r')
    print(requester.recv_string())
