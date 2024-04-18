import serial
from time import sleep
from command import COMMAND, CmdRotateGrid, CmdPlaceCubes, CmdMoveLift, DataUnion, Message, CmdSendState

class commandbuilder:
    id = 0

    def idGenerator(self):
        commandbuilder.id = (commandbuilder.id + 1) % 256
        return commandbuilder.id
    

    def rotateGrid(self, degrees_h, degrees_l):
        union = DataUnion()
        cmd = Message()
        cmd.checksum = 12
        cmd.id = self.idGenerator()
        rotate = CmdRotateGrid()
        rotate.degrees_h = degrees_h
        rotate.degrees_l = degrees_l
        union.cmdRotateGrid = rotate
        cmd.cmd = COMMAND.CMD_ROTATE_GRID.value
        cmd.dataUnion = union
        return cmd

    def placeCubes(self, red, yellow, blue):
        union = DataUnion()
        cmd = Message()
        cmd.checksum = 12
        cmd.id = self.idGenerator()
        place = CmdPlaceCubes()
        place.cubes_red = red
        place.cubes_yellow = yellow
        place.cubes_blue = blue
        union.cmdPlaceCubes = place
        cmd.cmd = COMMAND.CMD_PLACE_CUBES.value
        cmd.dataUnion = union
        return cmd

    def moveLift(self, state):
        union = DataUnion()
        cmd = Message()
        cmd.checksum = 12
        cmd.id = self.idGenerator()
        union.cmdMoveLift = state.value
        cmd.cmd = COMMAND.CMD_MOVE_LIFT.value
        cmd.dataUnion = union
        return cmd

    def sendState(self, dummy1, dummy2, dummy3, dummy4):
        union = DataUnion()
        cmd = Message()
        cmd.checksum = 12
        cmd.id = self.idGenerator()
        cmd.cmd = COMMAND.CMD_SEND_STATE.value
        state = CmdSendState()
        state.dummy1 = dummy1
        state.dummy2 = dummy2
        state.dummy3 = dummy3
        state.dummy4 = dummy4
        union.cmdSendState = state
        cmd.dataUnion = union
        return cmd

    def otherCommands(self, command):
        union = DataUnion()
        cmd = Message()
        cmd.checksum = 12
        cmd.id = self.idGenerator()
        cmd.cmd = command.value
        cmd.dataUnion = union
        return cmd
    
if __name__ == "__main__":
    command = commandbuilder().otherCommands(COMMAND.CMD_ACKNOWLEDGE)
