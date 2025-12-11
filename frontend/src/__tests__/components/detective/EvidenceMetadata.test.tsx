/**
 * Integration tests for EvidenceMetadata Component
 * Task T103 - US11 Tests
 *
 * Tests for frontend/src/components/detective/EvidenceMetadata.tsx:
 * - EXIF metadata display
 * - GPS coordinate formatting
 * - Date/time formatting
 * - Device information display
 * - Expandable/collapsible sections
 * - Map link functionality
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import EvidenceMetadata, { type ExifMetadata } from '@/components/detective/EvidenceMetadata';

// Mock window.open
const mockWindowOpen = jest.fn();
Object.defineProperty(window, 'open', {
  value: mockWindowOpen,
  writable: true,
});

describe('EvidenceMetadata Component', () => {
  const fullExifData: ExifMetadata = {
    gps_latitude: 37.5665,
    gps_longitude: 126.978,
    gps_altitude: 15.5,
    gps_accuracy: 5.0,
    datetime_original: '2024-01-15T14:30:00Z',
    datetime_digitized: '2024-01-15T14:30:00Z',
    camera_make: 'Samsung',
    camera_model: 'Galaxy S24',
    software: 'One UI 6.0',
    image_width: 4032,
    image_height: 3024,
    orientation: 1,
    flash: false,
    focal_length: 5.4,
    iso_speed: 100,
    exposure_time: '1/120',
    f_number: 1.8,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Empty State', () => {
    test('should show empty message when no metadata available', () => {
      const emptyExif: ExifMetadata = {};
      render(<EvidenceMetadata exif={emptyExif} />);

      expect(screen.getByText('메타데이터를 찾을 수 없습니다.')).toBeInTheDocument();
    });
  });

  describe('Header and Toggle', () => {
    test('should render EXIF header', () => {
      render(<EvidenceMetadata exif={fullExifData} />);

      expect(screen.getByText('EXIF 메타데이터')).toBeInTheDocument();
    });

    test('should show GPS badge when GPS data is present', () => {
      render(<EvidenceMetadata exif={fullExifData} />);

      expect(screen.getByText('GPS 포함')).toBeInTheDocument();
    });

    test('should not show GPS badge when no GPS data', () => {
      const noGpsExif: ExifMetadata = {
        camera_make: 'Samsung',
      };
      render(<EvidenceMetadata exif={noGpsExif} />);

      expect(screen.queryByText('GPS 포함')).not.toBeInTheDocument();
    });

    test('should toggle content visibility when header is clicked', () => {
      render(<EvidenceMetadata exif={fullExifData} />);

      // Initially expanded
      expect(screen.getByText('위치 정보')).toBeVisible();

      // Click to collapse
      fireEvent.click(screen.getByText('EXIF 메타데이터'));

      // Content should be hidden
      expect(screen.queryByText('위치 정보')).not.toBeInTheDocument();

      // Click to expand again
      fireEvent.click(screen.getByText('EXIF 메타데이터'));

      // Content should be visible again
      expect(screen.getByText('위치 정보')).toBeVisible();
    });
  });

  describe('GPS Information', () => {
    test('should display formatted latitude', () => {
      render(<EvidenceMetadata exif={fullExifData} />);

      expect(screen.getByText('위도:')).toBeInTheDocument();
      // 37.5665 N should format to approximately 37° 33' 59.40" N
      expect(screen.getByText(/37°.*N/)).toBeInTheDocument();
    });

    test('should display formatted longitude', () => {
      render(<EvidenceMetadata exif={fullExifData} />);

      expect(screen.getByText('경도:')).toBeInTheDocument();
      // 126.978 E should format to approximately 126° 58' 40.80" E
      expect(screen.getByText(/126°.*E/)).toBeInTheDocument();
    });

    test('should display altitude', () => {
      render(<EvidenceMetadata exif={fullExifData} />);

      expect(screen.getByText('고도:')).toBeInTheDocument();
      expect(screen.getByText('15.5m')).toBeInTheDocument();
    });

    test('should display GPS accuracy', () => {
      render(<EvidenceMetadata exif={fullExifData} />);

      expect(screen.getByText('정확도:')).toBeInTheDocument();
      expect(screen.getByText('±5.0m')).toBeInTheDocument();
    });

    test('should show "지도에서 보기" button when showMap is true', () => {
      render(<EvidenceMetadata exif={fullExifData} showMap={true} />);

      expect(screen.getByText('지도에서 보기')).toBeInTheDocument();
    });

    test('should not show map button when showMap is false', () => {
      render(<EvidenceMetadata exif={fullExifData} showMap={false} />);

      expect(screen.queryByText('지도에서 보기')).not.toBeInTheDocument();
    });

    test('should open Google Maps when map button is clicked', () => {
      render(<EvidenceMetadata exif={fullExifData} showMap={true} />);

      fireEvent.click(screen.getByText('지도에서 보기'));

      expect(mockWindowOpen).toHaveBeenCalledWith(
        'https://www.google.com/maps?q=37.5665,126.978',
        '_blank',
        'noopener,noreferrer'
      );
    });

    test('should format negative latitude as South', () => {
      const southExif: ExifMetadata = {
        gps_latitude: -33.8688,
        gps_longitude: 151.2093,
      };
      render(<EvidenceMetadata exif={southExif} />);

      // Should contain coordinates ending with S
      expect(screen.getByText(/\d+°.*S$/)).toBeInTheDocument();
    });

    test('should format negative longitude as West', () => {
      const westExif: ExifMetadata = {
        gps_latitude: 40.7128,
        gps_longitude: -74.006,
      };
      render(<EvidenceMetadata exif={westExif} />);

      // Should contain coordinates ending with W
      expect(screen.getByText(/\d+°.*W$/)).toBeInTheDocument();
    });
  });

  describe('DateTime Information', () => {
    test('should display formatted capture time', () => {
      render(<EvidenceMetadata exif={fullExifData} />);

      expect(screen.getByText('촬영 시간')).toBeInTheDocument();
      expect(screen.getByText('촬영일시:')).toBeInTheDocument();
      // Should be formatted in Korean locale
      expect(screen.getByText(/2024년/)).toBeInTheDocument();
    });

    test('should show digitized time if different from original', () => {
      const differentDigitized: ExifMetadata = {
        datetime_original: '2024-01-15T14:30:00Z',
        datetime_digitized: '2024-01-16T10:00:00Z',
      };
      render(<EvidenceMetadata exif={differentDigitized} />);

      expect(screen.getByText('디지털화:')).toBeInTheDocument();
    });

    test('should not show digitized time if same as original', () => {
      render(<EvidenceMetadata exif={fullExifData} />);

      expect(screen.queryByText('디지털화:')).not.toBeInTheDocument();
    });
  });

  describe('Device Information', () => {
    test('should display camera make', () => {
      render(<EvidenceMetadata exif={fullExifData} />);

      expect(screen.getByText('기기 정보')).toBeInTheDocument();
      expect(screen.getByText('제조사:')).toBeInTheDocument();
      expect(screen.getByText('Samsung')).toBeInTheDocument();
    });

    test('should display camera model', () => {
      render(<EvidenceMetadata exif={fullExifData} />);

      expect(screen.getByText('모델:')).toBeInTheDocument();
      expect(screen.getByText('Galaxy S24')).toBeInTheDocument();
    });

    test('should display software', () => {
      render(<EvidenceMetadata exif={fullExifData} />);

      expect(screen.getByText('소프트웨어:')).toBeInTheDocument();
      expect(screen.getByText('One UI 6.0')).toBeInTheDocument();
    });
  });

  describe('Image Properties', () => {
    test('should display resolution', () => {
      render(<EvidenceMetadata exif={fullExifData} />);

      expect(screen.getByText('이미지 속성')).toBeInTheDocument();
      expect(screen.getByText('해상도:')).toBeInTheDocument();
      expect(screen.getByText('4032 x 3024')).toBeInTheDocument();
    });

    test('should display ISO speed', () => {
      render(<EvidenceMetadata exif={fullExifData} />);

      expect(screen.getByText('ISO:')).toBeInTheDocument();
      expect(screen.getByText('100')).toBeInTheDocument();
    });

    test('should display shutter speed', () => {
      render(<EvidenceMetadata exif={fullExifData} />);

      expect(screen.getByText('셔터속도:')).toBeInTheDocument();
      expect(screen.getByText('1/120')).toBeInTheDocument();
    });

    test('should display aperture', () => {
      render(<EvidenceMetadata exif={fullExifData} />);

      expect(screen.getByText('조리개:')).toBeInTheDocument();
      expect(screen.getByText('f/1.8')).toBeInTheDocument();
    });

    test('should display focal length', () => {
      render(<EvidenceMetadata exif={fullExifData} />);

      expect(screen.getByText('초점거리:')).toBeInTheDocument();
      expect(screen.getByText('5.4mm')).toBeInTheDocument();
    });

    test('should display flash status as "사용 안 함" when false', () => {
      render(<EvidenceMetadata exif={fullExifData} />);

      expect(screen.getByText('플래시:')).toBeInTheDocument();
      expect(screen.getByText('사용 안 함')).toBeInTheDocument();
    });

    test('should display flash status as "사용됨" when true', () => {
      const flashExif: ExifMetadata = { ...fullExifData, flash: true };
      render(<EvidenceMetadata exif={flashExif} />);

      expect(screen.getByText('사용됨')).toBeInTheDocument();
    });
  });

  describe('Partial Data Display', () => {
    test('should only show GPS section when only GPS data is present', () => {
      const gpsOnlyExif: ExifMetadata = {
        gps_latitude: 37.5665,
        gps_longitude: 126.978,
      };
      render(<EvidenceMetadata exif={gpsOnlyExif} />);

      expect(screen.getByText('위치 정보')).toBeInTheDocument();
      expect(screen.queryByText('촬영 시간')).not.toBeInTheDocument();
      expect(screen.queryByText('기기 정보')).not.toBeInTheDocument();
      expect(screen.queryByText('이미지 속성')).not.toBeInTheDocument();
    });

    test('should only show device section when only device data is present', () => {
      const deviceOnlyExif: ExifMetadata = {
        camera_make: 'Apple',
        camera_model: 'iPhone 15 Pro',
      };
      render(<EvidenceMetadata exif={deviceOnlyExif} />);

      expect(screen.queryByText('위치 정보')).not.toBeInTheDocument();
      expect(screen.queryByText('촬영 시간')).not.toBeInTheDocument();
      expect(screen.getByText('기기 정보')).toBeInTheDocument();
      expect(screen.queryByText('이미지 속성')).not.toBeInTheDocument();
    });

    test('should show image properties when only camera settings present', () => {
      const settingsOnlyExif: ExifMetadata = {
        iso_speed: 400,
        exposure_time: '1/60',
      };
      render(<EvidenceMetadata exif={settingsOnlyExif} />);

      expect(screen.getByText('이미지 속성')).toBeInTheDocument();
      expect(screen.getByText('400')).toBeInTheDocument();
      expect(screen.getByText('1/60')).toBeInTheDocument();
    });
  });

  describe('Custom Styling', () => {
    test('should apply custom className', () => {
      const { container } = render(
        <EvidenceMetadata exif={fullExifData} className="custom-class" />
      );

      expect(container.firstChild).toHaveClass('custom-class');
    });
  });

  describe('Accessibility', () => {
    test('should have button type for header toggle', () => {
      render(<EvidenceMetadata exif={fullExifData} />);

      const toggleButton = screen.getByText('EXIF 메타데이터').closest('button');
      expect(toggleButton).toHaveAttribute('type', 'button');
    });

    test('should have button type for map link', () => {
      render(<EvidenceMetadata exif={fullExifData} showMap={true} />);

      const mapButton = screen.getByText('지도에서 보기');
      expect(mapButton).toHaveAttribute('type', 'button');
    });
  });

  describe('Coordinate Formatting Edge Cases', () => {
    test('should handle exactly 0 coordinates', () => {
      const zeroExif: ExifMetadata = {
        gps_latitude: 0,
        gps_longitude: 0,
      };
      render(<EvidenceMetadata exif={zeroExif} />);

      // 0 latitude should be North, 0 longitude should be East
      expect(screen.getByText(/0°.*N/)).toBeInTheDocument();
      expect(screen.getByText(/0°.*E/)).toBeInTheDocument();
    });

    test('should handle coordinates with many decimal places', () => {
      const preciseExif: ExifMetadata = {
        gps_latitude: 37.566535423,
        gps_longitude: 126.978125789,
      };
      render(<EvidenceMetadata exif={preciseExif} />);

      // Should render without error
      expect(screen.getByText('위도:')).toBeInTheDocument();
      expect(screen.getByText('경도:')).toBeInTheDocument();
    });
  });

  describe('Invalid Date Handling', () => {
    test('should render datetime section even with unusual date format', () => {
      const unusualDateExif: ExifMetadata = {
        datetime_original: '2024:01:15 14:30:00', // EXIF format with colons
      };
      render(<EvidenceMetadata exif={unusualDateExif} />);

      // Should still display the datetime section
      expect(screen.getByText('촬영 시간')).toBeInTheDocument();
      expect(screen.getByText('촬영일시:')).toBeInTheDocument();
    });
  });
});
