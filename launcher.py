import overlay
import threading
import signal
import sys

def start_sectors_thread():
    import main as sectors

def signal_handler(sig, frame):
    print('Exiting gracefully...')
    sys.exit(0)

# Register the signal handler for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

# Thread to start the sectors
sectors_thread = threading.Thread(target=start_sectors_thread, daemon=True)
sectors_thread.start()

# Start the overlay in a separate thread
overlay.main()
