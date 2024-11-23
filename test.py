import pymem
import pymem.process

game_name = "Ultimate_Racing_2D_2.exe"
pointer_offset = 0x021ACA98  # Hex pointer_offset

pm = pymem.Pymem(game_name)
base_address = pymem.process.module_from_name(pm.process_handle, game_name).lpBaseOfDll
pointer = base_address + pointer_offset

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
    print(hex(pointer))

# read the value that the final pointer points
value = pm.read_double(pointer)
print(value)
