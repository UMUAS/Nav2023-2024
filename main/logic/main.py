import cv2
import multiprocessing
import time
import threading
import sys
sys.path.append("../../object_detection/src/")

try:
    from application.script import ObjectDetection
except ImportError:
    print("Error importing ObjectDetection class")
    sys.exit(1)

updated_location = threading.Condition()
image_set = []

def main(video_path):
    cap = cv2.VideoCapture(video_path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        with updated_location:
            if len(image_set) < 10:  # Limit size of image_set to prevent memory issues
                image_set.append(frame)
            print(f"Adding frame to image_set...{len(image_set)}")
            updated_location.notify_all()
        time.sleep(0.1)  # Control the frame rate

    cap.release()

def start_object_detection(conn):
    object_detection = ObjectDetection(conn)
    object_detection.getDirection()


def create_pipe(target_class):
    main_conn, sub_conn = multiprocessing.Pipe()
    # process = multiprocessing.Process(target=target_class(sub_conn))
    # return process, main_conn
    return multiprocessing.Process(target=start_object_detection, args=(sub_conn,)), main_conn


def await_image(object_detection_process, object_detection_conn):
    while True:
        with updated_location:
            updated_location.wait()
            images_to_send = image_set.copy()
            image_set.clear()  # Clear the images after sending

        # Send image to object detection
        object_detection_conn.send(images_to_send)

        time.sleep(2)


def setup_video_writer(cap, output_filename='output.mp4'):
    # Get the width and height of video frames
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define the codec and create VideoWriter object
    # The following line uses the XVID codec and writes to an AVI file.
    # You can change the codec and file format depending on your needs and platform capabilities.
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_filename, fourcc, 20.0, (frame_width, frame_height), True)

    return out


def display_direction_on_video(video_path, conn, output_filename='output.mp4'):
    cap = cv2.VideoCapture(video_path)
    count = 0
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    out = setup_video_writer(cap, output_filename)

    direction = "None"
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Send frame to object detection process
        conn.send(frame)

        # Receive direction from object detection process
        if conn.poll():  # Check if direction is ready
            direction = conn.recv()

        # Add text overlay to the frame
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, f"Direction: {direction}", (50, 50), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

        # Write the frame into the file 'output.avi'
        out.write(frame)
        print(f"Writing frame...{count}")
        count += 1

    print("Finished processing video.")
    # Release everything when job is finished
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    conn.close()



def move(direction):
    # Implement movement logic based on 'direction'
    print(f"Direction: {direction}")

if __name__ == '__main__':
    video_path = 'DJI_0072.MP4'
    object_detection_process, object_detection_conn = create_pipe(ObjectDetection)

    # Start processes
    object_detection_process.start()

    threading.Thread(target=display_direction_on_video, args=(video_path, object_detection_conn)).start()

    main(video_path)
