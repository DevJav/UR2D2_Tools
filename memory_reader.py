import pymem
import pymem.process

class MemoryReader:
    def __init__(self, game_name, pointer_offset):
        self.game_name = game_name
        self.pointer_offset = pointer_offset
        self.pm = None
        self.base_address = None
        self.pointer = None

    def attach(self):
        try:
            self.pm = pymem.Pymem(self.game_name)
            self.base_address = pymem.process.module_from_name(self.pm.process_handle, self.game_name).lpBaseOfDll
            print(f"Attached to {self.game_name}!")
        except Exception as e:
            raise RuntimeError(f"Failed to attach to {self.game_name}: {e}")

    def resolve_pointer(self, offsets):
        try:
            pointer = self.base_address + self.pointer_offset
            pointer = int.from_bytes(self.pm.read_bytes(pointer, 8), byteorder='little')

            for offset in offsets[:-1]:
                # print(f"Resolving pointer at {hex(pointer)}")
                pointer = int.from_bytes(self.pm.read_bytes(pointer + offset, 8), byteorder='little')

            pointer += offsets[-1]

            self.pointer = pointer
            # print(f"Pointer resolved at {hex(self.pointer)}")
            return pointer
        except Exception as e:
            raise RuntimeError(f"Failed to resolve pointer: {e}")

    def read_double(self):
        if self.pointer is None:
            raise RuntimeError("Pointer not resolved")
        return self.pm.read_double(self.pointer)
    
    def read_float(self):
        if self.pointer is None:
            raise RuntimeError("Pointer not resolved")
        return self.pm.read_float(self.pointer)

    def read_4bytes(self, address):
        return self.pm.read_int(address)