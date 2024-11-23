import pymem
import pymem.process
import time
from flask import Flask, jsonify
from threading import Thread
import logging

def main():

    # Game-specific details
    GAME_NAME = "Ultimate_Racing_2D_2.exe"
    POINTER_OFFSET = 0x021ACA98

    # Attach to the game process
    try:
        pm = pymem.Pymem(GAME_NAME)
        print(f"Attached to {GAME_NAME}!")

        base_address = pymem.process.module_from_name(pm.process_handle, GAME_NAME).lpBaseOfDll
        pointer = base_address + POINTER_OFFSET

        print(hex(pointer))  # Print the pointer address

        # read the pointer that poitner points
        pointer = pm.read_bytes(pointer, 8)
        pointer = int.from_bytes(pointer, byteorder='little')
        print(hex(pointer))

        offsets = [0x8, 0x68, 0x10, 0x48, 0x10, 0xEA0]

        # read the pointer that pointer points
        for offset in offsets:
            pointer = pm.read_bytes(pointer + offset, 8)
            pointer = int.from_bytes(pointer, byteorder='little')

        # read the value that the final pointer points
        PERCENTAGE_POINTER = pointer

        # try to read the value that the pointer points
        print(pm.read_double(PERCENTAGE_POINTER))
    except Exception as e:
        print(f"Failed to attach to {GAME_NAME}: {e}")
        exit()


    # Start a Flask server for communication
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    app = Flask(__name__)
    lap_data = {
        "current_lap": 0,
        "current_lap_time": 0,
        "last_lap_time": 0,
        "sector_times": [],
        "best_sector_times": [],
        "best_lap_time": float("inf"),
    }

    @app.route("/get_data", methods=["GET"])
    def get_data():
        return jsonify(lap_data)

    def start_server():
        app.run(port=5000, debug=False, use_reloader=False)

    # Start the server in a separate thread
    server_thread = Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()

    terminal_colors = {
        "YELLOW": "\033[93m",
        "GREEN": "\033[92m",
        "PURPLE": "\033[95m",
        "END": "\033[0m",
    }



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
    best_lap_time = float("inf")

    def manage_sectors(sector_index, sector_time):
        if sector_time < best_sector_times[sector_index]:
            best_sector_times[sector_index] = sector_time
            color = terminal_colors["GREEN"]
        else:
            color = terminal_colors["YELLOW"]

        print(f"  {color}Sector {sector_index + 1}: {sector_time:.2f} s{terminal_colors['END']}")
        lap_data["sector_times"] = laps_times_and_sectors.get(lap_number, [])

    def manage_lap(lap_time, best_lap_time):

        if lap_time < best_lap_time:
            best_lap_time = lap_time
            color = terminal_colors["GREEN"]
        else:
            color = terminal_colors["YELLOW"]

        print(f"{color}Lap time: {lap_time:.2f} s{terminal_colors['END']}")
        return best_lap_time

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
                        sector_time -= sum(laps_times_and_sectors[lap_number])

                    laps_times_and_sectors[lap_number] = laps_times_and_sectors.get(lap_number, []) + [sector_time]

                    manage_sectors(sector_index, sector_time)
                    sector_index += 1

                    if sector_index >= len(track_divisions):
                        # Wait for the next lap to start
                        while int(pm.read_double(PERCENTAGE_POINTER)) == lap_number:
                            current_time = time.time()
                            lap_data["current_lap_time"] = current_time - start_time
                            time.sleep(0.001)
                        current_time = time.time()
                        sector_time = round(current_time - start_time, 2)

                        if lap_number in laps_times_and_sectors and laps_times_and_sectors[lap_number]:
                            # Subtract previous sector time to calculate the actual sector time
                            sector_time -= sum(laps_times_and_sectors[lap_number])

                        laps_times_and_sectors[lap_number] = laps_times_and_sectors.get(lap_number, []) + [sector_time]

                        manage_sectors(sector_index, sector_time)

                        lap_time = current_time - start_time
                        best_lap_time = manage_lap(lap_time, best_lap_time)

                        sector_index = 0
                        start_time = time.time()
                        lap_number += 1
                        lap_data["current_lap"] = lap_number
                        lap_data["last_lap_time"] = lap_time

            # Update `lap_data` in your timing script where necessary:
            current_time = time.time()
            lap_data["current_lap_time"] = current_time - start_time
            lap_data["best_sector_times"] = best_sector_times
            lap_data["best_lap_time"] = best_lap_time

            time.sleep(0.001)
        except Exception as e:
            print(f"Error reading memory: {e}")
            break