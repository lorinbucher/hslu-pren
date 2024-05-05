from .command import Command, CmdRotateGrid, CmdPlaceCubes, DataUnion, Message, CmdSendState


class CommandBuilder:
    id = 0

    def generate_id(self):
        CommandBuilder.id = (CommandBuilder.id + 1) % 256
        return CommandBuilder.id

    def rotate_grid(self, degrees):
        union = DataUnion()
        cmd = Message()
        cmd.checksum = 12
        cmd.id = self.generate_id()
        rotate = CmdRotateGrid()
        rotate.degrees = degrees
        union.cmdRotateGrid = rotate
        cmd.cmd = Command.ROTATE_GRID.value
        cmd.dataUnion = union
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
        place = CmdPlaceCubes()
        place.cubes_red = red
        place.cubes_yellow = yellow
        place.cubes_blue = blue
        union.cmdPlaceCubes = place
        cmd.cmd = Command.PLACE_CUBES.value
        cmd.dataUnion = union
        return cmd

    def move_lift(self, state):
        union = DataUnion()
        cmd = Message()
        cmd.checksum = 12
        cmd.id = self.generate_id()
        union.cmdMoveLift = state.value
        cmd.cmd = Command.MOVE_LIFT.value
        cmd.dataUnion = union
        return cmd

    def send_state(self, dummy1, dummy2, dummy3, dummy4):
        union = DataUnion()
        cmd = Message()
        cmd.checksum = 12
        cmd.id = self.generate_id()
        cmd.cmd = Command.SEND_STATE.value
        state = CmdSendState()
        state.dummy1 = dummy1
        state.dummy2 = dummy2
        state.dummy3 = dummy3
        state.dummy4 = dummy4
        union.cmdSendState = state
        cmd.dataUnion = union
        return cmd

    def other_commands(self, command):
        union = DataUnion()
        cmd = Message()
        cmd.checksum = 12
        cmd.id = self.generate_id()
        cmd.cmd = command.value
        cmd.dataUnion = union
        return cmd
