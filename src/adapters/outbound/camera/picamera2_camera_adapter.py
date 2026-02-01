from typing import Callable, Optional
import threading
import cv2
import time
import os
from picamera2 import Picamera2

from src.domain.ports.outbound.camera_ports import CameraPort
from src.domain.models.pan_tilt_controller import PanTiltController

CAMERA_INDEX = 0  # Default camera index

class PiCameraAdapter(CameraPort):
    """
    Adapter for PiCamera using picamera2 library.

    Integrates with PanTiltController for camera orientation.
    """

    def __init__(self):
        """
        Initialize PiCamera adapter.

        Args:
            pan_tilt_controller: Optional[PanTiltController] = None
        """
        self.camera = None
        self.is_running = False
        self.is_tracking: bool = False
        self.camera_thread: Optional[threading.Thread] = None
        self.window_name: str = "Raspberry Friend - Camera"
        self.view_callback: Optional[Callable] = None  # GUI/frame consumer
        self.clear_callback: Optional[Callable] = None
        self.face_cascade = None
        self.thread_stopped = threading.Event()  # Signal when thread has fully stopped
        self.thread_stopped.set()  # Initially stopped
        
        # Pan/Tilt servo control
        self.pan_tilt_controller: PanTiltController = PanTiltController()
        self.key_callback: Optional[Callable] = None  # For keyboard input handling
        
        # Optimización para Raspberry Pi: frame skipping
        self.frame_skip: int = 2  # Procesar cada 3er frame (30fps -> 10fps)
        self.frame_counter: int = 0
        self.target_fps: int = 10  # FPS objetivo para GUI (conservar energía)
        self.frame_time: float = 1.0 / self.target_fps  # ~100ms entre frames

    def track_my_face(self) -> dict[str, str | bool]:
        """
        Enable face tracking without restarting the camera.
        Uses Haar cascade for lightweight face detection.
        Integrates pan/tilt servo control for automatic face following.

        Returns:
            dict with 'success' (bool) and 'error-message' (str) keys
        """
        # Auto-start camera if needed
        if not self.is_running:
            start_result = self.start_camera()
            if not start_result.get("success", False):
                return {
                    "success": False,
                    "error-message": start_result.get("error-message", "Failed to start camera")
                }

        if self.is_tracking:
            return {"success": True, "error-message": ""}

        try:
            # Load Haar cascade if not already loaded
            if self.face_cascade is None:
                cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                self.face_cascade = cv2.CascadeClassifier(cascade_path)
                
                if self.face_cascade.empty():
                    return {"success": False, "error-message": "Failed to load face cascade"}
            
            # Enable tracking mode
            self.is_tracking = True
            self.window_name = "Raspberry Friend - Face Tracking"
            
            # Set pan/tilt controller to auto mode
            self.pan_tilt_controller.set_auto_mode()
            
            return {"success": True, "error-message": ""}
            
        except Exception as exc:
            return {"success": False, "error-message": f"Failed to enable face tracking: {exc}"}


    def untrack_my_face(self) -> dict[str, str | bool]:
        """
        Disable face tracking while keeping camera on.
        Switches pan/tilt controller back to manual mode if available.
        """
        self.is_tracking = False
        
        # Switch back to manual mode if pan/tilt controller is available
        self.pan_tilt_controller.set_manual_mode()
        
        self.window_name = "Raspberry Friend - Camera"
        return {"success": True, "error-message": ""}
    
    def start_camera(self) -> dict[str, str | bool]:
        """
        Start the camera and display it in real-time in a separate thread.
        
        Returns:
            dict with 'success' (bool) and 'error-message' (str) keys
        """
        if not self.is_camera_available():
            return {
                "success": False,
                "error-message": "No camera detected or camera is not available"
            }
        
        if self.is_running:
            return {
                "success": False,
                "error-message": "Camera is already running"
            }
        
        try:
            # Ensure previous thread is fully cleaned up before reopening
            if not self.thread_stopped.is_set():
                self.thread_stopped.wait(timeout=2.0)

            if self.camera:
                try:
                    self.camera.stop()
                    self.camera.close()
                except Exception:
                    pass
            
            time.sleep(0.3)
            
            self.camera = Picamera2()
            camera_config = self.camera.create_preview_configuration(main={"format": 'BGR888', "size": (640, 480)})
            self.camera.configure(camera_config)
            self.camera.start()
            
            self.is_running = True
            self.thread_stopped.clear()  # Mark thread as not stopped
            self.camera_thread = threading.Thread(target=self.__display_camera_feed__, daemon=True)
            self.camera_thread.start()
            
            return {
                "success": True,
                "error-message": ""
            }
        except Exception as e:
            return {
                "success": False,
                "error-message": f"Error starting camera: {str(e)}"
            }
    
    def stop_camera(self) -> dict[str, str | bool]:
        """
        Stop the camera and close the display window.
        
        Returns:
            dict with 'success' (bool) and 'error-message' (str) keys
        """
        try:
            self.is_running = False
            self.is_tracking = False
            # DO NOT clear callback - it will be reused on restart
            self.window_name = "Raspberry Friend - Camera"
            
            # Wait for thread to stop reading before releasing camera
            if not self.thread_stopped.wait(timeout=2.5):
                print("Warning: Camera thread did not stop in time")
            
            # Now safe to release camera
            if self.camera:
                try:
                    self.camera.stop()
                    self.camera.close()
                except Exception as e:
                    print(f"Error releasing camera: {e}")
                self.camera = None

            # Wait for capture thread to finish
            if self.camera_thread and self.camera_thread.is_alive():
                self.camera_thread.join(timeout=1.0)
            self.camera_thread = None
            
            # Extra delay for MSMF handles to fully release on Windows
            time.sleep(1.0)
            
            cv2.destroyAllWindows()
            
            # Llamar al callback de limpieza si existe (clear GUI display)
            if self.clear_callback:
                try:
                    self.clear_callback()
                except Exception as e:
                    print(f"Error in clear callback: {str(e)}")
            
            return {
                "success": True,
                "error-message": ""
            }
        except Exception as e:
            return {
                "success": False,
                "error-message": f"Error stopping camera: {str(e)}"
            }
    
    def is_camera_available(self) -> bool:
        """
        Check if camera is available and connected.
        
        Returns:
            True if camera is available, False otherwise
        """
        if self.is_running:
            return True  # Already running
        
        return os.path.exists("/dev/video0") or os.path.exists("/dev/media0")
    
    def set_frame_callback(self, callback: Optional[Callable]) -> None:
        """Set a callback function to receive processed frames (GUI)."""
        self.view_callback = callback
    
    def set_clear_callback(self, callback: Optional[Callable]) -> None:
        """
        Set a callback function to be called when camera stops.
        
        Args:
            callback: Function to call when camera stops or None to disable
        """
        self.clear_callback = callback
    
    def set_key_callback(self, callback: Optional[Callable]) -> None: # TODO: Creo que no se usa
        """
        Set a callback function to handle keyboard input.
        
        Callback receives key codes (from cv2.waitKey).
        
        Args:
            callback: Function that accepts key code (int) or None to disable
        """
        self.key_callback = callback
    
    def handle_keyboard_input(self, key: int) -> None:
        """
        Handle keyboard input for manual servo control.
        
        - SPACE: Toggle between manual and auto tracking modes
        - W: Move tilt up
        - S: Move tilt down
        - A: Move pan left
        - D: Move pan right
        
        Args:
            key: Key code from cv2.waitKey()
        """
        # Space: toggle tracking mode
        if key == ord(' '):
            if self.pan_tilt_controller.is_manual_mode():
                self._toggle_face_tracking()
            else:
                self.untrack_my_face()
        # Manual control keys (only in manual mode)
        elif self.pan_tilt_controller.is_manual_mode():
            if key == ord('w'):
                self.pan_tilt_controller.move_tilt_up()
            elif key == ord('s'):
                self.pan_tilt_controller.move_tilt_down()
            elif key == ord('a'):
                self.pan_tilt_controller.move_pan_left()
            elif key == ord('d'):
                self.pan_tilt_controller.move_pan_right()
    
    def _toggle_face_tracking(self) -> None:
        """Toggle face tracking on/off."""
        if self.is_tracking:
            self.untrack_my_face()
        else:
            self.track_my_face()
    
    def __display_camera_feed__(self):
        """
        Internal method to display camera feed in real-time.
        Runs in a separate thread.
        Sends frames to the callback if one is set, otherwise displays in window.
        Optimized for Raspberry Pi with frame skipping and throttling.
        """
        
        try:
            while self.is_running:
                frame_start = time.time()
                
                # Capture frame from PiCamera
                frame = self.camera.capture_array()
                
                # Convert RGB to BGR for OpenCV processing
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                # Frame skipping for performance optimization
                self.frame_counter += 1
                should_process = (self.frame_counter % (self.frame_skip + 1)) == 0
                
                if should_process:
                    # Process frame: detect faces and control servos if tracking
                    frame_bgr = self.__annotate_faces__(frame_bgr)
                
                # Send frame to GUI callback if available
                if self.view_callback is not None:
                    try:
                        self.view_callback(frame_bgr)
                    except Exception as e:
                        print(f"Error in view callback: {e}")
                
                # Frame rate limiting
                elapsed = time.time() - frame_start
                sleep_time = self.frame_time - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
        except Exception as e:
            print(f"Camera feed error: {e}")
        finally:
            self.thread_stopped.set()
            if self.clear_callback is not None:
                try:
                    self.clear_callback()
                except Exception:
                    pass

    def __annotate_faces__(self, frame):
        """
        Detect faces in the frame and render bounding boxes.
        If in auto tracking mode, automatically adjust pan/tilt servos.
        """
        if not self.is_tracking:
            return frame

        if self.face_cascade is None:
            return frame
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces with optimized parameters for Raspberry Pi
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(80, 80)
        )
        
        # Process each detected face
        for (x, y, w, h) in faces:
            # Draw rectangle around face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw center point of face
            center_x = x + w // 2
            center_y = y + h // 2
            cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)
            
            # If tracking is enabled, update servo positions
            if self.is_tracking:
                self.pan_tilt_controller.track_face(x, y, w, h)
                break
        
        # Draw tracking status on frame
        mode_text = "TRACKING: ON" if self.is_tracking else "TRACKING: OFF"
        color = (0, 255, 0) if self.is_tracking else (0, 0, 255)
        cv2.putText(frame, mode_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Draw deadzone rectangle (center of frame)
        frame_h, frame_w = frame.shape[:2]
        center_frame_x = frame_w // 2
        center_frame_y = frame_h // 2
        deadzone = 10  # pixels
        cv2.rectangle(
            frame,
            (center_frame_x - deadzone, center_frame_y - deadzone),
            (center_frame_x + deadzone, center_frame_y + deadzone),
            (255, 255, 255), 1
        )
        
        return frame