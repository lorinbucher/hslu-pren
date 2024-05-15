"""Helper classes to build the commands for the UART communication protocol."""
from .command import Command, DataUnion, Message, MoveLift, PlaceCubes, RotateGrid


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

        union = DataUnion()
        union.rotate_grid = rotate

        cmd = Message()
        cmd.cmd = Command.ROTATE_GRID.value
        cmd.id = cls._generate_id()
        cmd.data = union
        cmd.checksum = 12
        return cmd

    @classmethod
    def place_cubes(cls, red: int, yellow: int, blue: int) -> Message:
        """Builds the command to place the specified cubes."""
        place = PlaceCubes()
        place.cubes_red = red
        place.cubes_yellow = yellow
        place.cubes_blue = blue

        union = DataUnion()
        union.place_cubes = place

        cmd = Message()
        cmd.cmd = Command.PLACE_CUBES.value
        cmd.id = cls._generate_id()
        cmd.data = union
        cmd.checksum = 12
        return cmd

    @classmethod
    def move_lift(cls, state: MoveLift) -> Message:
        """Builds the command to move the lift."""
        union = DataUnion()
        union.move_lift = state.value

        cmd = Message()
        cmd.cmd = Command.MOVE_LIFT.value
        cmd.id = cls._generate_id()
        cmd.data = union
        cmd.checksum = 12
        return cmd

    @classmethod
    def other_command(cls, command: Command) -> Message:
        """Builds other commands that don't require any data."""
        union = DataUnion()
        cmd = Message()
        cmd.cmd = command.value
        cmd.id = cls._generate_id()
        cmd.data = union
        cmd.checksum = 12
        return cmd
