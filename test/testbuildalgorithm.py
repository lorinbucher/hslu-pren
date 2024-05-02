from builder.buildalgorithm import buildalgorithm
from shared.cubecolor import CubeColor
from builder.uartcomunicatorSpy import uartcomunicatorSpy
import unittest

class testbuildalgorithm(unittest.TestCase):
    def setUp(self):
        self.builder = buildalgorithm(uartcomunicatorSpy())

    def test_move_array_left(self):
        # Test moving elements to the left
        array = [1, 2, 3, 4, 5]
        expected_result = [2, 3, 4, 5, 1]
        self.assertEqual(self.builder.moveArrayLeft(array, 1), expected_result)

        # Test no shift
        self.assertEqual(self.builder.moveArrayLeft(array, 0), array)

        # Test shift by array length (should return the same array)
        self.assertEqual(self.builder.moveArrayLeft(array, len(array)), array)

        # Test shift more than array length
        expected_result = [4, 5, 1, 2, 3]
        self.assertEqual(self.builder.moveArrayLeft(array, 3), expected_result)

        # Test single-element array
        self.assertEqual(self.builder.moveArrayLeft([1], 1), [1])

    def test_move_array_right(self):
        # Test moving elements to the right
        array = [1, 2, 3, 4, 5]
        expected_result = [5, 1, 2, 3, 4]
        self.assertEqual(self.builder.moveArrayRight(array, 1), expected_result)

        # Test no shift
        self.assertEqual(self.builder.moveArrayRight(array, 0), array)

        # Test shift by array length (should return the same array)
        self.assertEqual(self.builder.moveArrayRight(array, len(array)), array)

        # Test shift more than array length
        expected_result = [3, 4, 5, 1, 2]
        self.assertEqual(self.builder.moveArrayRight(array, 3), expected_result)

        # Test single-element array
        self.assertEqual(self.builder.moveArrayRight([1], 1), [1])

    def test_move_array(self):
        # Reseting pos that tests also work when there are changes
        self.builder.pos = [CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE]

        # Test 1: Move array left by 1
        self.builder.moveArray(1)
        assert self.builder.pos == [CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE, CubeColor.NONE], "Test 1 Failed: moveArray(1) did not rotate left correctly."

        # Resetting position for the next test
        self.builder.pos = [CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE]

        # Test 2: Move array left by 2
        self.builder.moveArray(2)
        assert self.builder.pos == [CubeColor.YELLOW, CubeColor.BLUE, CubeColor.NONE, CubeColor.RED], "Test 2 Failed: moveArray(2) did not rotate left twice correctly."

        # Resetting position for the next test
        self.builder.pos = [CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE]

        # Test 3: Move array right by 1
        self.builder.moveArray(-1)
        assert self.builder.pos == [CubeColor.BLUE, CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW], "Test 3 Failed: moveArray(-1) did not rotate right correctly."

        # Resetting position for the next test
        self.builder.pos = [CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE]

        # Test 4: Move array right by 2
        self.builder.moveArray(-2)
        assert self.builder.pos == [CubeColor.YELLOW, CubeColor.BLUE, CubeColor.NONE, CubeColor.RED], "Test 4 Failed: moveArray(-2) did not rotate right twice correctly."

        # Additional test cases can be added as needed to thoroughly test all edge cases and behaviors.


if __name__ == '__main__':
    unittest.main()