from message_object import ScheduleMessage
import queue
import threading

class Scheduler:
    # Queue of ScheduleMessage objects
    waiting_messages = queue.Queue()
    new_messages = threading.Condition()

    def __init__(self):
        pass

    def scheduler(self):
        while True:
            message_schedule = None
            with self.new_messages:
                self.new_messages.wait()
                if not self.waiting_messages.empty():
                    message = self.waiting_messages.get()
                    # TODO make message a tuple
                    print(f"Received message: {message}")
                    if "MISSION_PLAN" in message:
                        # TODO Make priority an enum
                        message_schedule = ScheduleMessage("START_MISSION", message, 1)
                    elif "OBJECT_DETECTION" in message:
                        pass
                    elif message == "MOVE":
                        move()
                new_messages.notify_all()
            time.sleep(1)