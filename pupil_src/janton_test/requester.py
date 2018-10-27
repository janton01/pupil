# we need a serializer
import msgpack as serializer
import zmq
import time

class Requester():
    def __init__(self, ctx, ip, port):
        # The requester talks to Pupil remote and receives the session unique IPC SUB PORT
        self.requester_socket = ctx.socket(zmq.REQ)
        self.requester_socket.connect('tcp://%s:%s'%(ip,port))
        time.sleep(1)

    def send_string(self, string):
        self.requester_socket.send_string(string)

    def recv_string(self):
        return self.requester_socket.recv_string()

    # call it self.notify
    def notify(self, notification):
        """Sends ``notification`` to Pupil Remote"""
        self.requester_socket.send_string('notify.%s'%notification['subject'], flags=zmq.SNDMORE)
        self.requester_socket.send(serializer.dumps(notification, use_bin_type=True))

        # REQ REP requirese lock step communication with multipart msg (topic,msgpack_encoded dict)
        #topic = ('notify.%s'%notification['subject']).encode()
        #argument = serializer.dumps(notification, use_bin_type=True)

        # can also send messages individually
        # a) requester_socket.send_string(topic, flags=zmq.SNDMORE)
        # b) requester_socket.send(payload)

        #self.requester_socket.send_multipart((topic,argument))
        return self.requester_socket.recv_string()

    def set_3d_detection_mapping_mode(self):
        n = {'subject':'set_detection_mapping_mode','mode':'3d', 'args':{}}
        self.notify(n)

    def get_pupil_timestamp(self):
        self.requester_socket.send(b't') #see Pupil Remote Plugin for details
        return float(self.requester_socket.recv())

    def unsure_start_recording(self, session_name):
        self.requester_socket.send_string("R " + session_name)
        print(self.requester_socket.recv_string())

    def unsure_stop_recording(self):
        self.requester_socket.send_string('r')
        print(self.requester_socket.recv_string())

    def start_plugins(self, plugin_list):
        for plugin in plugin_list:
            print("Starting plugin: " + plugin)
            self.start_plugin(plugin)

    def start_plugin(self, plugin_name):
        n = {'subject':'start_plugin','name':plugin_name, 'args':{}}
        print(self.notify(n))

    def start_recording(self, session_name, recording_path):
        print("START RECORDING!!!")
        n = {'subject': 'recording.should_start', 'session_name': session_name,
            'rec_path': recording_path}#, 'record_eye': True, 'compression': True}
        print(self.notify(n))

    def stop_recording(self):
        n = {'subject': 'recording.should_stop'}
        print(self.notify(n))

    def annotate(self, point_location, timestamp):
        n = {'subject': 'annotation', 'label': point_location, 'timestamp': timestamp,
             'duration': 0.0, 'record': True}
        print(self.requester_socket.recv_string())

    def stop_service(self):
        # can we just do "should start?"
        n = {'subject':'service_process.should_stop'}
        print(self.notify(n))

    def eye_process_start(self):
        # set start eye windows
        n = {'subject':'eye_process.should_start.0','eye_id':0, 'args':{}}
        print(self.notify(n))
        print("completed eye 1")

        n = {'subject':'eye_process.should_start.1','eye_id':1, 'args':{}}
        print(self.notify(n))
        print("completed eye 2")
        time.sleep(2)

    def eye_process_end(self):
        n = {'subject':'eye_process.should_stop.0','eye_id':0, 'args':{}}
        print(self.notify(n))

        n = {'subject':'eye_process.should_stop.1','eye_id':1, 'args':{}}
        print(self.notify(n))
        time.sleep(1)

    # TODO JANTON: why args
    def setup_general_parameters(self):
        n = {'subject':'set_detection_mapping_mode','mode':'3d', 'args':{}}
        print(self.notify(n))

    def send_trigger(self, label, timestamp, duration=0., **custom_keys):
        minimal_trigger.update(custom_keys)
        return self.notify(minimal_trigger)

    def accuracy_test_start(self):
        n = {'subject': 'accuracy_test.should_start'}
        print(self.recv_string())
