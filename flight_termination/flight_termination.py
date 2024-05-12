import logging

logger = logging.getLogger()


def begin_flight_termination(autopilot_conn_wrapper):
    # TODO: See CONOPS for more flight termintaion instructions.
    pre_flight_termination()


def pre_flight_termination():
    pass


def terminate_flight(autopilot_conn_wrapper):
    autopilot_conn_wrapper.conn.mav.command_long_send(
        autopilot_conn_wrapper.conn.target_system,
        autopilot_conn_wrapper.conn.target_component,
        autopilot_conn_wrapper.mavlink.MAV_CMD_DO_FLIGHTTERMINATION,
        0,
        1,
        0,
        0,
        0,
        0,
        0,
        0,
    )
    msg = autopilot_conn_wrapper.conn.recv_match(type=["COMMAND_ACK"], blocking=True)
    logger.info(msg)


def post_flight_termination():
    pass
