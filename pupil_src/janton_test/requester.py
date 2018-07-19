# we need a serializer
import msgpack as serializer
import zmq

def setup_requester(ctx, ip, port):
   # The requester talks to Pupil remote and receives the session unique IPC SUB PORT
    requester = ctx.socket(zmq.REQ)
    requester.connect('tcp://%s:%s'%(ip,port))
    return requester

    # call it notify
def notify(notification):
    """Sends ``notification`` to Pupil Remote"""
    # REQ REP requirese lock step communication with multipart msg (topic,msgpack_encoded dict)
    topic = ('notify.%s'%notification['subject']).encode()
    argument = serializer.dumps(notification, use_bin_type=True)

    # can also send messages individually
    # a) requester.send_string(topic, flags=zmq.SNDMORE)
    # b) requester.send(payload)

    requester.send_multipart((topic,argument))

    return requester.recv_string()

def get_pupil_timestamp():
    requester.send(b't') #see Pupil Remote Plugin for details
    return float(requester.recv())

def unsure_start_recording(session_name):
    requester.send_string("R " + session_name)
    print(requester.recv_string())

def unsure_stop_recording():
    requester.send_string('r')
    print(requester.recv_string())

def start_plugins(plugin_list):
    for plugin in plugin_list:
        start_plugin(plugin)

def start_plugin(plugin_name):
    n = {'subject':'start_plugin','name':plugin_name, 'args':{}}
    print(notify(n))

def start_recording(session_name, recording_path):
    print("START RECORDING!!!")
    n = {'subject': 'recording.should_start', 'session_name': session_name,
        'rec_path': recording_path}#, 'record_eye': True, 'compression': True}
    print(notify(n))

def stop_recording():
    n = {'subject': 'recording.should_stop'}
    print(notify(n))

def annotate(point_location, timestamp):
    n = {'subject': 'annotation', 'label': point_location, 'timestamp': timestamp,
         'duration': 0.0, 'record': True}
    print(requester.recv_string())


def calibrate(points, times_per_point):
    # set calibration method to hmd calibration
    n = {'subject':'start_plugin','name':'HMD_Calibration', 'args':{}}
    print(notify(n))
    sleep(1)
    # start caliration routine with params. This will make pupil start sampeling pupil data.
    n = {'subject':'calibration.should_start', 'hmd_video_frame_size':(1000,1000), 'outlier_threshold':35}
    print(notify(n))

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
            sleep(1/60.) #simulate animation speed.

    # Send ref data to Pupil Capture/Service:
    # This notification can be sent once at the end or multiple times.
    # During one calibraiton all new data will be appended.
    n = {'subject':'calibration.add_ref_data','ref_data':ref_data}
    print(notify(n))

    # stop calibration
    # Pupil will correlate pupil and ref data based on timestamps,
    # compute the gaze mapping params, and start a new gaze mapper.
    n = {'subject':'calibration.should_stop'}
    print(notify(n))

    sleep(2)

def stop_service():
    # can we just do "should start?"
    n = {'subject':'service_process.should_stop'}
    print(notify(n))

def eye_process_start():
    # set start eye windows
    n = {'subject':'eye_process.should_start.0','eye_id':0, 'args':{}}
    print(notify(n))

    n = {'subject':'eye_process.should_start.1','eye_id':1, 'args':{}}
    print(notify(n))
    sleep(2)

def eye_process_end():
    n = {'subject':'eye_process.should_stop.0','eye_id':0, 'args':{}}
    print(notify(n))

    n = {'subject':'eye_process.should_stop.1','eye_id':1, 'args':{}}
    print(notify(n))
    sleep(1)

# TODO JANTON: why args
def setup_general_parameters():
    n = {'subject':'set_detection_mapping_mode','mode':'3d', 'args':{}}
    print(notify(n))

def send_trigger(label, timestamp, duration=0., **custom_keys):
    minimal_trigger.update(custom_keys)
    return notify(minimal_trigger)
