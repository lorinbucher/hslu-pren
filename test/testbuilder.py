"""Unit tests for the build algorithm."""
import unittest
from multiprocessing import Queue

from rebuilder.builder import Builder, Layer
from shared.enumerations import CubeColor
from uart.command import Command


class TestBuildAlgorithm(unittest.TestCase):
    """Test class for the build algorithm."""

    def test_move_pos(self):
        builder = Builder(Queue(), Queue())

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
        uart_write = Queue()
        builder = Builder(Queue(), uart_write)

        builder.rotate_grid(-5)
        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, -90)

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
        self.assertEqual(message.data.rotate_grid.degrees, -90)

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
        self.assertEqual(message.data.rotate_grid.degrees, -90)

        builder.rotate_grid(4)
        self.assertTrue(uart_write.empty())

        builder.rotate_grid(5)
        message = uart_write.get(timeout=2.0)
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data.rotate_grid.degrees, 90)

    def test_place_cubes(self):
        uart_write = Queue()
        builder = Builder(Queue(), uart_write)

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

    def test_match(self):
        builder = Builder(Queue(), Queue())

        self.assertEqual([False, False, False, False], builder.match(Layer.BOTTOM))
        builder.rotate_grid(1)
        self.assertEqual([True, True, False, False], builder.match(Layer.BOTTOM))
        builder.rotate_grid(1)
        self.assertEqual([False, False, True, True], builder.match(Layer.BOTTOM))

    def test_update(self):
        builder = Builder(Queue(), Queue())

        builder.update_placed(Layer.BOTTOM, [True, True, True, True])
        self.assertEqual([True, True, True, True, False, False, False, False], builder.placed)
        self.assertFalse(builder.layer_placed(Layer.TOP))
        self.assertTrue(builder.layer_placed(Layer.BOTTOM))
        builder.update_placed(Layer.TOP, [True, True, True, True])
        self.assertEqual([True, True, True, True, True, True, True, True], builder.placed)
        self.assertTrue(builder.layer_placed(Layer.TOP))
        self.assertTrue(builder.layer_placed(Layer.BOTTOM))
