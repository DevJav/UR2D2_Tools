import pymem
import time

# Game-specific details
GAME_NAME = "Ultimate_Racing_2D_2.exe"
X_POINTER = 0x20DDE5A32BC  # Replace with your X pointer address
Y_POINTER = 0x20DDE5A32C0 # Replace with your Y pointer address

# Attach to the game process
try:
    pm = pymem.Pymem(GAME_NAME)
    print(f"Attached to {GAME_NAME}!")
except Exception as e:
    print(f"Failed to attach to {GAME_NAME}: {e}")
    exit()


# Define checkpoints as line segments (x1, y1, x2, y2)
checkpoints = [
    (206.37, 173.1, 206.37, 159.56),  # Example checkpoint 1
    (206.37, 24, 206.37, 50),  # Example checkpoint 2
    # Add more checkpoints as needed
]

# Function to check if a point (px, py) crosses a line segment (x1, y1, x2, y2)
def crosses_line(px, py, x1, y1, x2, y2):
    # Check if the point (px, py) is on the line segment (x1, y1) to (x2, y2)
    tolerance = 0.5  # Increase tolerance for crossing detection
    if min(x1, x2) - tolerance <= px <= max(x1, x2) + tolerance and min(y1, y2) - tolerance <= py <= max(y1, y2) + tolerance:
        # Calculate the slope of the line segment
        if x1 != x2:
            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - slope * x1
            return abs(py - (slope * px + intercept)) < tolerance
        else:
            return abs(px - x1) < tolerance
    return False

# Initialize checkpoint index and start time
checkpoint_index = 0
start_time = None

while True:
    try:
        # Read X and Y positions from memory
        car_x = pm.read_float(X_POINTER)
        car_y = pm.read_float(Y_POINTER)

        # print(f"X: {car_x} Y: {car_y}")

        # Check if the car crosses the current checkpoint
        if checkpoint_index < len(checkpoints):
            x1, y1, x2, y2 = checkpoints[checkpoint_index]
            # print(f"Checkpoint {checkpoint_index + 1}: ({x1}, {y1}) to ({x2}, {y2})")
            if crosses_line(car_x, car_y, x1, y1, x2, y2):
                if checkpoint_index == 0:
                    elapsed_time = time.time() - start_time if start_time else 0
                    start_time = time.time()
                    print(f"Lap time: {elapsed_time:.3f} seconds")
                    print(f"New lap!")
                else:
                    elapsed_time = time.time() - start_time
                    print(f"Checkpoint {checkpoint_index + 1} crossed. Time elapsed: {elapsed_time:.3f} seconds")
                checkpoint_index += 1
                if checkpoint_index == len(checkpoints):
                    checkpoint_index = 0
                    

        time.sleep(0.0001)
    except Exception as e:
        print(f"Error reading memory: {e}")
        break