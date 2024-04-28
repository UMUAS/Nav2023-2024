import unittest

from pymavlink import mavutil
from src.flight_termination.flight_termination import AutopilotConnectionWrapper


class TestAutopilotHeartbeatMessage(unittest.TestCase):
    @classmethod
    def create_fake_autopilot_client(self):
        """A fake autopilot for receiving messages."""
        master = mavutil.mavlink_connection("udpin:0.0.0.0:14550")
        return master

    @classmethod
    def create_fake_autopilot_server(self):
        """A fake autopilot for sending messages."""
        master = mavutil.mavlink_connection("udpout:0.0.0.0:14551")
        return master

    def test_sending_heartbeat_msg(self):
        master = self.create_fake_autopilot_client()
        autopilot_conn = AutopilotConnectionWrapper("udpout:0.0.0.0:14550")

        # Send a heartbeat message to the fake autopilot.
        autopilot_conn.send_heartbeat_msg()
        msg_received = master.recv_match(timeout=1).to_dict()
        self.assertIn("mavpackettype", msg_received)
        self.assertEqual(msg_received["mavpackettype"], "HEARTBEAT")

        # Close connections.
        autopilot_conn.conn.close()
        master.close()

    def test_receive_heartbeat_msg(self):
        master = self.create_fake_autopilot_server()
        autopilot_conn = AutopilotConnectionWrapper("udpin:0.0.0.0:14551")

        # Receive a heartbeat message from the fake autopilot.
        master.mav.heartbeat_send(
            mavutil.mavlink.MAV_TYPE_HEXAROTOR,
            mavutil.mavlink.MAV_AUTOPILOT_INVALID,
            0,
            0,
            0,
        )
        msg_received = autopilot_conn.conn.recv_match(timeout=1).to_dict()
        self.assertIn("mavpackettype", msg_received)
        self.assertIn("type", msg_received)
        self.assertEqual(msg_received["mavpackettype"], "HEARTBEAT")
        self.assertEqual(msg_received["type"], 13)

        # Close connections.
        autopilot_conn.conn.close()
        master.close()


# class TestGCSHeartbeatMessage(unittest.TestCase):
#     @classmethod
#     def create_fake_gcs_client(self):
#         """A fake GCS system for receiving messages."""
#         master = mavutil.mavlink_connection("udpin:0.0.0.0:14552")
#         return master

#     @classmethod
#     def create_fake_gcs_server(self):
#         """A fake GCS system for sending messages."""
#         master = mavutil.mavlink_connection("udpout:0.0.0.0:14553")
#         return master

#     def test_sending_heartbeat_msg(self):
#         master = self.create_fake_gcs_client()
#         gcs_conn = GCSConnection("udpout:0.0.0.0:14552")

#         # Send a heartbeat message to the fake GCS.
#         gcs_conn.send_heartbeat_msg()
#         msg_received = master.recv_match(timeout=1).to_dict()
#         self.assertIn("mavpackettype", msg_received)
#         self.assertEqual(msg_received["mavpackettype"], "HEARTBEAT")

#         # Close connections.
#         gcs_conn.conn.close()
#         master.close()

#     def test_receive_heartbeat_msg(self):
#         master = self.create_fake_gcs_server()
#         gcs_conn = GCSConnection("udpin:0.0.0.0:14553")

#         # Receive a heartbeat message from the fake GCS.
#         master.mav.heartbeat_send(
#             mavutil.mavlink.MAV_TYPE_HEXAROTOR,
#             mavutil.mavlink.MAV_AUTOPILOT_INVALID,
#             0,
#             0,
#             0,
#         )
#         msg_received = gcs_conn.conn.recv_match(timeout=1).to_dict()
#         self.assertIn("mavpackettype", msg_received)
#         self.assertIn("type", msg_received)
#         self.assertEqual(msg_received["mavpackettype"], "HEARTBEAT")
#         self.assertEqual(msg_received["type"], 13)

#         # Close connections.
#         gcs_conn.conn.close()
#         master.close()
