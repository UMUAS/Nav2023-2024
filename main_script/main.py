# main script for UMUAS autonomous drone system.
from dronekit import *


#initialize variables
vehicle = None


#Function that initializes the connection with our drone
def initialize_connection_with_vehicle(serial_port,baud_rate):
    vehicle = connect(serial_port,wait_ready = True, baud=baud_rate)


#Function that gets the drone's attributes
def get_vehicle_attributes():
    #If we have a connection with our vehicle, get the attributes.
    if(Vehicle != None):
        #Instead of print, we may have to use another function that sends messages to the GCS and displays it there.
        print("Autopilot Firmware version: %s" % vehicle.version)
        print("Autopilot capabilities (supports ftp): %s" % vehicle.capabilities.ftp)
        print("Global Location: %s" % vehicle.location.global_frame)
        print("Global Location (relative altitude): %s" % vehicle.location.global_relative_frame)
        print("Local Location: %s" % vehicle.location.local_frame)    #NED
        print("Attitude: %s" % vehicle.attitude)
        print("Velocity: %s" % vehicle.velocity)
        print("GPS: %s" % vehicle.gps_0)
        print("Groundspeed: %s" % vehicle.groundspeed)
        print("Airspeed: %s" % vehicle.airspeed)
        print("Gimbal status: %s" % vehicle.gimbal)
        print("Battery: %s" % vehicle.battery)
        print("EKF OK?: %s" % vehicle.ekf_ok)
        print("Last Heartbeat: %s" % vehicle.last_heartbeat)
        print("Rangefinder: %s" % vehicle.rangefinder)
        print("Rangefinder distance: %s" % vehicle.rangefinder.distance)
        print("Rangefinder voltage: %s" % vehicle.rangefinder.voltage)
        print("Heading: %s" % vehicle.heading)
        print("Is Armable?: %s" % vehicle.is_armable)
        print("System status: %s" % vehicle.system_status.state)
        print("Mode: %s" % vehicle.mode.name)    # settable
        print("Armed: %s" % vehicle.armed)    # settable

    #otherwise, send negative response
    else:
        print("Vehicle connection has not been established.")
