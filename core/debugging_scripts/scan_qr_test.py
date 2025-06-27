## Using: https://www.hbvcamera.com/13mp-camera-module/13mp-4k-pdaf-fast-auto-focus-usb2.0-camera-module-for-android-machine.html
import cv2

cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION) # use find_camera.py to determine which camera feed to use.
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Limit resolution to reduce demand on camera
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
detector = cv2.QRCodeDetector()
last_data = None
stable_counter = 0

print("Press 'q' in camera window to quit.")
while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera read failed.")
        break

    data, bbox, _ = detector.detectAndDecode(frame)

    if bbox is not None and len(bbox) > 0:
        bbox = bbox[0]
        for i in range(len(bbox)):
            pt1 = tuple(map(int, bbox[i]))
            pt2 = tuple(map(int, bbox[(i + 1) % len(bbox)]))
            cv2.line(frame, pt1, pt2, (255, 0, 0), 2)

        if data:
            if data != last_data:
                print(f"QR Detected: {data}")
            last_data = data
            stable_counter = 15  # Show overlay for 15 frames

    if stable_counter > 0:
        cv2.putText(frame, f"Detected: {last_data}", (40, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        stable_counter -= 1
    else:
        cv2.putText(frame, "No QR detected", (40, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

    cv2.imshow("QR Scanner", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()