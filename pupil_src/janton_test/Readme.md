*Command to run*:

python eye_tracker_discovery.py while service app is running. No need
to open up the eye windows in the service.

*Procedure*:

The computer will open up the eye windows from pupil service. Wait until
the eye tracker starts to reliably detect the eye.

You must hear "Starting Calibration". On the terminal you can see where
to look. 9 points are required for calibration. (0,0) is the bottom left
and (1,1) is top right. x is horizontal and y is vertical.

Whenever you are stably looking at a point click enter in the terminal
and it will record the gaze readings for that point. Once you do this
for all points, it will say "Starting calibration"

You then have 2 seconds to relax before it starts recording and graphing
in real-time your gaze. It will display points in dark blue color when
done graphing.

Whenever you are done, close the graph and pupil will close safely.

*Comments on the code*
Subscriber has two sockets. The first uses the recv_multipart and the
second is built ontop of pupil's recv. The second is currently not in
use and commented out.

Subscriber ignores all, but the last message it pulls from the buffer.
This can by returning an array. The number of messages in the buffer
are printed out to see how many packages it is dropping.



