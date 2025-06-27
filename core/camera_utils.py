import cv2

def capture_image(camera_index=0, window_name="Camera Preview"):
    """
    Captures a single frame from the webcam.

    Parameters:
        camera_index (int): Index of the camera to use (default is 0).
        window_name (str): Title of the OpenCV preview window.

    Returns:
        np.ndarray or None: Captured image frame, or None if cancelled.
    """
    cap = cv2.VideoCapture(camera_index, cv2.CAP_AVFOUNDATION)

    if not cap.isOpened():
        raise RuntimeError("Could not open camera.")

    print("Press space to capture an image, or Esc to cancel.")
    frame = None

    while True:
        ret, img = cap.read()
        if not ret:
            continue

        cv2.imshow(window_name, img)
        key = cv2.waitKey(1)

        if key == 27:  # ESC
            print("Capture cancelled.")
            break
        elif key == 32:  # SPACE
            print("Image captured.")
            frame = img.copy()
            break

    cap.release()
    cv2.destroyWindow(window_name)
    return frame