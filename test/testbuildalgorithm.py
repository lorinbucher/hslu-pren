from builder.buildalgorithm import buildalgorithm
from shared.cubecolor import CubeColor
from builder.uartcomunicatorSpy import uartcomunicatorSpy
import unittest

class testbuildalgorithm(unittest.TestCase):
    
    def test_move_array_left(self):
        # Test moving elements to the left
        array = [1, 2, 3, 4, 5]
        expected_result = [2, 3, 4, 5, 1]
        self.assertEqual(buildalgorithm.moveArrayLeft(array, 1), expected_result)

        # Test no shift
        self.assertEqual(buildalgorithm.moveArrayLeft(array, 0), array)

        # Test shift by array length (should return the same array)
        self.assertEqual(buildalgorithm.moveArrayLeft(array, len(array)), array)

        # Test shift more than array length
        expected_result = [4, 5, 1, 2, 3]
        self.assertEqual(buildalgorithm.moveArrayLeft(array, 3), expected_result)

        # Test single-element array
        self.assertEqual(buildalgorithm.moveArrayLeft([1], 1), [1])

    def test_move_array_right(self):
        # Test moving elements to the right
        array = [1, 2, 3, 4, 5]
        expected_result = [5, 1, 2, 3, 4]
        self.assertEqual(buildalgorithm.moveArrayRight(array, 1), expected_result)

        # Test no shift
        self.assertEqual(buildalgorithm.moveArrayRight(array, 0), array)

        # Test shift by array length (should return the same array)
        self.assertEqual(buildalgorithm.moveArrayRight(array, len(array)), array)

        # Test shift more than array length
        expected_result = [3, 4, 5, 1, 2]
        self.assertEqual(buildalgorithm.moveArrayRight(array, 3), expected_result)

        # Test single-element array
        self.assertEqual(buildalgorithm.moveArrayRight([1], 1), [1])

    def test_move_array(self):
        builder = buildalgorithm(uartcomunicatorSpy())
        # Reseting pos that tests also work when there are changes
        builder.pos = [CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE]

        # Test 1: Move array left by 1
        builder.movePos(1)
        assert builder.pos == [CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE, CubeColor.NONE], "Test 1 Failed: moveArray(1) did not rotate left correctly."

        # Resetting position for the next test
        builder.pos = [CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE]

        # Test 2: Move array left by 2
        builder.movePos(2)
        assert builder.pos == [CubeColor.YELLOW, CubeColor.BLUE, CubeColor.NONE, CubeColor.RED], "Test 2 Failed: moveArray(2) did not rotate left twice correctly."

        # Resetting position for the next test
        builder.pos = [CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE]

        # Test 3: Move array right by 1
        builder.movePos(-1)
        assert builder.pos == [CubeColor.BLUE, CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW], "Test 3 Failed: moveArray(-1) did not rotate right correctly."

        # Resetting position for the next test
        builder.pos = [CubeColor.NONE, CubeColor.RED, CubeColor.YELLOW, CubeColor.BLUE]

        # Test 4: Move array right by 2
        builder.movePos(-2)
        assert builder.pos == [CubeColor.YELLOW, CubeColor.BLUE, CubeColor.NONE, CubeColor.RED], "Test 4 Failed: moveArray(-2) did not rotate right twice correctly."

        # Additional test cases can be added as needed to thoroughly test all edge cases and behaviors.

    def testRotateTimes(self):
        communicator = uartcomunicatorSpy()
        builder = buildalgorithm(communicator)

        builder.rotateTimes(2)
        self.assertEqual('Command ID: 4Message ID: Checksum: 12Rotate Grid Degrees: 180', communicator.lastresult)

        builder.rotateTimes(-3)
        self.assertEqual('Command ID: 4Message ID: Checksum: 12Rotate Grid Degrees: -270', communicator.lastresult)

    def testplaceCubes(self):
        communicator = uartcomunicatorSpy()
        builder = buildalgorithm(communicator)

        builder.placeCubes([[False, False, False, False]])
        self.assertIsNone(communicator.lastresult)

        builder.placeCubes([False, True, True, True])
        self.assertEqual('Command ID: 5Message ID: Checksum: 12Place Cubes - Red: 1, Yellow: 1, Blue: 1', communicator.lastresult)

        builder.placeCubes([True, True, True, True])
        self.assertEqual('Command ID: 5Message ID: Checksum: 12Place Cubes - Red: 1, Yellow: 1, Blue: 1', communicator.lastresult)

        builder.placeCubes([False, False, True, False])
        self.assertEqual('Command ID: 5Message ID: Checksum: 12Place Cubes - Red: 0, Yellow: 1, Blue: 0', communicator.lastresult)

        builder.placeCubes([False, True, False, True])
        self.assertEqual('Command ID: 5Message ID: Checksum: 12Place Cubes - Red: 1, Yellow: 0, Blue: 1', communicator.lastresult)

        builder.rotateTimes(2)
        builder.placeCubes([True, False, False, False])
        self.assertEqual('Command ID: 5Message ID: Checksum: 12Place Cubes - Red: 0, Yellow: 1, Blue: 0', communicator.lastresult)

        builder.placeCubes([False, True, False, False])
        self.assertEqual('Command ID: 5Message ID: Checksum: 12Place Cubes - Red: 0, Yellow: 0, Blue: 1', communicator.lastresult)

        builder.placeCubes([False, False, False, True])
        self.assertEqual('Command ID: 5Message ID: Checksum: 12Place Cubes - Red: 1, Yellow: 0, Blue: 0', communicator.lastresult)

    def test_arrayfalsetest(self):
        self.assertFalse(buildalgorithm.arrayFalseCheck([True, True, True, True]))
        self.assertFalse(buildalgorithm.arrayFalseCheck([False, True, False, False]))
        self.assertTrue(buildalgorithm.arrayFalseCheck([False, False, False, False]))

    def test_match(self):
        communicator = uartcomunicatorSpy()
        builder = buildalgorithm(communicator)

        self.assertEqual([False, False, False, False], builder.match(True))
        builder.rotateTimes(1)
        self.assertEqual([True, True, False, False], builder.match(True))
        builder.rotateTimes(1)
        self.assertEqual([False, False, True, True], builder.match(True))

    def test_update(self):
        communicator = uartcomunicatorSpy()
        builder = buildalgorithm(communicator)

        builder.updatePlaced(True, [True, True, True, True])
        self.assertEqual([True, True, True, True, False, False, False, False], builder.placed)
        self.assertFalse(builder.fullplacedCheck(False))
        self.assertTrue(builder.fullplacedCheck(True))
        builder.updatePlaced(False, [True, True, True, True])
        self.assertEqual([True, True, True, True, True, True, True, True], builder.placed)
        self.assertTrue(builder.fullplacedCheck(True))
        self.assertTrue(builder.fullplacedCheck(False))



if __name__ == '__main__':
    unittest.main()