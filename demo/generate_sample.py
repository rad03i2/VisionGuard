"""
Sample generator script. Creates a test MP4 video with simulated pedestrians and vehicles
for benchmarking VisionGuard without requiring external RTSP cameras or webcams.
"""

import os
import cv2
import numpy as np

def generate_sample_cctv_video(output_path: str = "demo/sample_surveillance.mp4", duration_sec: int = 10, fps: int = 30):
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    width, height = 1280, 720
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    total_frames = duration_sec * fps
    print(f"Generating {total_frames} test CCTV surveillance frames to [{output_path}]...")

    x1, y1 = 150.0, 300.0
    vx1, vy1 = 3.5, 0.8

    x2, y2 = 900.0, 450.0
    vx2, vy2 = -4.0, -1.0

    for f in range(total_frames):
        # Dark asphalt / floor background
        frame = np.full((height, width, 3), 35, dtype=np.uint8)

        # Draw parking lot / floor markers
        for x in range(200, width - 200, 150):
            cv2.line(frame, (x, 150), (x + 80, height - 100), (70, 70, 70), 2)

        # Entity 1: Person moving rightwards into restricted zone
        x1 += vx1
        y1 += vy1
        if x1 > width - 150 or x1 < 100:
            vx1 *= -1

        cv2.rectangle(frame, (int(x1), int(y1)), (int(x1 + 60), int(y1 + 130)), (50, 180, 50), -1)
        cv2.circle(frame, (int(x1 + 30), int(y1 + 25)), 18, (70, 220, 70), -1)

        # Entity 2: Vehicle moving leftwards
        x2 += vx2
        y2 += vy2
        if x2 < 100 or x2 > width - 250:
            vx2 *= -1

        cv2.rectangle(frame, (int(x2), int(y2)), (int(x2 + 180), int(y2 + 90)), (180, 100, 40), -1)

        # Timestamp banner
        cv2.putText(frame, f"CAM-TEST-FEED [REC] FRAME {f+1}/{total_frames}", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        out.write(frame)

    out.release()
    print("Sample CCTV test video generated successfully!")

if __name__ == "__main__":
    generate_sample_cctv_video()
