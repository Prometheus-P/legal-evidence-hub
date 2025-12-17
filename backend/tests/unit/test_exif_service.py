"""
Unit Tests for EXIF Service
009-mvp-gap-closure - Issue #268

Tests for app/services/exif_service.py
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

from app.services.exif_service import (
    GpsCoordinates,
    ExifData,
    ExifService,
    extract_exif_metadata
)


class TestGpsCoordinates:
    """Test GpsCoordinates dataclass"""

    def test_to_dict_with_all_fields(self):
        """Test to_dict with all fields populated"""
        gps = GpsCoordinates(
            latitude=37.5665,
            longitude=126.9780,
            altitude=50.0
        )
        result = gps.to_dict()

        assert result["latitude"] == 37.5665
        assert result["longitude"] == 126.9780
        assert result["altitude"] == 50.0

    def test_to_dict_without_altitude(self):
        """Test to_dict without altitude"""
        gps = GpsCoordinates(latitude=35.6762, longitude=139.6503)
        result = gps.to_dict()

        assert result["latitude"] == 35.6762
        assert result["longitude"] == 139.6503
        assert result["altitude"] is None


class TestExifData:
    """Test ExifData dataclass"""

    def test_to_dict_with_all_fields(self):
        """Test to_dict with all fields populated"""
        gps = GpsCoordinates(latitude=37.5, longitude=126.9, altitude=10.0)
        exif = ExifData(
            gps=gps,
            datetime_original=datetime(2024, 1, 15, 10, 30, 0),
            datetime_digitized=datetime(2024, 1, 15, 10, 30, 0),
            camera_make="Apple",
            camera_model="iPhone 15 Pro",
            software="iOS 17.0",
            image_width=4032,
            image_height=3024,
            orientation=1,
            flash="No Flash"
        )

        result = exif.to_dict()

        assert "gps" in result
        assert result["gps"]["latitude"] == 37.5
        assert result["datetime_original"] == "2024-01-15T10:30:00"
        assert result["datetime_digitized"] == "2024-01-15T10:30:00"
        assert result["camera_make"] == "Apple"
        assert result["camera_model"] == "iPhone 15 Pro"
        assert result["software"] == "iOS 17.0"
        assert result["image_width"] == 4032
        assert result["image_height"] == 3024
        assert result["orientation"] == 1
        assert result["flash"] == "No Flash"

    def test_to_dict_with_minimal_fields(self):
        """Test to_dict with only some fields populated"""
        exif = ExifData(camera_make="Samsung", camera_model="Galaxy S24")
        result = exif.to_dict()

        assert "gps" not in result
        assert "datetime_original" not in result
        assert result["camera_make"] == "Samsung"
        assert result["camera_model"] == "Galaxy S24"

    def test_to_dict_empty(self):
        """Test to_dict with no fields populated"""
        exif = ExifData()
        result = exif.to_dict()

        assert result == {}

    def test_has_location_true(self):
        """Test has_location returns True when GPS exists"""
        gps = GpsCoordinates(latitude=37.5, longitude=126.9)
        exif = ExifData(gps=gps)

        assert exif.has_location() is True

    def test_has_location_false(self):
        """Test has_location returns False when no GPS"""
        exif = ExifData()

        assert exif.has_location() is False

    def test_has_datetime_with_original(self):
        """Test has_datetime with datetime_original"""
        exif = ExifData(datetime_original=datetime(2024, 1, 15, 10, 30, 0))

        assert exif.has_datetime() is True

    def test_has_datetime_with_digitized(self):
        """Test has_datetime with datetime_digitized only"""
        exif = ExifData(datetime_digitized=datetime(2024, 1, 15, 10, 30, 0))

        assert exif.has_datetime() is True

    def test_has_datetime_false(self):
        """Test has_datetime returns False when no datetime"""
        exif = ExifData()

        assert exif.has_datetime() is False

    def test_get_capture_time_prefers_original(self):
        """Test get_capture_time prefers datetime_original"""
        original = datetime(2024, 1, 15, 10, 0, 0)
        digitized = datetime(2024, 1, 15, 10, 5, 0)
        exif = ExifData(datetime_original=original, datetime_digitized=digitized)

        assert exif.get_capture_time() == original

    def test_get_capture_time_falls_back_to_digitized(self):
        """Test get_capture_time falls back to datetime_digitized"""
        digitized = datetime(2024, 1, 15, 10, 5, 0)
        exif = ExifData(datetime_digitized=digitized)

        assert exif.get_capture_time() == digitized

    def test_get_capture_time_returns_none(self):
        """Test get_capture_time returns None when no datetime"""
        exif = ExifData()

        assert exif.get_capture_time() is None


class TestExifService:
    """Test ExifService class"""

    @pytest.fixture
    def service(self):
        """Create ExifService instance"""
        return ExifService()

    def test_extract_from_file_success(self, service):
        """Test extract_from_file with valid image"""
        mock_img = MagicMock()
        mock_img._getexif.return_value = {
            271: "Apple",  # Make
            272: "iPhone 15",  # Model
        }

        with patch("app.services.exif_service.Image.open") as mock_open:
            mock_open.return_value.__enter__.return_value = mock_img

            result = service.extract_from_file("/path/to/image.jpg")

            assert result is not None
            assert result.camera_make == "Apple"
            assert result.camera_model == "iPhone 15"

    def test_extract_from_file_no_exif(self, service):
        """Test extract_from_file with image without EXIF"""
        mock_img = MagicMock()
        mock_img._getexif.return_value = None

        with patch("app.services.exif_service.Image.open") as mock_open:
            mock_open.return_value.__enter__.return_value = mock_img

            result = service.extract_from_file("/path/to/image.jpg")

            assert result is None

    def test_extract_from_file_exception(self, service):
        """Test extract_from_file with invalid file"""
        with patch("app.services.exif_service.Image.open") as mock_open:
            mock_open.side_effect = Exception("File not found")

            result = service.extract_from_file("/invalid/path.jpg")

            assert result is None

    def test_extract_from_bytes_success(self, service):
        """Test extract_from_bytes with valid image bytes"""
        mock_img = MagicMock()
        mock_img._getexif.return_value = {
            271: "Samsung",  # Make
            272: "Galaxy S24",  # Model
        }

        with patch("app.services.exif_service.Image.open") as mock_open:
            mock_open.return_value.__enter__.return_value = mock_img

            file_bytes = BytesIO(b"fake image data")
            result = service.extract_from_bytes(file_bytes)

            assert result is not None
            assert result.camera_make == "Samsung"
            assert result.camera_model == "Galaxy S24"

    def test_extract_from_bytes_exception(self, service):
        """Test extract_from_bytes with invalid data"""
        with patch("app.services.exif_service.Image.open") as mock_open:
            mock_open.side_effect = Exception("Invalid image")

            file_bytes = BytesIO(b"invalid data")
            result = service.extract_from_bytes(file_bytes)

            assert result is None

    def test_extract_from_image_with_datetime(self, service):
        """Test _extract_from_image extracts datetime fields"""
        mock_img = MagicMock()
        mock_img._getexif.return_value = {
            36867: "2024:01:15 10:30:00",  # DateTimeOriginal
            36868: "2024:01:15 10:30:05",  # DateTimeDigitized
        }

        result = service._extract_from_image(mock_img)

        assert result is not None
        assert result.datetime_original == datetime(2024, 1, 15, 10, 30, 0)
        assert result.datetime_digitized == datetime(2024, 1, 15, 10, 30, 5)

    def test_extract_from_image_with_gps(self, service):
        """Test _extract_from_image extracts GPS info"""
        mock_img = MagicMock()
        mock_img._getexif.return_value = {
            34853: {  # GPSInfo
                1: "N",  # GPSLatitudeRef
                2: ((37, 1), (33, 1), (59, 1)),  # GPSLatitude
                3: "E",  # GPSLongitudeRef
                4: ((126, 1), (58, 1), (41, 1)),  # GPSLongitude
            }
        }

        result = service._extract_from_image(mock_img)

        assert result is not None
        assert result.gps is not None
        # 37° 33' 59" N ≈ 37.566
        assert abs(result.gps.latitude - 37.566) < 0.01
        # 126° 58' 41" E ≈ 126.978
        assert abs(result.gps.longitude - 126.978) < 0.01

    def test_parse_exif_datetime_valid(self, service):
        """Test _parse_exif_datetime with valid EXIF format"""
        result = service._parse_exif_datetime("2024:01:15 10:30:00")

        assert result == datetime(2024, 1, 15, 10, 30, 0)

    def test_parse_exif_datetime_iso_format(self, service):
        """Test _parse_exif_datetime with ISO format fallback"""
        result = service._parse_exif_datetime("2024-01-15T10:30:00")

        assert result == datetime(2024, 1, 15, 10, 30, 0)

    def test_parse_exif_datetime_invalid(self, service):
        """Test _parse_exif_datetime with invalid format"""
        result = service._parse_exif_datetime("invalid datetime")

        assert result is None

    def test_parse_exif_datetime_none(self, service):
        """Test _parse_exif_datetime with None"""
        result = service._parse_exif_datetime(None)

        assert result is None

    def test_parse_exif_datetime_non_string(self, service):
        """Test _parse_exif_datetime with non-string value"""
        result = service._parse_exif_datetime(12345)

        assert result is None

    def test_parse_gps_info_valid(self, service):
        """Test _parse_gps_info with valid GPS data"""
        gps_info = {
            1: "N",  # GPSLatitudeRef
            2: ((37, 1), (30, 1), (0, 1)),  # GPSLatitude: 37° 30' 0"
            3: "E",  # GPSLongitudeRef
            4: ((127, 1), (0, 1), (0, 1)),  # GPSLongitude: 127° 0' 0"
        }

        result = service._parse_gps_info(gps_info)

        assert result is not None
        assert result.latitude == 37.5  # 37° 30' 0"
        assert result.longitude == 127.0  # 127° 0' 0"

    def test_parse_gps_info_with_altitude(self, service):
        """Test _parse_gps_info with altitude"""
        gps_info = {
            1: "N",
            2: ((37, 1), (30, 1), (0, 1)),
            3: "E",
            4: ((127, 1), (0, 1), (0, 1)),
            5: 0,  # GPSAltitudeRef: above sea level
            6: (100, 1),  # GPSAltitude: 100m
        }

        result = service._parse_gps_info(gps_info)

        assert result is not None
        assert result.altitude == 100.0

    def test_parse_gps_info_with_negative_altitude(self, service):
        """Test _parse_gps_info with below sea level altitude"""
        gps_info = {
            1: "N",
            2: ((37, 1), (30, 1), (0, 1)),
            3: "E",
            4: ((127, 1), (0, 1), (0, 1)),
            5: 1,  # GPSAltitudeRef: below sea level
            6: (50, 1),  # GPSAltitude: 50m below
        }

        result = service._parse_gps_info(gps_info)

        assert result is not None
        assert result.altitude == -50.0

    def test_parse_gps_info_south_west(self, service):
        """Test _parse_gps_info with South/West coordinates"""
        gps_info = {
            1: "S",  # South
            2: ((33, 1), (52, 1), (0, 1)),  # 33° 52' 0" S
            3: "W",  # West
            4: ((151, 1), (12, 1), (0, 1)),  # 151° 12' 0" W
        }

        result = service._parse_gps_info(gps_info)

        assert result is not None
        assert result.latitude < 0  # South is negative
        assert result.longitude < 0  # West is negative

    def test_parse_gps_info_empty(self, service):
        """Test _parse_gps_info with empty dict"""
        result = service._parse_gps_info({})

        assert result is None

    def test_parse_gps_info_none(self, service):
        """Test _parse_gps_info with None"""
        result = service._parse_gps_info(None)

        assert result is None

    def test_parse_gps_info_missing_latitude(self, service):
        """Test _parse_gps_info with missing latitude"""
        gps_info = {
            3: "E",
            4: ((127, 1), (0, 1), (0, 1)),
        }

        result = service._parse_gps_info(gps_info)

        assert result is None

    def test_get_gps_coordinate_valid(self, service):
        """Test _get_gps_coordinate with valid DMS"""
        dms = ((37, 1), (30, 1), (0, 1))  # 37° 30' 0"

        result = service._get_gps_coordinate(dms, "N")

        assert result == 37.5

    def test_get_gps_coordinate_south(self, service):
        """Test _get_gps_coordinate with South reference"""
        dms = ((33, 1), (0, 1), (0, 1))  # 33° 0' 0"

        result = service._get_gps_coordinate(dms, "S")

        assert result == -33.0

    def test_get_gps_coordinate_west(self, service):
        """Test _get_gps_coordinate with West reference"""
        dms = ((122, 1), (30, 1), (0, 1))  # 122° 30' 0"

        result = service._get_gps_coordinate(dms, "W")

        assert result == -122.5

    def test_get_gps_coordinate_none(self, service):
        """Test _get_gps_coordinate with None"""
        result = service._get_gps_coordinate(None, "N")

        assert result is None

    def test_get_gps_coordinate_short_tuple(self, service):
        """Test _get_gps_coordinate with too short tuple"""
        dms = ((37, 1), (30, 1))  # Missing seconds

        result = service._get_gps_coordinate(dms, "N")

        assert result is None

    def test_rational_to_float_int(self, service):
        """Test _rational_to_float with integer"""
        result = service._rational_to_float(42)

        assert result == 42.0

    def test_rational_to_float_float(self, service):
        """Test _rational_to_float with float"""
        result = service._rational_to_float(37.5)

        assert result == 37.5

    def test_rational_to_float_tuple(self, service):
        """Test _rational_to_float with tuple (num, denom)"""
        result = service._rational_to_float((100, 2))

        assert result == 50.0

    def test_rational_to_float_tuple_zero_denom(self, service):
        """Test _rational_to_float with zero denominator"""
        result = service._rational_to_float((100, 0))

        assert result is None

    def test_rational_to_float_ifd_rational(self, service):
        """Test _rational_to_float with IFDRational-like object"""
        mock_rational = Mock()
        mock_rational.numerator = 75
        mock_rational.denominator = 2

        result = service._rational_to_float(mock_rational)

        assert result == 37.5

    def test_rational_to_float_ifd_rational_zero_denom(self, service):
        """Test _rational_to_float with IFDRational zero denominator"""
        mock_rational = Mock()
        mock_rational.numerator = 75
        mock_rational.denominator = 0

        result = service._rational_to_float(mock_rational)

        assert result is None

    def test_rational_to_float_none(self, service):
        """Test _rational_to_float with None"""
        result = service._rational_to_float(None)

        assert result is None

    def test_rational_to_float_string(self, service):
        """Test _rational_to_float with string that can be converted"""
        result = service._rational_to_float("37.5")

        assert result == 37.5


class TestExtractExifMetadata:
    """Test extract_exif_metadata convenience function"""

    def test_extract_exif_metadata_success(self):
        """Test extract_exif_metadata with valid image"""
        mock_img = MagicMock()
        mock_img._getexif.return_value = {
            271: "Canon",  # Make
            272: "EOS R5",  # Model
        }

        with patch("app.services.exif_service.Image.open") as mock_open:
            mock_open.return_value.__enter__.return_value = mock_img

            result = extract_exif_metadata("/path/to/image.jpg")

            assert result is not None
            assert result["camera_make"] == "Canon"
            assert result["camera_model"] == "EOS R5"

    def test_extract_exif_metadata_no_exif(self):
        """Test extract_exif_metadata with no EXIF data"""
        mock_img = MagicMock()
        mock_img._getexif.return_value = None

        with patch("app.services.exif_service.Image.open") as mock_open:
            mock_open.return_value.__enter__.return_value = mock_img

            result = extract_exif_metadata("/path/to/image.jpg")

            assert result is None

    def test_extract_exif_metadata_failure(self):
        """Test extract_exif_metadata with file error"""
        with patch("app.services.exif_service.Image.open") as mock_open:
            mock_open.side_effect = Exception("File error")

            result = extract_exif_metadata("/invalid/path.jpg")

            assert result is None
