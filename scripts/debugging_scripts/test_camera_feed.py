import cv2

def test_camera(index):
    cap = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)  # macOS-specific backend
    if not cap.isOpened():
        print(f"Camera index {index} failed to open.")
        return
    print(f"Camera index {index} opened successfully.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow(f'Camera {index}', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

for i in range(3):  # test 0, 1, 2
    print(f"\n=== Testing Camera Index {i} ===")
    test_camera(i)