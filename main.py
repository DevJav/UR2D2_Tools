import time
from memory_reader import MemoryReader
from lap_manager import LapManager
from server import start_server

# Constants
GAME_NAME = "Ultimate_Racing_2D_2.exe"
POINTER_OFFSET = 0x021AEAB8
OFFSETS = [0x8, 0x68, 0x10, 0x48, 0x10, 0xEC0, 0x0]
TRACK_DIVISIONS = [0.33, 0.66]
TERMINAL_COLORS = {"YELLOW": "\033[93m", "GREEN": "\033[92m", "PURPLE": "\033[95m", "END": "\033[0m"}

# Initialize components
memory_reader = MemoryReader(GAME_NAME, POINTER_OFFSET)
lap_manager = LapManager(TRACK_DIVISIONS, TERMINAL_COLORS)

# Attach to game and resolve memory pointers
memory_reader.attach()
memory_reader.resolve_pointer(OFFSETS)
print("Successfully attached to game and resolved memory pointers.")

# Start Flask server
start_server(lap_manager.lap_data)

# Wait for current lap to finish
lap_manager.lap_number = int(memory_reader.read_double())
print(f"Waiting for lap {lap_manager.lap_number + 1} to start...")
while int(memory_reader.read_double()) == lap_manager.lap_number:
    time.sleep(0.001)

print("Lap started!")

lap_manager.lap_number += 1

# Main loop
lap_manager.start_time = time.time()

while True:
    try:
        full_percentage = memory_reader.read_double()

        # Check if still in the same lap
        if int(full_percentage) == lap_manager.lap_number:
            percentage = full_percentage - int(full_percentage)
            if lap_manager.sector_index < len(TRACK_DIVISIONS):
                # Check if it's time to process the next sector
                if percentage >= TRACK_DIVISIONS[lap_manager.sector_index]:
                    current_time = time.time()
                    sector_time = lap_manager.calculate_sector_time(current_time)

                    lap_manager.store_sector_time(sector_time)
                    lap_manager.manage_sectors(lap_manager.sector_index, sector_time)

                    lap_manager.sector_index += 1

        # Check if lap is finished
        elif int(full_percentage) == lap_manager.lap_number + 1:
            current_time = time.time()
            sector_time = lap_manager.calculate_sector_time(current_time)
            lap_manager.store_sector_time(sector_time)

            lap_manager.manage_sectors(lap_manager.sector_index, sector_time)

            lap_time = current_time - lap_manager.start_time
            lap_manager.manage_lap(lap_time)

            lap_manager.reset_for_new_lap()

        # Continuously update lap data
        lap_manager.update_lap_data(time.time())
        time.sleep(0.001)

    except Exception as e:
        print(f"Error: {e}")
        break

