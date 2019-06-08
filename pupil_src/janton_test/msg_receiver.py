import zmq
from zmq.utils.monitor import recv_monitor_message
import msgpack as serializer
import logging

class Msg_Receiver():
    """
    Recv messages on a sub port.
    Not threadsafe. Make a new one for each thread
    __init__ will block until connection is established.
    """
    def __init__(self, ctx, url, topics=(), block_until_connected=True, hwm=None):
        self.socket = zmq.Socket(ctx, zmq.SUB)
        assert type(topics) != str

        if hwm is not None:
            self.socket.set_hwm(hwm)

        if block_until_connected:
            # connect node and block until a connecetion has been made
            monitor = self.socket.get_monitor_socket()
            self.socket.connect(url)
            while True:
                status = recv_monitor_message(monitor)
                if status["event"] == zmq.EVENT_CONNECTED:
                    break
                elif status["event"] == zmq.EVENT_CONNECT_DELAYED:
                    pass
                else:
                    raise Exception("ZMQ connection failed")
            self.socket.disable_monitor()
        else:
            self.socket.connect(url)

        for t in topics:
            self.subscribe(t)

    def __del__(self):
        pass
        #self.socket.close()

    def subscribe(self, topic):
        self.socket.subscribe('gaze')

    def unsubscribe(self, topic):
        self.socket.unsubscribe(topic)

    def recv(self):
        """Recv a message with topic, payload.
        Topic is a utf-8 encoded string. Returned as unicode object.
        Payload is a msgpack serialized dict. Returned as a python dict.
        Any addional message frames will be added as a list
        in the payload dict with key: '__raw_data__' .
        """
        topic = self.recv_topic()
        remaining_frames = self.recv_remaining_frames()
        payload = self.deserialize_payload(*remaining_frames)
        return topic, payload

    def recv_topic(self):
        return self.socket.recv_string()

    def recv_remaining_frames(self):
        while self.socket.get(zmq.RCVMORE):
            yield self.socket.recv()

    def deserialize_payload(self, payload_serialized, *extra_frames):
        payload = serializer.loads(payload_serialized, encoding="utf-8")
        if extra_frames:
            payload["__raw_data__"] = extra_frames
        return payload

    @property
    def new_data(self):
        return self.socket.get(zmq.EVENTS) & zmq.POLLIN
