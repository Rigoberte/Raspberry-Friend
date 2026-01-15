import cv2
import threading
from typing import Callable, Optional
from src.domain.ports.outbound.camera_ports import CameraPort

CAMERA_INDEX = 0  # Default camera index

class OpenCVCameraAdapter(CameraPort):
    """
    Camera adapter implementation using OpenCV.
    Handles camera capture and display in a separate thread.
    Supports frame callbacks for GUI integration.
    """
    
    def __init__(self):
        self.camera = None
        self.is_running = False
        self.camera_thread = None
        self.window_name = "Raspberry Friend - Camera"
        self.frame_callback: Optional[Callable] = None
        self.clear_callback: Optional[Callable] = None
    
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
            self.camera = cv2.VideoCapture(CAMERA_INDEX)
            
            if not self.camera.isOpened():
                return {
                    "success": False,
                    "error-message": "Failed to open camera"
                }
            
            self.is_running = True
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
            
            if self.camera is not None:
                self.camera.release()
                self.camera = None
            
            cv2.destroyAllWindows()
            
            # Llamar al callback de limpieza si existe
            if self.clear_callback is not None:
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
        try:
            test_camera = cv2.VideoCapture(CAMERA_INDEX)
            is_available = test_camera.isOpened()
            test_camera.release()
            return is_available
        except Exception:
            return False
    
    def set_frame_callback(self, callback: Optional[Callable]) -> None:
        """
        Set a callback function to receive camera frames.
        
        Args:
            callback: Function that accepts a frame (numpy array) or None to disable
        """
        self.frame_callback = callback
    
    def set_clear_callback(self, callback: Optional[Callable]) -> None:
        """
        Set a callback function to be called when camera stops.
        
        Args:
            callback: Function to call when camera stops or None to disable
        """
        self.clear_callback = callback
    
    def __display_camera_feed__(self):
        """
        Internal method to display camera feed in real-time.
        Runs in a separate thread.
        Sends frames to the callback if one is set, otherwise displays in window.
        """
        while self.is_running:
            try:
                ret, frame = self.camera.read()
                
                if not ret:
                    break
                
                # Send frame to callback if one is set
                if self.frame_callback is not None:
                    try:
                        self.frame_callback(frame)
                    except Exception as e:
                        print(f"Error in frame callback: {str(e)}")
                else:
                    # Fallback: Display in window if no callback
                    cv2.imshow(self.window_name, frame)
                
                # Check for 'q' key with small delay (when using window display)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.is_running = False
                    break
            
            except Exception as e:
                print(f"Error in camera feed: {str(e)}")
                break
        
        # Cleanup
        if self.camera is not None:
            self.camera.release()
        cv2.destroyAllWindows()
