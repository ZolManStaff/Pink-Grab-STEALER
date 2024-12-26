from pynput.mouse import Controller
import time
import threading

def block_mouse(duration):
    mouse_controller = Controller()
    initial_position = mouse_controller.position

    def lock_cursor():
        while blocking:
            mouse_controller.position = initial_position
            time.sleep(0.01)

    global blocking
    blocking = True
    thread = threading.Thread(target=lock_cursor)
    thread.start()
    time.sleep(duration)
    blocking = False
    thread.join()

block_mouse(10)