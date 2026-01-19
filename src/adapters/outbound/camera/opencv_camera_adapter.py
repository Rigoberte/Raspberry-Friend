import cv2
import threading
import time
from typing import Callable, Optional
from src.domain.ports.outbound.camera_ports import CameraPort

CAMERA_INDEX = 1  # Default camera index

class OpenCVCameraAdapter(CameraPort):
    """
    Camera adapter implementation using OpenCV.
    Handles camera capture and display in a separate thread.
    Supports frame callbacks for GUI integration.
    """
    
    def __init__(self):
        self.camera = None
        self.is_running = False
        self.is_tracking = False
        self.camera_thread = None
        self.window_name = "Raspberry Friend - Camera"
        self.view_callback: Optional[Callable] = None  # GUI/frame consumer
        self.clear_callback: Optional[Callable] = None
        self.face_cascade = None
        self.thread_stopped = threading.Event()  # Signal when thread has fully stopped
        self.thread_stopped.set()  # Initially stopped
        
        # Optimización para Raspberry Pi: frame skipping
        self.frame_skip = 2  # Procesar cada 3er frame (30fps -> 10fps)
        self.frame_counter = 0
        self.target_fps = 10  # FPS objetivo para GUI (conservar energía)
        self.frame_time = 1.0 / self.target_fps  # ~100ms entre frames
    
    def track_my_face(self) -> dict[str, str | bool]:
        """
        Enable face tracking without restarting the camera.
        Uses Haar cascade for lightweight face detection.

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
            if self.face_cascade is None:
                cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                self.face_cascade = cv2.CascadeClassifier(cascade_path)

            if self.face_cascade is None or self.face_cascade.empty():
                return {
                    "success": False,
                    "error-message": "Failed to load face detection model"
                }

            self.is_tracking = True
            self.window_name = "Raspberry Friend - Face Tracking"

            return {"success": True, "error-message": ""}
        except Exception as exc:  # noqa: BLE001
            self.is_tracking = False
            return {
                "success": False,
                "error-message": f"Error enabling face tracking: {exc}"
            }

    def untrack_my_face(self) -> dict[str, str | bool]:
        """Disable face tracking while keeping camera on."""
        self.is_tracking = False
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
            
            time.sleep(0.3)
            
            self.camera = cv2.VideoCapture(CAMERA_INDEX)
            
            if not self.camera.isOpened():
                return {
                    "success": False,
                    "error-message": "Failed to open camera"
                }
            
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
            if self.camera is not None:
                try:
                    self.camera.release()
                except Exception as e:
                    print(f"Error releasing camera: {e}")
                self.camera = None

            # Wait for capture thread to finish
            if self.camera_thread is not None and self.camera_thread.is_alive():
                self.camera_thread.join(timeout=1.0)
            self.camera_thread = None
            
            # Extra delay for MSMF handles to fully release on Windows
            time.sleep(1.0)
            
            cv2.destroyAllWindows()
            
            # Llamar al callback de limpieza si existe (clear GUI display)
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
        """Set a callback function to receive processed frames (GUI)."""
        self.view_callback = callback
    
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
        Optimized for Raspberry Pi with frame skipping and throttling.
        """
        import time as time_module
        
        last_frame_time = time_module.time()
        
        try:
            while self.is_running and self.camera is not None:
                try:
                    ret, frame = self.camera.read()
                    
                    if not ret or self.camera is None:
                        break
                    
                    self.frame_counter += 1
                    
                    # Frame skipping: procesar cada N frames (reduce CPU en RPi)
                    if self.frame_counter % (self.frame_skip + 1) != 0:
                        continue
                    
                    # Throttle a target_fps: no enviar frames más rápido que lo necesario
                    current_time = time_module.time()
                    elapsed = current_time - last_frame_time
                    if elapsed < self.frame_time:
                        time_module.sleep(self.frame_time - elapsed)
                        current_time = time_module.time()
                    
                    last_frame_time = current_time
                    
                    # Apply tracking overlay if enabled (solo si se procesa el frame)
                    if self.is_tracking and self.face_cascade is not None:
                        frame = self.__annotate_faces__(frame)

                    # Send frame to GUI callback if set
                    if self.view_callback is not None:
                        try:
                            self.view_callback(frame)
                        except Exception as e:
                            print(f"Error in frame callback: {str(e)}")
                    # If no callback, drop frame to avoid creating external windows
                
                except Exception as e:
                    print(f"Error in camera feed: {str(e)}")
                    break
        finally:
            # Signal that thread has finished
            self.thread_stopped.set()
            # Final cleanup
            try:
                if self.camera is not None:
                    self.camera.release()
                    self.camera = None
            except Exception:
                pass

    def __annotate_faces__(self, frame):
        """Detect faces in the frame and render bounding boxes."""
        if not self.is_tracking:
            return frame

        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.2,
                minNeighbors=5,
                minSize=(60, 60),
            )

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        except Exception as exc:  # noqa: BLE001
            print(f"Error in face tracking: {exc}")
        return frame
