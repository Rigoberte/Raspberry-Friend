class FaceTracker:
    """
    Encapsulates the face tracking algorithm.

    Given the center of the camera frame and the center of a detected face,
    calculates the required servo angles to keep the face centered.
    Uses a deadzone to reduce servo jitter and unnecessary movement.
    """

    # Frame center (640x480 resolution)
    CENTER_X: int = 640 // 2
    CENTER_Y: int = 480 // 2

    def calculate_error_from_face_center(self, 
            face_x: int, face_y: int, 
            face_w: int, face_h: int
        ) -> tuple[float, float]:
        """
        Calculate servo angles to center a detected face.

        Args:
            face_x: Face bounding box X coordinate
            face_y: Face bounding box Y coordinate
            face_w: Face bounding box width
            face_h: Face bounding box height

        Returns:
            Tuple of (new_pan, new_tilt) angles (0-180 degrees)
        """
        # Calculate face center
        face_center_x = face_x + (face_w // 2)
        face_center_y = face_y + (face_h // 2)

        # Calculate error (distance from frame center)
        error_x = self.CENTER_X - face_center_x
        error_y = self.CENTER_Y - face_center_y


        return error_x, error_y