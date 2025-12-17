"""
Parsers Module
Handles parsing of various file types: KakaoTalk, Text, PDF, Images, Audio
"""

from .base import BaseParser, Message, StandardMetadata

__all__ = ["BaseParser", "Message", "StandardMetadata"]

# Optional imports - these require additional dependencies
# noqa: F401 comments are used because these are re-exports for the public API
try:
    from .image_ocr import ImageOCRParser  # noqa: F401
    __all__.append("ImageOCRParser")
except ImportError:
    pass  # pytesseract not installed

try:
    from .image_vision import ImageVisionParser  # noqa: F401
    __all__.append("ImageVisionParser")
except ImportError:
    pass  # pytesseract or other deps not installed

try:
    from .pdf_parser import PDFParser  # noqa: F401
    __all__.append("PDFParser")
except ImportError:
    pass  # PyPDF2 not installed

try:
    from .audio_parser import AudioParser  # noqa: F401
    __all__.append("AudioParser")
except ImportError:
    pass  # openai not installed

try:
    from .video_parser import VideoParser  # noqa: F401
    __all__.append("VideoParser")
except ImportError:
    pass  # ffmpeg-python not installed

# V2 Parsers - Archived (not used in Lambda handler)
# Located in ./archive/ directory for future reference
# - kakaotalk_v2.py, pdf_parser_v2.py, audio_parser_v2.py, image_parser_v2.py
