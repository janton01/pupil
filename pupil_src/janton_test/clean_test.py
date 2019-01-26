import zmq
import time
from requester import Requester
from subscriber import Subscriber

topic_list = ["pupil.0",
              "pupil.1",

              "gaze",
              "notify",
              "logging.error",
              "Blink_Detection",
              "blink",
              "fixations",
              "Annotation_Capture",
              "Fixation_Detector",
              "fixation_detector"]
#''] # this would receive everything

non_calibration_plugins = ['Blink_Detection',
                           'Fixation_Detector']#,
                           #'Annotation_Capture']

calibration_times_per_point = 60

calibration_points = ((0, 0), (0, 1), (1, 1), (1, 0))
ip = 'localhost'  # If you talk to a different machine use its IP.

# is this the requester port?
port = 50020  # The port defaults to 50020 but can be set in the GUI of Pupil Capture
recording_path = '/Users/JorgeMain/Box Sync/Jorge Work/Post-Tufts/2017/Tarseer/Tech/Software/pupil/pupil_src/janton_test/recordings'
session_name = "test"


def main():
    # setup IPC backbone
    ctx = zmq.Context()
    requester, subscriber = setup_subscriber_requester(ctx)

    #subscriber.subscribe_to_topics(topic_list)
    #print("topics subscribed to")

    requester.start_plugins(non_calibration_plugins)
    #print("plugins ready")
    # has to happen before eye process starts
    #calibrate(requester, calibration_points, calibration_times_per_point)

    requester.eye_process_start()
    print("eye process started")

    requester.unsure_start_recording(session_name) # NOT WORKING
    #requester.start_recording(session_name, recording_path)

    requester.set_3d_detection_mapping_mode()

    time.sleep(5)

    #i = 0
    #while i < 100:
    #    i += 1
    #    topic,message = subscriber.read_message()
    #    print(str(topic) + ": " + str(message))

    requester.eye_process_end()
    print("done")
    requester.unsure_stop_recording()
    #requester.stop_recording()


    return

def setup_subscriber_requester(context):
    requester = Requester(context, ip, port)
    print("Requester ready")
    requester.send_string('SUB_PORT')
    sub_port = requester.recv_string()
    print(sub_port)
    subscriber = Subscriber(context, ip, sub_port)
    print("subscriber ready")
    return requester, subscriber


def start_calibration(requester, hmd_video_frame_size, outlier_threshold):
    # set calibration method to hmd calibration
    n = {'subject': 'start_plugin', 'name': 'HMD_Calibration', 'args': {}}
    print(requester.notify(n))
    time.sleep(1)
    # start caliration routine with params. This will make pupil start sampeling pupil data.
    n = {'subject': 'calibration.should_start',
         'hmd_video_frame_size': hmd_video_frame_size, 'outlier_threshold': 35}
    print(requester.notify(n))

def end_calibration(requester, ref_data):
    # Send ref data to Pupil Capture/Service:
    # This notification can be sent once at the end or multiple times.
    # During one calibraiton all new data will be appended.
    print(ref_data)
    n = {'subject': 'calibration.add_ref_data', 'ref_data': ref_data}
    print(requester.notify(n))

    # stop calibration
    # Pupil will correlate pupil and ref data based on timestamps,
    # compute the gaze mapping params, and start a new gaze mapper.
    n = {'subject': 'calibration.should_stop'}
    print(requester.notify(n))
    pass

def get_calibration_data(requester, position):
    # you direct screen animation instructions here

    # get the current pupil time (pupil uses CLOCK_MONOTONIC with adjustable timebase).
    # You can set the pupil timebase to another clock and use that.
    t = requester.get_pupil_timestamp()

    # in this mockup  the left and right screen marker positions are identical.
    datum0 = {'norm_pos': position, 'timestamp': t, 'id': 0}
    datum1 = {'norm_pos': position, 'timestamp': t, 'id': 1}
    return datum0, datum1

def calibrate(requester, points, times_per_point):
    hmd_video_frame_size = (1000, 1000)
    outlier_threshold = 35

    start_calibration(requester, hmd_video_frame_size, outlier_threshold)

    # Mockup logic for sample movement:
    # We sample some reference positions (in normalized screen coords).
    # Positions can be freely defined

    ref_data = []
    for pos in calibration_points:
        print('subject now looks at position:', pos)
        input()
        for s in range(calibration_times_per_point):
            eye0, eye1 = get_calibration_data(requester, pos)
            ref_data.append(eye0)
            ref_data.append(eye1)
            time.sleep(1 / 60.)  # simulate animation speed.
    end_calibration(requester, ref_data)



if __name__ == "__main__":
    main()




