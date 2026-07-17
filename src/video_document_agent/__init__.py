"""Video Document Agent package."""

def _load_dotenv() -> None:
    import os
    from pathlib import Path
    cwd = Path.cwd()
    for directory in (cwd, *cwd.parents):
        dotenv_path = directory / ".env"
        if dotenv_path.is_file():
            try:
                for line in dotenv_path.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, val = line.split("=", 1)
                        val = val.strip()
                        if val.startswith(('"', "'")) and val.endswith(val[0]):
                            val = val[1:-1]
                        os.environ.setdefault(key.strip(), val)
                break
            except Exception:
                pass

_load_dotenv()

from .pipeline import PipelineConfig, VideoDocumentPipeline

__all__ = ["PipelineConfig", "VideoDocumentPipeline"]

