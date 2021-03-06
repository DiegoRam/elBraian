import unittest
from braianDriver.motor import MotorDC
class TestMotors(unittest.TestCase):
    def test_motor_creation(self):
        gpio = "gpio"
        pin_set_left, pin_set_right = ((12,13),(17,18))
        testMotor = MotorDC(gpio, pin_set_left, pin_set_right)
        self.assertEqual(testMotor.gpio, gpio)
        self.assertEqual(testMotor.pin_set_left, pin_set_left)
        self.assertEqual(testMotor.pin_set_right, (17,18))

if __name__ == '__main__':
    unittest.main()
