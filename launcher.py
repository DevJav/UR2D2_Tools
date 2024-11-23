import sectors
import overlay
import threading

# Start the overlay in a separate thread
overlay_thread = threading.Thread(target=overlay.main)
overlay_thread.daemon = True
overlay_thread.start()

# Start the sectors in a separate thread
sectors_thread = threading.Thread(target=sectors.main)
sectors_thread.daemon = True
sectors_thread.start()

# Wait for the threads to finish
overlay_thread.join()

# Wait for the threads to finish
sectors_thread.join()
