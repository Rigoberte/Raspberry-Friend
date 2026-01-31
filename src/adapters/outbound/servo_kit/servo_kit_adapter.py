from src.domain.ports.outbound.servo_kit_ports import ServoKitPort


class AdafruitServoKitAdapter(ServoKitPort):
    """
    Servo motor adapter using Adafruit ServoKit.
    Controls up to 16 servo motors via PCA9685 PWM driver.

    This adapter handles the hardware communication and angle constraints.
    It assumes the Adafruit servo kit library is installed and the hardware
    is properly connected to the Raspberry Pi via I2C.
    """
    MIN_ANGLE = 0
    MAX_ANGLE = 180
    DEFAULT_ANGLE = 90

    def __init__(self, port: int) -> None:
        """
        Initialize the servo kit adapter.

        Raises:
            Exception: If servo kit hardware is not available or initialization fails
        """
        self.port: int = port
        self.num_ports: int = 4

        if not 0 <= port < self.num_ports:
            raise ValueError(f"Invalid port: {port}. Valid range: 0-{self.num_ports - 1}")

        try:
            import adafruit_servokit

            self.kit = adafruit_servokit.ServoKit(channels=16)
            self.reset()
        except Exception as e:
            error_msg = f"Failed to initialize ServoKit: {str(e)}"
            raise RuntimeError(error_msg) from e
    
    def increase_angle(self) -> dict[str, str | bool]:
        return self.__set_angle__(self.get_angle()["angle"] + 5)
    
    def decrease_angle(self) -> dict[str, str | bool]:
        return self.__set_angle__(self.get_angle()["angle"] - 5)

    def get_angle(self) -> dict[str, float | str | bool]:
        try:
            angle = self.kit.servo[self.port].angle
            return {"angle": angle, "success": True, "error-message": ""}
        except Exception as e:
            return {
                "angle": 0,
                "success": False,
                "error-message": f"Error getting servo angle: {str(e)}"
            }

    def reset(self) -> dict[str, str | bool]:
        return self.__set_angle__(self.DEFAULT_ANGLE)

    def __set_angle__(self, angle: float) -> dict[str, str | bool]:
        try:
            # Constrain angle to valid range
            new_angle = max(self.MIN_ANGLE, min(angle, self.MAX_ANGLE))
            self.kit.servo[self.port].angle = new_angle
            return {"success": True, "error-message": ""}
        except Exception as e:
            return {
                "success": False,
                "error-message": f"Error setting servo angle: {str(e)}"
            }