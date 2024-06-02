"""Helper classes to build the commands for the UART communication protocol."""
from .command import BuzzerState, Command, DataUnion, Message, MoveLift, PlaceCubes, RotateGrid


class CommandBuilder:
    """Assembles the command for the UART communication protocol."""
    _id = 0

    @classmethod
    def _generate_id(cls):
        """Increments the id for each new command."""
        cls._id = (cls._id + 1) % 256
        return cls._id

    @classmethod
    def rotate_grid(cls, degrees: int) -> Message:
        """Builds the command to rotate the grid by the specified degrees."""
        deg = degrees % 360
        if deg > 180:
            deg -= 360

        rotate = RotateGrid()
        rotate.degrees = deg

        data = DataUnion()
        data.rotate_grid = rotate

        cmd = Message()
        cmd.cmd = Command.ROTATE_GRID.value
        cmd.id = cls._generate_id()
        cmd.data = data
        cmd.checksum = cls.calculate_checksum(cmd)
        return cmd

    @classmethod
    def place_cubes(cls, red: int, yellow: int, blue: int) -> Message:
        """Builds the command to place the specified cubes."""
        place = PlaceCubes()
        place.cubes_red = red
        place.cubes_yellow = yellow
        place.cubes_blue = blue

        data = DataUnion()
        data.place_cubes = place

        cmd = Message()
        cmd.cmd = Command.PLACE_CUBES.value
        cmd.id = cls._generate_id()
        cmd.data = data
        cmd.checksum = cls.calculate_checksum(cmd)
        return cmd

    @classmethod
    def move_lift(cls, state: MoveLift) -> Message:
        """Builds the command to move the lift."""
        data = DataUnion()
        data.move_lift = state.value

        cmd = Message()
        cmd.cmd = Command.MOVE_LIFT.value
        cmd.id = cls._generate_id()
        cmd.data = data
        cmd.checksum = cls.calculate_checksum(cmd)
        return cmd

    @classmethod
    def enable_buzzer(cls, state: BuzzerState) -> Message:
        """Builds the command to enable or disable the buzzer."""
        data = DataUnion()
        data.enable_buzzer = state.value

        cmd = Message()
        cmd.cmd = Command.ENABLE_BUZZER.value
        cmd.id = cls._generate_id()
        cmd.data = data
        cmd.checksum = cls.calculate_checksum(cmd)
        return cmd

    @classmethod
    def other_command(cls, command: Command, data: DataUnion = DataUnion()) -> Message:
        """Builds other commands with optional data."""
        cmd = Message()
        cmd.cmd = command.value
        cmd.id = cls._generate_id()
        cmd.data = data
        cmd.checksum = cls.calculate_checksum(cmd)
        return cmd

    @staticmethod
    def calculate_checksum(message: Message) -> int:
        """Calculates the checksum of the message."""
        data = bytes(message)[:-1]
        crc = 123456  # initial value
        polynomial = 0b100101111  # x^8 + x^5 + x^3 + x^2 + x + 1
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ polynomial
                else:
                    crc <<= 1
        return crc & 0xFF
