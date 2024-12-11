import time
from memory_reader import MemoryReader
import pygame
import sys
import math

GAME_NAME = "Ultimate_Racing_2D_2.exe"
POINTER_OFFSET = 0x021A8EA0
OFFSETS_TH = [0x8, 0x30, 0x3E0, 0xC90]
OFFSETS_BR = [0x8, 0x30, 0x3E0, 0xC60]
OFFSETS_RIGHT = [0x8, 0x30, 0x3E0, 0xCC0]
OFFSETS_LEFT = [0x8, 0x30, 0x3E0, 0xCF0]
POINTER_OFFSET_2 = 0x021ACA98
OFFSETS_SPEED = [0x8, 0x68, 0x10, 0x48, 0x10, 0x8D0, 0x0]

memory_reader_th = MemoryReader(GAME_NAME, POINTER_OFFSET)
memory_reader_th.attach()
memory_reader_th.resolve_pointer(OFFSETS_TH)

memory_reader_br = MemoryReader(GAME_NAME, POINTER_OFFSET)
memory_reader_br.attach()
memory_reader_br.resolve_pointer(OFFSETS_BR)

memory_reader_right = MemoryReader(GAME_NAME, POINTER_OFFSET)
memory_reader_right.attach()
memory_reader_right.resolve_pointer(OFFSETS_RIGHT)

memory_reader_left = MemoryReader(GAME_NAME, POINTER_OFFSET)
memory_reader_left.attach()
memory_reader_left.resolve_pointer(OFFSETS_LEFT)

memory_reader_speed = MemoryReader(GAME_NAME, POINTER_OFFSET_2)
memory_reader_speed.attach()
memory_reader_speed.resolve_pointer(OFFSETS_SPEED)

while True:
    th = memory_reader_th.read_double()
    br = memory_reader_br.read_double()
    right = memory_reader_right.read_double()
    left = memory_reader_left.read_double()
    speed = memory_reader_speed.read_double()
    # write into file new line
    with open("data.csv", "a") as f:
        f.write(f"{th},{br},{right},{left},{speed}\n")
    time.sleep(0.01)