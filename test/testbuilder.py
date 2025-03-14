"""Unit tests for the build algorithm."""
import queue
import unittest

from rebuilder.builder import Builder, CubeState
from shared.enumerations import CubeColor
from uart.command import Command


class TestBuildAlgorithm(unittest.TestCase):
    """Test class for the build algorithm."""

    def test_move_pos(self):
        builder = Builder(queue.Queue())

        # Move array left by 1
        builder.reset()
        builder.move_pos(1)
        self.assertEqual(builder.pos, [CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE, CubeColor.NONE])

        # Move array left by 2
        builder.reset()
        builder.move_pos(2)
        self.assertEqual(builder.pos, [CubeColor.YELLOW, CubeColor.BLUE, CubeColor.NONE, CubeColor.RED])

        # Move array left more often than length of array
        builder.reset()
        builder.move_pos(6)
        self.assertEqual(builder.pos, [CubeColor.YELLOW, CubeColor.BLUE, CubeColor.NONE, CubeColor.RED])

        # Move array right by 1
        builder.reset()
        builder.move_pos(-1)
        self.assertEqual(builder.pos, [CubeColor.BLUE, CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW])

        # Move array right by 2
        builder.reset()
        builder.move_pos(-2)
        self.assertEqual(builder.pos, [CubeColor.YELLOW, CubeColor.BLUE, CubeColor.NONE, CubeColor.RED])

        # Move array right more often than length of array
        builder.reset()
        builder.move_pos(-6)
        self.assertEqual(builder.pos, [CubeColor.YELLOW, CubeColor.BLUE, CubeColor.NONE, CubeColor.RED])

    def test_rotate_grid(self):
        uart_write = queue.Queue()
        builder = Builder(uart_write)

        builder.rotate_grid(-5)
        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 270)

        builder.rotate_grid(-4)
        self.assertTrue(uart_write.empty())

        builder.rotate_grid(-3)
        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 90)

        builder.rotate_grid(-2)
        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 180)

        builder.rotate_grid(-1)
        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 270)

        builder.rotate_grid(0)
        self.assertTrue(uart_write.empty())

        builder.rotate_grid(1)
        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 90)

        builder.rotate_grid(2)
        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 180)

        builder.rotate_grid(3)
        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 270)

        builder.rotate_grid(4)
        self.assertTrue(uart_write.empty())

        builder.rotate_grid(5)
        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 90)

    def test_place_cubes(self):
        uart_write = queue.Queue()
        builder = Builder(uart_write)

        builder.place_cubes([False, False, False, False])
        self.assertTrue(uart_write.empty())

        builder.place_cubes([False, True, True, True])
        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 1)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 1)
        self.assertEqual(message.data.place_cubes.cubes_blue, 1)

        builder.place_cubes([True, True, True, True])
        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 1)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 1)
        self.assertEqual(message.data.place_cubes.cubes_blue, 1)

        builder.place_cubes([False, False, True, False])
        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 0)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 1)
        self.assertEqual(message.data.place_cubes.cubes_blue, 0)

        builder.place_cubes([False, True, False, True])
        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 1)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 0)
        self.assertEqual(message.data.place_cubes.cubes_blue, 1)

        builder.rotate_grid(2)
        message = uart_write.get(timeout=2.0)
        builder.place_cubes([True, False, False, False])
        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 0)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 1)
        self.assertEqual(message.data.place_cubes.cubes_blue, 0)

        builder.place_cubes([False, True, False, False])
        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 0)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 0)
        self.assertEqual(message.data.place_cubes.cubes_blue, 1)

        builder.place_cubes([False, False, False, True])
        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 1)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 0)
        self.assertEqual(message.data.place_cubes.cubes_blue, 0)

    def test_array_false(self):
        self.assertFalse(Builder.array_false([True, True, True, True]))
        self.assertFalse(Builder.array_false([False, True, False, False]))
        self.assertTrue(Builder.array_false([False, False, False, False]))

    def test_match_with_config(self):
        builder = Builder(queue.Queue())
        matches, config = builder.match_with_config([CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE])
        self.assertEqual([False, True, True, True], matches)
        self.assertEqual([CubeColor.NONE, CubeColor.NONE, CubeColor.NONE, CubeColor.NONE], config)
        builder.rotate_grid(1, True)
        matches, config = builder.match_with_config([CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE, CubeColor.RED])
        self.assertEqual([True, True, True, False], matches)
        self.assertEqual([CubeColor.NONE, CubeColor.NONE, CubeColor.NONE, CubeColor.RED], config)

    def test_config_none(self):
        self.assertEqual(True, Builder.config_none([CubeColor.NONE, CubeColor.NONE, CubeColor.NONE, CubeColor.NONE]))
        self.assertEqual(False, Builder.config_none([CubeColor.RED, CubeColor.NONE, CubeColor.NONE, CubeColor.NONE]))

    def test_build_config_1(self):
        uart_write = queue.Queue()
        builder = Builder(uart_write)

        builder.build_config([CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE])
        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 1)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 1)
        self.assertEqual(message.data.place_cubes.cubes_blue, 1)

    def test_build_config_2(self):
        uart_write = queue.Queue()
        builder = Builder(uart_write)

        builder.build_config([CubeColor.RED, CubeColor.RED, CubeColor.RED, CubeColor.RED])

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 1)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 0)
        self.assertEqual(message.data.place_cubes.cubes_blue, 0)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 90)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 1)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 0)
        self.assertEqual(message.data.place_cubes.cubes_blue, 0)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 90)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 1)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 0)
        self.assertEqual(message.data.place_cubes.cubes_blue, 0)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 90)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 1)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 0)
        self.assertEqual(message.data.place_cubes.cubes_blue, 0)

        self.assertTrue(uart_write.empty())

    def test_update_cube_state(self):
        builder = Builder(queue.Queue())
        builder.update_cube_states()
        self.assertEqual(
            [CubeState.NOTPLACED, CubeState.NOTPLACED, CubeState.PLACED, CubeState.NOTPLACED, CubeState.NOTPLACED,
             CubeState.NOTPLACED, CubeState.PLACED, CubeState.NOTPLACED], builder.cube_states)

    def test_build_1(self):
        uart_write = queue.Queue()
        builder = Builder(uart_write)

        builder.set_config(
            [CubeColor.RED, CubeColor.YELLOW, CubeColor.NONE, CubeColor.RED, CubeColor.NONE, CubeColor.NONE,
             CubeColor.NONE, CubeColor.NONE])

        builder.build()
        builder.finish_build()

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 90)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 1)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 1)
        self.assertEqual(message.data.place_cubes.cubes_blue, 0)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 90)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 1)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 0)
        self.assertEqual(message.data.place_cubes.cubes_blue, 0)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 180)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.MOVE_LIFT)
        self.assertEqual(message.data.move_lift, 1)

    def test_build_2(self):
        uart_write = queue.Queue()
        builder = Builder(uart_write)

        builder.set_config(
            [CubeColor.RED, CubeColor.YELLOW, CubeColor.NONE, CubeColor.RED, CubeColor.RED, CubeColor.YELLOW,
             CubeColor.NONE, CubeColor.RED])

        builder.build()
        builder.finish_build()

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 90)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 1)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 1)
        self.assertEqual(message.data.place_cubes.cubes_blue, 0)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 90)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 1)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 0)
        self.assertEqual(message.data.place_cubes.cubes_blue, 0)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 1)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 0)
        self.assertEqual(message.data.place_cubes.cubes_blue, 0)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 270)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 1)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 1)
        self.assertEqual(message.data.place_cubes.cubes_blue, 0)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 270)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.MOVE_LIFT)
        self.assertEqual(message.data.move_lift, 1)

    def test_build_3(self):
        uart_write = queue.Queue()
        builder = Builder(uart_write)

        builder.set_config(
            [CubeColor.RED, CubeColor.UNKNOWN, CubeColor.NONE, CubeColor.RED, CubeColor.RED, CubeColor.YELLOW,
             CubeColor.NONE, CubeColor.RED])

        builder.build_whats_possible()

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 90)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 1)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 0)
        self.assertEqual(message.data.place_cubes.cubes_blue, 0)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 90)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 1)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 0)
        self.assertEqual(message.data.place_cubes.cubes_blue, 0)

        builder.set_config(
            [CubeColor.RED, CubeColor.YELLOW, CubeColor.NONE, CubeColor.RED, CubeColor.RED, CubeColor.YELLOW,
             CubeColor.NONE, CubeColor.RED])
        builder.build_whats_possible()

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 1)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 0)
        self.assertEqual(message.data.place_cubes.cubes_blue, 0)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 270)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 1)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 0)
        self.assertEqual(message.data.place_cubes.cubes_blue, 0)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 0)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 1)
        self.assertEqual(message.data.place_cubes.cubes_blue, 0)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 0)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 1)
        self.assertEqual(message.data.place_cubes.cubes_blue, 0)

        builder.finish_build()

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 270)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.MOVE_LIFT)
        self.assertEqual(message.data.move_lift, 1)

    def test_build_with_doubles_first_1(self):
        uart_write = queue.Queue()
        builder = Builder(uart_write)

        builder.set_config(
            [CubeColor.RED, CubeColor.YELLOW, CubeColor.NONE, CubeColor.RED, CubeColor.RED, CubeColor.YELLOW,
             CubeColor.NONE, CubeColor.RED])

        builder.build(True)
        builder.finish_build()

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 90)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 2)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 2)
        self.assertEqual(message.data.place_cubes.cubes_blue, 0)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 90)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 2)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 0)
        self.assertEqual(message.data.place_cubes.cubes_blue, 0)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 180)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.MOVE_LIFT)
        self.assertEqual(message.data.move_lift, 1)

    def test_build_with_doubles_first_2(self):
        uart_write = queue.Queue()
        builder = Builder(uart_write)

        builder.set_config(
            [CubeColor.RED, CubeColor.YELLOW, CubeColor.NONE, CubeColor.RED, CubeColor.RED, CubeColor.BLUE,
             CubeColor.NONE, CubeColor.RED])

        builder.build(True)
        builder.finish_build()

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 90)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 2)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 0)
        self.assertEqual(message.data.place_cubes.cubes_blue, 0)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 90)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 2)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 0)
        self.assertEqual(message.data.place_cubes.cubes_blue, 0)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 270)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 0)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 1)
        self.assertEqual(message.data.place_cubes.cubes_blue, 0)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 90)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data.place_cubes.cubes_red, 0)
        self.assertEqual(message.data.place_cubes.cubes_yellow, 0)
        self.assertEqual(message.data.place_cubes.cubes_blue, 1)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 180)

        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.MOVE_LIFT)
        self.assertEqual(message.data.move_lift, 1)
