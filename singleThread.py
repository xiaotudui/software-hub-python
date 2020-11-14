import threading
import time

def test():

    for i in range(5):
        print(threading.current_thread().name+' test ',i)
        time.sleep(1)


thread = threading.Thread(target=test)
thread.setDaemon(True)
thread.start()
print(thread.is_alive())
for i in range(5):
    print(threading.current_thread().name+' main ', i)
    time.sleep(1)

time.sleep(2)
print(thread.is_alive())