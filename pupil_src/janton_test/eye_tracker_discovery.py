import zmq
import time
# we need a serializer
import msgpack as serializer
import numpy as np
import clean_test as test
import matplotlib.pyplot as plt

colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w', '0.75']

import sys

sys.path.append(
    "/Users/JorgeMain/Box Sync/Jorge Work/Post-Tufts/2017/Tarseer/Tech/Software/tarseer/headset_prototype_v0.5/TarseerVFT/app")

from src.debugging_tools.dev_code_template import DevCode

test_with_display = 0
num_test_points = 9
nomr_physical_location_list = [(0, 0),       (3.5 / 7.5, 0),       (7.5 / 7.5, 0),
                               (0, 4.5 / 9), (3.5 / 7.5, 4.5 / 9), (7.5 / 7.5, 4.5 / 9),
                               (0, 9 / 9),   (3.5 / 7.5, 9 / 9),   (7.5 / 7.5, 9 / 9)]
def main():
    if test_with_display:
        display = DevCode.setup_display()
    else:
        display = 1

    calib_per_point = 30  # half a second of data

    ctx = zmq.Context()
    requester, subscriber = test.setup_subscriber_requester(ctx)
    subscriber.subscribe_to_topics(test.topic_list)
    print("topics subscribed to")

    requester.eye_process_start()
    print("eye process started")
    time.sleep(2)
    calibrate(requester, display, nomr_physical_location_list, calib_per_point)
    #requester.set_3d_detection_mapping_mode()
    #real_time_graph(subscriber)
    requester.eye_process_end()

    return
    # requester.unsure_start_recording("test_recording")
    # requester.set_3d_detection_mapping_mode()
    time.sleep(10)
    requester.start_plugins(test.non_calibration_plugins)
    print("plugins ready")    # requester.unsure_stop_recording()
    test_accuracy(subscriber)
    requester.eye_process_end()

    print("done")
    pass


def calibrate(requester, display, physical_location_list, times_per_point):
    test.start_calibration(requester, hmd_video_frame_size=(
        1000*7.5/9, 1000), outlier_threshold=35)

    ref_data = []
    for location in physical_location_list:
        print('subject now looks at position:', location)
        if test_with_display:
            display.set(location, intensity=200, time_on=0)

        x = input()  # wait for click

        for s in range(times_per_point):
            eye0, eye1 = test.get_calibration_data(requester, location)
            ref_data.append(eye0)
            ref_data.append(eye1)
            time.sleep(1 / 60.)  # simulate animation speed.
        if test_with_display:
            display.set(location, 0, time_on=0)

    test.end_calibration(requester, ref_data)

    # Mockup logic for sample movement:
    # We sample some reference positions (in normalized screen coords).
    # Positions can be freely defined


def real_time_graph(subscriber):
    curr_pos_0 = [0, 0]
    curr_pos_1 = [0, 0]

    for i in range(1000):
        topic, message = subscriber.read_message()
       # if topic == b'pupil.1':
        if topic == b'gaze':
            print("gaze")
            if message[b'topic'] == b'gaze.2d.1.':
                print(message)
                if message[b'confidence'] > 0.7:
                    curr_pos_1 = message[b'norm_pos']
            #if topic == b'pupil.0':
            if message[b'topic'] == b'gaze.2d.0.':
                print("2")
                if message[b'confidence'] > 0.7:
                    curr_pos_0 = message[b'norm_pos']
        #plt.scatter(curr_pos_0[0], curr_pos_0[1])
        print(curr_pos_1)
        plt.scatter(curr_pos_1[0], curr_pos_1[1])
        plt.pause(0.05)
    plt.show()

def test_accuracy(subscriber):
    import pdb
    pupil1_list = []
    pupil0_list = []
    min_confidence_threshold = 0.7

    for j in range(num_test_points):
        print("Num_test position: ")
        x = input()
        pupil0_list.append([])
        pupil1_list.append([])
        for i in range(10):
            topic, message = subscriber.read_message()
            if message[b'topic'] == b'gaze.2d.1':
            #if topic == b'pupil.1':
                if message[b'confidence'] > 0.7:
                    norm = np.array(message[b'norm_pos']).reshape(2, 1)
                    pupil1_list[j] = np.hstack([pupil1_list[j], norm]) if len(pupil1_list[j]) else norm
            if message[b'topic'] == b'gaze.2d.0':
            #if topic == b'pupil.0':
                if message[b'confidence'] > 0.7:
                    norm = np.array(message[b'norm_pos']).reshape(2, 1)
                    pupil0_list[j] = np.hstack([pupil0_list[j], norm]) if len(pupil0_list[j]) else norm

    for i in range(len(pupil1_list)):
        try:
            plt.subplot(1,2,1)
            plt.scatter(pupil0_list[i][0], pupil0_list[i][1], c=colors[i], label=physical_location_list[i])
        except IndexError:
            pass
        try:
            plt.subplot(1,2,2)
            plt.scatter(pupil1_list[i][0], pupil1_list[i][1], c=colors[i], label=physical_location_list[i])
        except IndexError:
            pass

    plt.show()
    pdb.set_trace()
    # show point
    # click
    # store next 1s of data


def map_to_3d_dome():
    pass
    # given pupil data make sure we can map it to our 3D dome


def distance_to_light():
    pass
    # given some way to map to our 3d dome, find radial distance to point


def test_blink():
    pass
    # subscribe only to blinking and loop to store results
    # whenever q pressed end
    # USER: look straight and performing blinking process


def map_one_by_one_cleanly(eye_t_list):
    for output in eye_t_list:
        print(outputs)
        for value in eye_t_list[output]:
            print(value, ':', eye_t_list[output][value])


if __name__ == "__main__":
    main()
