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
        rotate = RotateGrid()
        rotate.degrees = degrees

        union = DataUnion()
        union.cmd_rotate_grid = rotate

        cmd = Message()
        cmd.cmd = Command.ROTATE_GRID.value
        cmd.id = cls._generate_id()
        cmd.data_union = union
        cmd.checksum = 12
        return cmd

    @classmethod
    def rotate_grid_efficient(cls, degrees: int) -> Message:
        """Builds the command to rotate the grid in the opposite direction if it's shorter."""
        d = degrees % 360
        if d > 180:
            d -= 360
        return cls.rotate_grid(d)

    @classmethod
    def place_cubes(cls, red: int, yellow: int, blue: int) -> Message:
        """Builds the command to place the specified cubes."""
        place = PlaceCubes()
        place.cubes_red = red
        place.cubes_yellow = yellow
        place.cubes_blue = blue

        union = DataUnion()
        union.cmd_place_cubes = place

        cmd = Message()
        cmd.cmd = Command.PLACE_CUBES.value
        cmd.id = cls._generate_id()
        cmd.data_union = union
        cmd.checksum = 12
        return cmd

    @classmethod
    def move_lift(cls, state: MoveLift) -> Message:
        """Builds the command to move the lift."""
        union = DataUnion()
        union.cmd_move_lift = state.value

        cmd = Message()
        cmd.cmd = Command.MOVE_LIFT.value
        cmd.id = cls._generate_id()
        cmd.data_union = union
        cmd.checksum = 12
        return cmd

    @classmethod
    def other_command(cls, command: Command) -> Message:
        """Builds other commands that don't require any data."""
        union = DataUnion()
        cmd = Message()
        cmd.cmd = command.value
        cmd.id = cls._generate_id()
        cmd.data_union = union
        cmd.checksum = 12
        return cmd
