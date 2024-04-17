import multiprocessing
import time
import threading

from object_detection.src.application import script as ObjectDetection

updated_location = threading.Condition()
image_set = []


def main(self):
    # add more later
    while True:
        #build image set somehow...
        time.sleep(5)
        if image_set:
            with updated_location:
                updated_location.notify_all()


def create_pipe(target_class):
    main_conn, sub_conn = multiprocessing.Pipe()
    process = multiprocessing.Process(target=target_class, args=(sub_conn,))
    return process, main_conn


def await_image(object_detection_process, object_detection_conn):
    while True:
        with updated_location:
            updated_location.wait()

        # send image to object detection
        object_detection_conn.send(image_set)

        time.sleep(5)

        # get direction from object detection
        direction = object_detection_conn.recv()


def move(direction):
    # do stuff
    pass


if __name__ == '__main__':
    # Create processes and pipes
    object_detection_process, object_detection_conn = create_pipe(ObjectDetection)

    # for whenever flight termination is ready
    # flight_termination_process, flight_termination_conn = create_pipe(FlightTermination)

    # Start processes
    object_detection_process.start()

    # flight_termination_process.start()

    threading.Thread(target=await_image, args=(object_detection_process, object_detection_conn)).start()
    # threading.Thread(target=await_termination, args=(flight_termination_process, flight_termination_conn)).start()

    main()