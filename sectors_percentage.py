import pymem
import time

terminal_colors = {
    "YELLOW": "\033[93m",
    "GREEN": "\033[92m",
    "PURPLE": "\033[95m",
    "END": "\033[0m",
}

# Game-specific details
GAME_NAME = "Ultimate_Racing_2D_2.exe"
PERCENTAGE_POINTER = 0x198DCFFF680  # Replace with your X pointer address

# Attach to the game process
try:
    pm = pymem.Pymem(GAME_NAME)
    print(f"Attached to {GAME_NAME}!")
except Exception as e:
    print(f"Failed to attach to {GAME_NAME}: {e}")
    exit()


track_divisions = [0.33, 0.66]
lap_number = int(pm.read_double(PERCENTAGE_POINTER))
sector_index = 0

# Wait for the current lap to finish
initial_lap = int(pm.read_double(PERCENTAGE_POINTER))
while int(pm.read_double(PERCENTAGE_POINTER)) == initial_lap:
    time.sleep(0.001)

lap_number += 1
print(f"Starting lap {lap_number}")

start_time = time.time()

laps_times_and_sectors = {}
best_sector_times = [float("inf")] * (len(track_divisions) + 1)
best_lam_time = float("inf")

def manage_sectors(sector_index, sector_time):
    if sector_time < best_sector_times[sector_index]:
        best_sector_times[sector_index] = sector_time
        color = terminal_colors["GREEN"]
    else:
        color = terminal_colors["YELLOW"]

    print(f"{color}Sector {sector_index + 1}: {sector_time:.2f} s{terminal_colors['END']}")

while True:
    try:
        full_percentage = pm.read_double(PERCENTAGE_POINTER)

        if int(full_percentage) == lap_number:
            # percentage is lap + 0.lap_percentage
            # take only the decimal part
            percentage = full_percentage - int(full_percentage)

            if percentage >= track_divisions[sector_index]:
                current_time = time.time()
                sector_time = round(current_time - start_time, 2)

                if lap_number in laps_times_and_sectors and laps_times_and_sectors[lap_number]:
                    # Subtract previous sector time to calculate the actual sector time
                    sector_time -= laps_times_and_sectors[lap_number][-1]

                laps_times_and_sectors[lap_number] = laps_times_and_sectors.get(lap_number, []) + [sector_time]

                manage_sectors(sector_index, sector_time)
                sector_index += 1

                if sector_index >= len(track_divisions):
                    # Wait for the next lap to start
                    while int(pm.read_double(PERCENTAGE_POINTER)) == lap_number:
                        time.sleep(0.001)
                    current_time = time.time()
                    sector_time = round(current_time - start_time, 2)

                    if lap_number in laps_times_and_sectors and laps_times_and_sectors[lap_number]:
                        # Subtract previous sector time to calculate the actual sector time
                        sector_time -= laps_times_and_sectors[lap_number][-1]

                    laps_times_and_sectors[lap_number] = laps_times_and_sectors.get(lap_number, []) + [sector_time]

                    manage_sectors(sector_index, sector_time)

                    lap_time = current_time - start_time
                    print(f"Lap time: {lap_time:.2f} s")

                    sector_index = 0
                    start_time = time.time()
                    lap_number += 1

        time.sleep(0.001)
    except Exception as e:
        print(f"Error reading memory: {e}")
        break