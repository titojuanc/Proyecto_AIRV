import threading
import main_terminal
import main
from calendario import calend

def run_terminal():
    main_terminal.run_terminal()

def run_main_voice():
    main.run_main_voice(False)

if __name__ == "__main__":
    t1=threading.Thread(target=run_terminal)
    t2=threading.Thread(target=run_main_voice)
    t3=threading.Thread(target=calend.run_alarm_checker)

    t2.start()
    t1.start()
    t3.start()

    t2.join()
    t1.join()
    t3.join()
