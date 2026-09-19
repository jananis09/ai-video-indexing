import cv2
import os


def detect_scenes(video_path, threshold=35):
    """
    Detect major scene changes in a video.

    Returns:
        List containing:
        - timestamp
        - frame
        - preview_path
        - score
    """

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return []

    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 30

    scenes = []
    previous_frame = None
    frame_number = 0

    # Create output folder
    os.makedirs("output", exist_ok=True)

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        # Process every 10th frame
        if frame_number % 10 != 0:
            frame_number += 1
            continue

        # Resize frame
        small_frame = cv2.resize(
            frame,
            (320, 240)
        )

        # Convert to grayscale
        gray = cv2.cvtColor(
            small_frame,
            cv2.COLOR_BGR2GRAY
        )

        if previous_frame is not None:

            difference = cv2.absdiff(
                previous_frame,
                gray
            )

            # Calculate scene change score
            score = difference.mean()

            # Detect scene change
            if score > threshold:

                timestamp = frame_number / fps

                # Keep at least 2 seconds between scenes
                if (
                    not scenes
                    or timestamp
                    - scenes[-1]["timestamp"] >= 2
                ):

                    scene_number = len(scenes) + 1

                    # Save preview image
                    preview_path = (
                        f"output/scene_{scene_number}.jpg"
                    )

                    cv2.imwrite(
                        preview_path,
                        frame
                    )

                    scenes.append({
                        "timestamp": timestamp,
                        "frame": frame_number,
                        "preview_path": preview_path,
                        "score": round(score, 2)
                    })

        previous_frame = gray

        frame_number += 1

    cap.release()

    return scenes