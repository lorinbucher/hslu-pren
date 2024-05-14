"""Unit tests for the build algorithm."""
import unittest
from multiprocessing import Queue

from builder.builder import Builder
from builder.layer import Layer
from shared.enumerations import CubeColor
from uart.command import Command


class TestBuildAlgorithm(unittest.TestCase):
    """Test class for the build algorithm."""

    def test_move_array_left(self):
        # Test moving elements to the left
        array = [1, 2, 3, 4, 5]
        expected_result = [2, 3, 4, 5, 1]
        self.assertEqual(Builder.move_array_left(array, 1), expected_result)

        # Test no shift
        self.assertEqual(Builder.move_array_left(array, 0), array)

        # Test shift by array length (should return the same array)
        self.assertEqual(Builder.move_array_left(array, len(array)), array)

        # Test shift more than array length
        expected_result = [4, 5, 1, 2, 3]
        self.assertEqual(Builder.move_array_left(array, 3), expected_result)

        # Test single-element array
        self.assertEqual(Builder.move_array_left([1], 1), [1])

    def test_move_array_right(self):
        # Test moving elements to the right
        array = [1, 2, 3, 4, 5]
        expected_result = [5, 1, 2, 3, 4]
        self.assertEqual(Builder.move_array_right(array, 1), expected_result)

        # Test no shift
        self.assertEqual(Builder.move_array_right(array, 0), array)

        # Test shift by array length (should return the same array)
        self.assertEqual(Builder.move_array_right(array, len(array)), array)

        # Test shift more than array length
        expected_result = [3, 4, 5, 1, 2]
        self.assertEqual(Builder.move_array_right(array, 3), expected_result)

        # Test single-element array
        self.assertEqual(Builder.move_array_right([1], 1), [1])

    def test_move_array(self):
        builder = Builder(Queue(), Queue())
        # Resetting pos that tests also work when there are changes
        builder.reset()

        # Test 1: Move array left by 1
        builder.move_pos(1)
        self.assertEqual(builder.pos, [CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE, CubeColor.NONE])

        # Resetting position for the next test
        builder.reset()

        # Test 2: Move array left by 2
        builder.move_pos(2)
        self.assertEqual(builder.pos, [CubeColor.YELLOW, CubeColor.BLUE, CubeColor.NONE, CubeColor.RED])

        # Resetting position for the next test
        builder.reset()

        # Test 3: Move array right by 1
        builder.move_pos(-1)
        self.assertEqual(builder.pos, [CubeColor.BLUE, CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW])

        # Resetting position for the next test
        builder.reset()

        # Test 4: Move array right by 2
        builder.move_pos(-2)
        self.assertEqual(builder.pos, [CubeColor.YELLOW, CubeColor.BLUE, CubeColor.NONE, CubeColor.RED])

        # Additional test cases can be added as needed to thoroughly test all edge cases and behaviors.

    def test_rotate_times(self):
        uart_write = Queue()
        builder = Builder(Queue(), uart_write)

        builder.rotate_times(2)
        message = uart_write.get()
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data_union.cmd_rotate_grid.degrees, 180)

        builder.rotate_times(-3)
        message = uart_write.get()
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data_union.cmd_rotate_grid.degrees, 90)

        builder.rotate_times(-2)
        message = uart_write.get()
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data_union.cmd_rotate_grid.degrees, 180)

        builder.rotate_times(-1)
        message = uart_write.get()
        self.assertEqual(Command(message.cmd), Command.ROTATE_GRID)
        self.assertEqual(message.data_union.cmd_rotate_grid.degrees, -90)

    def test_place_cubes(self):
        uart_write = Queue()
        builder = Builder(Queue(), uart_write)

        builder.place_cubes([[False, False, False, False]])
        self.assertTrue(uart_write.empty())

        builder.place_cubes([False, True, True, True])
        message = uart_write.get()
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data_union.cmd_place_cubes.cubes_red, 1)
        self.assertEqual(message.data_union.cmd_place_cubes.cubes_yellow, 1)
        self.assertEqual(message.data_union.cmd_place_cubes.cubes_blue, 1)

        builder.place_cubes([True, True, True, True])
        message = uart_write.get()
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data_union.cmd_place_cubes.cubes_red, 1)
        self.assertEqual(message.data_union.cmd_place_cubes.cubes_yellow, 1)
        self.assertEqual(message.data_union.cmd_place_cubes.cubes_blue, 1)

        builder.place_cubes([False, False, True, False])
        message = uart_write.get()
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data_union.cmd_place_cubes.cubes_red, 0)
        self.assertEqual(message.data_union.cmd_place_cubes.cubes_yellow, 1)
        self.assertEqual(message.data_union.cmd_place_cubes.cubes_blue, 0)

        builder.place_cubes([False, True, False, True])
        message = uart_write.get()
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data_union.cmd_place_cubes.cubes_red, 1)
        self.assertEqual(message.data_union.cmd_place_cubes.cubes_yellow, 0)
        self.assertEqual(message.data_union.cmd_place_cubes.cubes_blue, 1)

        builder.rotate_times(2)
        message = uart_write.get()
        builder.place_cubes([True, False, False, False])
        message = uart_write.get()
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data_union.cmd_place_cubes.cubes_red, 0)
        self.assertEqual(message.data_union.cmd_place_cubes.cubes_yellow, 1)
        self.assertEqual(message.data_union.cmd_place_cubes.cubes_blue, 0)

        builder.place_cubes([False, True, False, False])
        message = uart_write.get()
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data_union.cmd_place_cubes.cubes_red, 0)
        self.assertEqual(message.data_union.cmd_place_cubes.cubes_yellow, 0)
        self.assertEqual(message.data_union.cmd_place_cubes.cubes_blue, 1)

        builder.place_cubes([False, False, False, True])
        message = uart_write.get()
        self.assertEqual(Command(message.cmd), Command.PLACE_CUBES)
        self.assertEqual(message.data_union.cmd_place_cubes.cubes_red, 1)
        self.assertEqual(message.data_union.cmd_place_cubes.cubes_yellow, 0)
        self.assertEqual(message.data_union.cmd_place_cubes.cubes_blue, 0)

    def test_array_false(self):
        self.assertFalse(Builder.array_false_check([True, True, True, True]))
        self.assertFalse(Builder.array_false_check([False, True, False, False]))
        self.assertTrue(Builder.array_false_check([False, False, False, False]))

    def test_match(self):
        builder = Builder(Queue(), Queue())

        self.assertEqual([False, False, False, False], builder.match(Layer.BOTTOM))
        builder.rotate_times(1)
        self.assertEqual([True, True, False, False], builder.match(Layer.BOTTOM))
        builder.rotate_times(1)
        self.assertEqual([False, False, True, True], builder.match(Layer.BOTTOM))

    def test_update(self):
        builder = Builder(Queue(), Queue())

        builder.update_placed(Layer.BOTTOM, [True, True, True, True])
        self.assertEqual([True, True, True, True, False, False, False, False], builder.placed)
        self.assertFalse(builder.full_placed_check(Layer.TOP))
        self.assertTrue(builder.full_placed_check(Layer.BOTTOM))
        builder.update_placed(False, [True, True, True, True])
        self.assertEqual([True, True, True, True, True, True, True, True], builder.placed)
        self.assertTrue(builder.full_placed_check(Layer.TOP))
        self.assertTrue(builder.full_placed_check(Layer.BOTTOM))
