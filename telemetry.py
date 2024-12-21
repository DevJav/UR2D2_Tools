import time
from memory_reader import MemoryReader

GAME_NAME = "Ultimate_Racing_2D_2.exe"
POINTER_OFFSET = 0x021A8EA0
OFFSETS_TH = [0x8, 0x30, 0x3E0, 0xC90]
OFFSETS_BR = [0x8, 0x30, 0x3E0, 0xC60]
OFFSETS_RIGHT = [0x8, 0x30, 0x3E0, 0xCC0]
OFFSETS_LEFT = [0x8, 0x30, 0x3E0, 0xCF0]
POINTER_OFFSET_2 = 0x021ACA98
OFFSETS_SPEED = [0x8, 0x68, 0x10, 0x48, 0x10, 0x8D0, 0x0]

class Telemetry:
    def __init__(self):
        launch_time_str = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        self.file_name = f"telemetry_data_{launch_time_str}.csv"
    
        self.memory_reader_th = MemoryReader(GAME_NAME, POINTER_OFFSET)
        self.memory_reader_th.attach()
        self.memory_reader_th.resolve_pointer(OFFSETS_TH)

        self.memory_reader_br = MemoryReader(GAME_NAME, POINTER_OFFSET)
        self.memory_reader_br.attach()
        self.memory_reader_br.resolve_pointer(OFFSETS_BR)

        self.memory_reader_right = MemoryReader(GAME_NAME, POINTER_OFFSET)
        self.memory_reader_right.attach()
        self.memory_reader_right.resolve_pointer(OFFSETS_RIGHT)

        self.memory_reader_left = MemoryReader(GAME_NAME, POINTER_OFFSET)
        self.memory_reader_left.attach()
        self.memory_reader_left.resolve_pointer(OFFSETS_LEFT)

        self.memory_reader_speed = MemoryReader(GAME_NAME, POINTER_OFFSET_2)
        self.memory_reader_speed.attach()
        self.memory_reader_speed.resolve_pointer(OFFSETS_SPEED)

    def get_telemetry(self):
        th = self.memory_reader_th.read_double()
        br = self.memory_reader_br.read_double()
        right = self.memory_reader_right.read_double()
        left = self.memory_reader_left.read_double()
        speed = self.memory_reader_speed.read_double()
        return th, br, right, left, speed
    
    def write_telemetry(self, lap):
        th, br, right, left, speed = self.get_telemetry()
        with open(self.file_name, "a") as f:
            f.write(f"{lap},{th},{br},{right},{left},{speed}\n")
