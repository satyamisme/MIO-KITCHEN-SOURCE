
from ctypes import LittleEndianStructure, sizeof, memmove, byref, string_at, addressof, c_ushort
magic = b'\x8bMPK'
###############
# Mpk Design
# ----------
# magic : 4bytes
# signature: 512 bytes
# info_len : 4bytes
# info_data: info_len bytes
# icon_len: 4bytes
# icon_data: icon_len
# mpk_data_len: 4bytes
# mpk_data: mpk_data_len
# ----------
##############
class BasicStruct(LittleEndianStructure):
    @property
    def _size(self):
        return sizeof(type(self))

    def __len__(self):
        return self._size

    def unpack(self, data: bytes):
        if len(data) < self._size:
            raise Exception("Input data size less than struct size.")
        if not isinstance(data, (bytes, bytearray)):
            raise Exception("Input data must be byte data or bytearray.")

        return memmove(byref(self), data, self._size)

    def pack(self):
        return string_at(addressof(self), sizeof(self))

class MpkHeader(BasicStruct):
    _packed_ = 1
    _fields_ = [
        ("magic", c_ushort * 4),
    ]
