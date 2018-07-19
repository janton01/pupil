import zmq
from time import sleep, time
from requester import *
from subscriber import *

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
recording_path = '/Users/JorgeMain/Box Sync/Jorge Work/Post-Tufts/2017/Tarseer/Tech/Software/pupil/pupil_src/janton_test/recordings'
session_name = "test"

def setup_IPC_backbone():
    # setup IPC backbone
    ctx = zmq.Context()
    requester = setup_requester(ctx, ip, port)
    requester.send_string('SUB_PORT')
    sub_port = requester.recv_string()
    subscriber = setup_subscriber(ctx, ip, sub_port)
    return requester, subscriber

def main():
    requester, subscriber = setup_IPC_backbone()

    subscribe_to_topics(topic_list)
    start_plugins(non_calibration_plugins)
    eye_process_start()
    # In order for the annotations to be correlated correctly with the rest of
    # the data it is required to change Pupil Capture's time base to this scripts
    # clock. We only set the time base once. Consider using Pupil Time Sync for
    # a more precise and long term time synchronization
    time_fn = time  # Use the appropriate time function here

    # Set Pupil Capture's time base to this scripts time. (Should be done before
    # starting the recording)
    requester.send_string('T {}'.format(time_fn()))
    print(requester.recv_string())

    requester.send_string('R')
    requester.recv_string()

    sleep(1.)  # sleep for a few seconds, can be less

    # Send a trigger with the current time
    # The annotation will be saved to the pupil_data notifications if a
    # recording is running. The Annotation_Player plugin will automatically
    # retrieve, display and export all recorded annotations.
    label = 'custom_annotation_label'
    duration = 0.
    minimal_trigger = {'subject': 'annotation', 'label': label,
                       'timestamp': time_fn(), 'duration': duration,
                       'record': True}


    notify(minimal_trigger)
    sleep(1.)  # sleep for a few seconds, can be less

    minimal_trigger = {'subject': 'annotation', 'label': label,
                       'timestamp': time_fn(), 'duration': duration,
                       'record': True}
    # add custom keys to your annotation
    minimal_trigger['custom_key'] = 'custom value'
    notify(minimal_trigger)
    sleep(1.)  # sleep for a few seconds, can be less

    requester.send_string('r')
    requester.recv_string()



    start_recording(session_name, recording_path)
    #unsure_start_recording(session_name)
    i = 0
    while i < 10:
        i += 1
        topic, message = read_message()
        print(str(topic) + ": " + str(message))

    stop_recording()
    #unsure_stop_recording()
    eye_process_end()
    # close socket


if __name__== "__main__":
    main()

def setup_plugin_parameters():
    pass

def accuracy_test_start():
    n = {'subject': 'accuracy_test.should_start'}
    print(requester.recv_string())


