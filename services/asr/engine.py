from faster_whisper import WhisperModel
from pathlib import Path

class ASREngine:
    def __init__(self, model_size: str = "small", device: str = "cpu", compute_type: str = "int8"):
        # model_size: tiny, base, small, medium, large-v3
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe_file(self, audio_path: str, language: str = "es") -> dict:
        path = Path(audio_path)
        if not path.exists():
            raise FileNotFoundError(audio_path)
        segments, info = self.model.transcribe(str(path), language=language, vad_filter=True)
        text = " ".join(seg.text for seg in segments).strip()
        return {"text": text, "duration": info.duration}
