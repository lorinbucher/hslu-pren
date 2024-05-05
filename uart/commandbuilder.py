"""Helper classes to build the commands for the UART communication protocol."""
from .command import Command, RotateGrid, PlaceCubes, DataUnion, Message, SendState


class CommandBuilder:
    """Assembles the command for the UART communication protocol."""
    id = 0

    def generate_id(self):
        CommandBuilder.id = (CommandBuilder.id + 1) % 256
        return CommandBuilder.id

    def rotate_grid(self, degrees):
        union = DataUnion()
        cmd = Message()
        cmd.checksum = 12
        cmd.id = self.generate_id()
        rotate = RotateGrid()
        rotate.degrees = degrees
        union.cmd_rotate_grid = rotate
        cmd.cmd = Command.ROTATE_GRID.value
        cmd.data_union = union
        return cmd

    def rotate_grid_efficient(self, degrees):
        d = degrees % 360
        if d > 180:
            d -= 360
        return self.rotate_grid(d)

    def place_cubes(self, red, yellow, blue):
        union = DataUnion()
        cmd = Message()
        cmd.checksum = 12
        cmd.id = self.generate_id()
        place = PlaceCubes()
        place.cubes_red = red
        place.cubes_yellow = yellow
        place.cubes_blue = blue
        union.cmd_place_cubes = place
        cmd.cmd = Command.PLACE_CUBES.value
        cmd.data_union = union
        return cmd

    def move_lift(self, state):
        union = DataUnion()
        cmd = Message()
        cmd.checksum = 12
        cmd.id = self.generate_id()
        union.cmd_move_lift = state.value
        cmd.cmd = Command.MOVE_LIFT.value
        cmd.data_union = union
        return cmd

    def send_state(self, dummy1, dummy2, dummy3, dummy4):
        union = DataUnion()
        cmd = Message()
        cmd.checksum = 12
        cmd.id = self.generate_id()
        cmd.cmd = Command.SEND_STATE.value
        state = SendState()
        state.dummy1 = dummy1
        state.dummy2 = dummy2
        state.dummy3 = dummy3
        state.dummy4 = dummy4
        union.cmd_send_state = state
        cmd.data_union = union
        return cmd

    def other_commands(self, command):
        union = DataUnion()
        cmd = Message()
        cmd.checksum = 12
        cmd.id = self.generate_id()
        cmd.cmd = command.value
        cmd.data_union = union
        return cmd
