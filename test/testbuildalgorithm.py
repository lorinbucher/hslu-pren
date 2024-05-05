"""Unit tests for the build algorithm."""
import unittest

from builder.buildalgorithm import BuildAlgorithm
from builder.layer import Layer
from builder.uartcommunicatorspy import UartCommunicatorSpy
from shared.enumerations import CubeColor


class TestBuildAlgorithm(unittest.TestCase):
    """Test class for the build algorithm."""

    def test_move_array_left(self):
        # Test moving elements to the left
        array = [1, 2, 3, 4, 5]
        expected_result = [2, 3, 4, 5, 1]
        self.assertEqual(BuildAlgorithm.move_array_left(array, 1), expected_result)

        # Test no shift
        self.assertEqual(BuildAlgorithm.move_array_left(array, 0), array)

        # Test shift by array length (should return the same array)
        self.assertEqual(BuildAlgorithm.move_array_left(array, len(array)), array)

        # Test shift more than array length
        expected_result = [4, 5, 1, 2, 3]
        self.assertEqual(BuildAlgorithm.move_array_left(array, 3), expected_result)

        # Test single-element array
        self.assertEqual(BuildAlgorithm.move_array_left([1], 1), [1])

    def test_move_array_right(self):
        # Test moving elements to the right
        array = [1, 2, 3, 4, 5]
        expected_result = [5, 1, 2, 3, 4]
        self.assertEqual(BuildAlgorithm.move_array_right(array, 1), expected_result)

        # Test no shift
        self.assertEqual(BuildAlgorithm.move_array_right(array, 0), array)

        # Test shift by array length (should return the same array)
        self.assertEqual(BuildAlgorithm.move_array_right(array, len(array)), array)

        # Test shift more than array length
        expected_result = [3, 4, 5, 1, 2]
        self.assertEqual(BuildAlgorithm.move_array_right(array, 3), expected_result)

        # Test single-element array
        self.assertEqual(BuildAlgorithm.move_array_right([1], 1), [1])

    def test_move_array(self):
        builder = BuildAlgorithm(UartCommunicatorSpy())
        # Reseting pos that tests also work when there are changes
        builder.pos = [CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE]

        # Test 1: Move array left by 1
        builder.move_pos(1)
        assert builder.pos == [CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE,
                               CubeColor.NONE], 'Test 1 Failed: moveArray(1) did not rotate left correctly.'

        # Resetting position for the next test
        builder.pos = [CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE]

        # Test 2: Move array left by 2
        builder.move_pos(2)
        assert builder.pos == [CubeColor.YELLOW, CubeColor.BLUE, CubeColor.NONE,
                               CubeColor.RED], 'Test 2 Failed: moveArray(2) did not rotate left twice correctly.'

        # Resetting position for the next test
        builder.pos = [CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE]

        # Test 3: Move array right by 1
        builder.move_pos(-1)
        assert builder.pos == [CubeColor.BLUE, CubeColor.NONE, CubeColor.RED,
                               CubeColor.YELLOW], 'Test 3 Failed: moveArray(-1) did not rotate right correctly.'

        # Resetting position for the next test
        builder.pos = [CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE]

        # Test 4: Move array right by 2
        builder.move_pos(-2)
        assert builder.pos == [CubeColor.YELLOW, CubeColor.BLUE, CubeColor.NONE,
                               CubeColor.RED], 'Test 4 Failed: moveArray(-2) did not rotate right twice correctly.'

        # Additional test cases can be added as needed to thoroughly test all edge cases and behaviors.

    def test_rotate_times(self):
        communicator = UartCommunicatorSpy()
        builder = BuildAlgorithm(communicator)

        builder.rotate_times(2)
        self.assertEqual('Command ID: 4Message ID: Checksum: 12Rotate Grid Degrees: 180', communicator.last_result)

        builder.rotate_times(-3)
        self.assertEqual('Command ID: 4Message ID: Checksum: 12Rotate Grid Degrees: 90', communicator.last_result)

        builder.rotate_times(-2)
        self.assertEqual('Command ID: 4Message ID: Checksum: 12Rotate Grid Degrees: 180', communicator.last_result)

        builder.rotate_times(-1)
        self.assertEqual('Command ID: 4Message ID: Checksum: 12Rotate Grid Degrees: -90', communicator.last_result)

    def test_place_cubes(self):
        communicator = UartCommunicatorSpy()
        builder = BuildAlgorithm(communicator)

        builder.place_cubes([[False, False, False, False]])
        self.assertIsNone(communicator.last_result)

        builder.place_cubes([False, True, True, True])
        self.assertEqual('Command ID: 5Message ID: Checksum: 12Place Cubes - Red: 1, Yellow: 1, Blue: 1',
                         communicator.last_result)

        builder.place_cubes([True, True, True, True])
        self.assertEqual('Command ID: 5Message ID: Checksum: 12Place Cubes - Red: 1, Yellow: 1, Blue: 1',
                         communicator.last_result)

        builder.place_cubes([False, False, True, False])
        self.assertEqual('Command ID: 5Message ID: Checksum: 12Place Cubes - Red: 0, Yellow: 1, Blue: 0',
                         communicator.last_result)

        builder.place_cubes([False, True, False, True])
        self.assertEqual('Command ID: 5Message ID: Checksum: 12Place Cubes - Red: 1, Yellow: 0, Blue: 1',
                         communicator.last_result)

        builder.rotate_times(2)
        builder.place_cubes([True, False, False, False])
        self.assertEqual('Command ID: 5Message ID: Checksum: 12Place Cubes - Red: 0, Yellow: 1, Blue: 0',
                         communicator.last_result)

        builder.place_cubes([False, True, False, False])
        self.assertEqual('Command ID: 5Message ID: Checksum: 12Place Cubes - Red: 0, Yellow: 0, Blue: 1',
                         communicator.last_result)

        builder.place_cubes([False, False, False, True])
        self.assertEqual('Command ID: 5Message ID: Checksum: 12Place Cubes - Red: 1, Yellow: 0, Blue: 0',
                         communicator.last_result)

    def test_array_false(self):
        self.assertFalse(BuildAlgorithm.array_false_check([True, True, True, True]))
        self.assertFalse(BuildAlgorithm.array_false_check([False, True, False, False]))
        self.assertTrue(BuildAlgorithm.array_false_check([False, False, False, False]))

    def test_match(self):
        communicator = UartCommunicatorSpy()
        builder = BuildAlgorithm(communicator)

        self.assertEqual([False, False, False, False], builder.match(Layer.BOTTOM))
        builder.rotate_times(1)
        self.assertEqual([True, True, False, False], builder.match(Layer.BOTTOM))
        builder.rotate_times(1)
        self.assertEqual([False, False, True, True], builder.match(Layer.BOTTOM))

    def test_update(self):
        communicator = UartCommunicatorSpy()
        builder = BuildAlgorithm(communicator)

        builder.update_placed(Layer.BOTTOM, [True, True, True, True])
        self.assertEqual([True, True, True, True, False, False, False, False], builder.placed)
        self.assertFalse(builder.full_placed_check(Layer.TOP))
        self.assertTrue(builder.full_placed_check(Layer.BOTTOM))
        builder.update_placed(False, [True, True, True, True])
        self.assertEqual([True, True, True, True, True, True, True, True], builder.placed)
        self.assertTrue(builder.full_placed_check(Layer.TOP))
        self.assertTrue(builder.full_placed_check(Layer.BOTTOM))
