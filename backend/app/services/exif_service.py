"""
EXIF Metadata Extraction Service
009-mvp-gap-closure - US11 (FR-038)

Extracts EXIF metadata from images including:
- GPS coordinates
- DateTime (capture time)
- Camera model

Used for evidence uploaded by detectives to capture location/time data.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple, BinaryIO
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


@dataclass
class GpsCoordinates:
    """GPS coordinate data"""
    latitude: float
    longitude: float
    altitude: Optional[float] = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude
        }


@dataclass
class ExifData:
    """Extracted EXIF metadata"""
    gps: Optional[GpsCoordinates] = None
    datetime_original: Optional[datetime] = None
    datetime_digitized: Optional[datetime] = None
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    software: Optional[str] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None
    orientation: Optional[int] = None
    flash: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        result = {}

        if self.gps:
            result["gps"] = self.gps.to_dict()

        if self.datetime_original:
            result["datetime_original"] = self.datetime_original.isoformat()

        if self.datetime_digitized:
            result["datetime_digitized"] = self.datetime_digitized.isoformat()

        if self.camera_make:
            result["camera_make"] = self.camera_make

        if self.camera_model:
            result["camera_model"] = self.camera_model

        if self.software:
            result["software"] = self.software

        if self.image_width:
            result["image_width"] = self.image_width

        if self.image_height:
            result["image_height"] = self.image_height

        if self.orientation:
            result["orientation"] = self.orientation

        if self.flash:
            result["flash"] = self.flash

        return result

    def has_location(self) -> bool:
        """Check if GPS data is available"""
        return self.gps is not None

    def has_datetime(self) -> bool:
        """Check if datetime data is available"""
        return self.datetime_original is not None or self.datetime_digitized is not None

    def get_capture_time(self) -> Optional[datetime]:
        """Get the capture time (prefer original over digitized)"""
        return self.datetime_original or self.datetime_digitized


class ExifService:
    """Service for extracting EXIF metadata from images"""

    # EXIF tag names to extract
    EXIF_TAGS_TO_EXTRACT = {
        "DateTimeOriginal": "datetime_original",
        "DateTimeDigitized": "datetime_digitized",
        "Make": "camera_make",
        "Model": "camera_model",
        "Software": "software",
        "ImageWidth": "image_width",
        "ImageLength": "image_height",  # ImageLength is height
        "Orientation": "orientation",
        "Flash": "flash",
    }

    def __init__(self):
        pass

    def extract_from_file(self, file_path: str) -> Optional[ExifData]:
        """
        Extract EXIF data from an image file path.

        Args:
            file_path: Path to the image file

        Returns:
            ExifData object or None if extraction fails
        """
        try:
            with Image.open(file_path) as img:
                return self._extract_from_image(img)
        except Exception:
            return None

    def extract_from_bytes(self, file_bytes: BinaryIO) -> Optional[ExifData]:
        """
        Extract EXIF data from file-like object (bytes).

        Args:
            file_bytes: File-like object containing image data

        Returns:
            ExifData object or None if extraction fails
        """
        try:
            with Image.open(file_bytes) as img:
                return self._extract_from_image(img)
        except Exception:
            return None

    def _extract_from_image(self, img: Image.Image) -> Optional[ExifData]:
        """
        Extract EXIF data from a PIL Image object.

        Args:
            img: PIL Image object

        Returns:
            ExifData object or None if no EXIF data
        """
        exif_data = img._getexif()
        if not exif_data:
            return None

        # Decode EXIF tags
        decoded_exif = {}
        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, tag_id)
            decoded_exif[tag_name] = value

        # Extract standard tags
        result = ExifData()

        # Extract datetime fields
        for tag_name, attr_name in self.EXIF_TAGS_TO_EXTRACT.items():
            if tag_name in decoded_exif:
                value = decoded_exif[tag_name]

                if "DateTime" in tag_name:
                    # Parse datetime string
                    parsed_dt = self._parse_exif_datetime(value)
                    setattr(result, attr_name, parsed_dt)
                elif isinstance(value, (int, float, str)):
                    setattr(result, attr_name, value)

        # Extract GPS info
        if "GPSInfo" in decoded_exif:
            gps_info = decoded_exif["GPSInfo"]
            gps_coords = self._parse_gps_info(gps_info)
            if gps_coords:
                result.gps = gps_coords

        return result

    def _parse_exif_datetime(self, dt_string: str) -> Optional[datetime]:
        """
        Parse EXIF datetime string.

        EXIF datetime format: "YYYY:MM:DD HH:MM:SS"

        Args:
            dt_string: EXIF datetime string

        Returns:
            datetime object or None if parsing fails
        """
        if not dt_string or not isinstance(dt_string, str):
            return None

        try:
            # Standard EXIF format
            return datetime.strptime(dt_string, "%Y:%m:%d %H:%M:%S")
        except ValueError:
            try:
                # Try ISO format as fallback
                return datetime.fromisoformat(dt_string)
            except ValueError:
                return None

    def _parse_gps_info(self, gps_info: dict) -> Optional[GpsCoordinates]:
        """
        Parse GPS info from EXIF data.

        GPS data structure:
        - GPSLatitude: (degrees, minutes, seconds)
        - GPSLatitudeRef: 'N' or 'S'
        - GPSLongitude: (degrees, minutes, seconds)
        - GPSLongitudeRef: 'E' or 'W'
        - GPSAltitude: altitude value
        - GPSAltitudeRef: 0 (above sea level) or 1 (below)

        Args:
            gps_info: Raw GPS info dictionary from EXIF

        Returns:
            GpsCoordinates object or None if parsing fails
        """
        if not gps_info:
            return None

        # Decode GPS tags
        decoded_gps = {}
        for tag_id, value in gps_info.items():
            tag_name = GPSTAGS.get(tag_id, tag_id)
            decoded_gps[tag_name] = value

        # Extract latitude
        lat = self._get_gps_coordinate(
            decoded_gps.get("GPSLatitude"),
            decoded_gps.get("GPSLatitudeRef", "N")
        )

        # Extract longitude
        lon = self._get_gps_coordinate(
            decoded_gps.get("GPSLongitude"),
            decoded_gps.get("GPSLongitudeRef", "E")
        )

        if lat is None or lon is None:
            return None

        # Extract altitude (optional)
        altitude = None
        if "GPSAltitude" in decoded_gps:
            alt_value = decoded_gps["GPSAltitude"]
            if isinstance(alt_value, tuple):
                altitude = float(alt_value[0]) / float(alt_value[1])
            else:
                altitude = float(alt_value)

            # Handle altitude reference (0 = above sea level, 1 = below)
            if decoded_gps.get("GPSAltitudeRef") == 1:
                altitude = -altitude

        return GpsCoordinates(
            latitude=lat,
            longitude=lon,
            altitude=altitude
        )

    def _get_gps_coordinate(
        self,
        dms: Optional[Tuple],
        ref: str
    ) -> Optional[float]:
        """
        Convert GPS degrees/minutes/seconds to decimal degrees.

        Args:
            dms: Tuple of (degrees, minutes, seconds) where each is a tuple (num, denom)
            ref: Reference ('N', 'S', 'E', or 'W')

        Returns:
            Decimal degrees as float, or None if invalid
        """
        if not dms or len(dms) < 3:
            return None

        try:
            # Extract degree/minute/second values
            # Each can be a tuple (numerator, denominator) or IFDRational
            degrees = self._rational_to_float(dms[0])
            minutes = self._rational_to_float(dms[1])
            seconds = self._rational_to_float(dms[2])

            if degrees is None or minutes is None or seconds is None:
                return None

            # Convert to decimal degrees
            decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)

            # Apply reference (negative for South or West)
            if ref in ('S', 'W'):
                decimal = -decimal

            return decimal
        except (TypeError, ValueError, IndexError):
            return None

    def _rational_to_float(self, value) -> Optional[float]:
        """
        Convert EXIF rational value to float.

        EXIF rational can be:
        - A tuple (numerator, denominator)
        - IFDRational object with numerator/denominator attributes
        - Already a float/int

        Args:
            value: EXIF rational value

        Returns:
            Float value or None if conversion fails
        """
        if value is None:
            return None

        try:
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, tuple) and len(value) == 2:
                if value[1] == 0:
                    return None
                return float(value[0]) / float(value[1])
            elif hasattr(value, 'numerator') and hasattr(value, 'denominator'):
                # IFDRational object
                if value.denominator == 0:
                    return None
                return float(value.numerator) / float(value.denominator)
            else:
                return float(value)
        except (TypeError, ValueError):
            return None


def extract_exif_metadata(file_path: str) -> Optional[dict]:
    """
    Convenience function to extract EXIF metadata from a file.

    Args:
        file_path: Path to the image file

    Returns:
        Dictionary with EXIF data or None if extraction fails
    """
    service = ExifService()
    exif_data = service.extract_from_file(file_path)
    if exif_data:
        return exif_data.to_dict()
    return None
