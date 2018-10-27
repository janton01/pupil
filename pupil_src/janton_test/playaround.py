    # In order for the annotations to be correlated correctly with the rest of
    # the data it is required to change Pupil Capture's time base to this scripts
    # clock. We only set the time base once. Consider using Pupil Time Sync for
    # a more precise and long term time synchronization
    time_fn = time.time()  # Use the appropriate time function here

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

