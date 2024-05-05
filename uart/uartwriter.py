import serial


class UartWriter:
    def __init__(self, path) -> None:
        self.path = path

    def encoder(self, command: bytes) -> bytes:
        preamble = b'AAAB'
        return preamble + command

    def write(self, cmd):
        print(self.encoder(cmd))
        ser = serial.Serial(self.path, 115200)
        ser.write(self.encoder(cmd))
        ser.close()
