import threading
import main_terminal
import main

def run_terminal():
    main_terminal.run_terminal()

def run_main_voice():
    main.run_main_voice(False)

if __name__ == "__main__":
    # Create threads
    t1 = threading.Thread(target=run_terminal)
    t2 = threading.Thread(target=run_main_voice)

    # Start both
    t1.start()
    t2.start()

    # Optionally wait for both to finish
    t1.join()
    t2.join()
