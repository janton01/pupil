import zmq
import time
# we need a serializer
import msgpack as serializer

import clean_test as test

import sys

sys.path.append(
    "/Users/JorgeMain/Box Sync/Jorge Work/Post-Tufts/2017/Tarseer/Tech/Software/tarseer/headset_prototype_v0.5/TarseerVFT/app")

from src.debugging_tools.dev_code_template import DevCode

test_with_display = 0


def main():
    if test_with_display:
        display = DevCode.setup_display()
    else:
        display = 1
    physical_location_list = [(0, -3), (0, -15), (0, 9)]
    calib_per_point = 60  # one second of data

    ctx = zmq.Context()
    requester, subscriber = test.setup_subscriber_requester(ctx)
    subscriber.subscribe_to_topics(test.topic_list)
    print("topics subscribed to")

    requester.eye_process_start()
    print("eye process started")
    time.sleep(2)
    calibrate(requester, display, physical_location_list, calib_per_point)

    # requester.unsure_start_recording("test_recording")
    # requester.set_3d_detection_mapping_mode()
    time.sleep(10)
    requester.start_plugins(test.non_calibration_plugins)
    print("plugins ready")    # requester.unsure_stop_recording()
    time.sleep(10)
    requester.eye_process_end()

    print("done")
    pass


def calibrate(requester, display, physical_location_list, times_per_point):
    test.start_calibration(requester, hmd_video_frame_size=(
        1000, 1000), outlier_threshold=35)

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


def test_accuracy():
    pass
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
