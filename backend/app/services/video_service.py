import os
from typing import List, Tuple
from scenedetect import detect, ContentDetector


class VideoService:
    def __init__(self):
        pass

    def segment_video(self, video_path: str) -> List[Tuple[float, float]]:
        """
        Segments a video into scenes based on content changes.
        Returns a list of (start_time, end_time) tuples in seconds.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Use PySceneDetect to find scene boundaries
        scene_list = detect(video_path, ContentDetector())

        # Convert scene list to list of (start_seconds, end_seconds)
        segments = []
        for scene in scene_list:
            start_sec = scene[0].get_seconds()
            end_sec = scene[1].get_seconds()
            segments.append((start_sec, end_sec))

        return segments

    def extract_keyframes(
        self,
        video_path: str,
        segments: List[Tuple[float, float]],
        output_dir: str,
    ) -> List[str]:
        """
        Extracts keyframes from the first frame of each segment.
        Returns a list of paths to the saved keyframes.
        """
        import cv2

        os.makedirs(output_dir, exist_ok=True)

        cap = cv2.VideoCapture(video_path)
        keyframe_paths = []

        for i, (start_sec, _) in enumerate(segments):
            # Set position to start_sec
            cap.set(cv2.CAP_PROP_POS_MSEC, start_sec * 1000)
            ret, frame = cap.read()
            if ret:
                filename = f"keyframe_{i:04d}.jpg"
                path = os.path.join(output_dir, filename)
                cv2.imwrite(path, frame)
                keyframe_paths.append(path)

        cap.release()
        return keyframe_paths

    def analyze_keyframes(self, keyframe_paths: List[str]) -> List[str]:
        """
        Analyzes keyframes using LLaVA via Ollama.
        Returns a list of visual descriptions.
        """
        import base64
        import httpx
        from app.config import settings

        descriptions = []
        url = f"{settings.OLLAMA_BASE_URL}/api/generate"

        # Structural Prompt from MULTIMODAL_VISION.md
        prompt = (
            "Describe this scene precisely. Focus on: "
            "1. Main subjects and actions. "
            "2. Notable text, UI elements, or code. "
            "3. Environment and context."
        )

        for path in keyframe_paths:
            with open(path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode("utf-8")

            payload = {
                "model": settings.OLLAMA_VLM_MODEL,
                "prompt": prompt,
                "images": [img_data],
                "stream": False,
            }

            try:
                response = httpx.post(url, json=payload, timeout=60.0)
                response.raise_for_status()
                desc = response.json().get("response", "")
                descriptions.append(desc)
            except Exception as e:
                descriptions.append(f"Error analyzing frame: {str(e)}")

        return descriptions


_video_service = None


def get_video_service():
    global _video_service
    if _video_service is None:
        _video_service = VideoService()
    return _video_service
