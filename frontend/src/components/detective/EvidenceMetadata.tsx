/**
 * Evidence Metadata Component (EXIF Display)
 * 009-mvp-gap-closure Feature - US11 (T103)
 *
 * Displays EXIF metadata extracted from evidence images.
 * Shows GPS coordinates, capture time, device info, etc.
 */

'use client';

import { useState } from 'react';

export interface ExifMetadata {
  // GPS Information
  gps_latitude?: number;
  gps_longitude?: number;
  gps_altitude?: number;
  gps_accuracy?: number;

  // Date/Time
  datetime_original?: string;
  datetime_digitized?: string;

  // Device Information
  camera_make?: string;
  camera_model?: string;
  software?: string;

  // Image Properties
  image_width?: number;
  image_height?: number;
  orientation?: number;

  // Additional
  flash?: boolean;
  focal_length?: number;
  iso_speed?: number;
  exposure_time?: string;
  f_number?: number;
}

interface EvidenceMetadataProps {
  exif: ExifMetadata;
  className?: string;
  showMap?: boolean;
}

// Format GPS coordinates to human-readable format
function formatCoordinate(value: number, isLatitude: boolean): string {
  const direction = isLatitude
    ? value >= 0 ? 'N' : 'S'
    : value >= 0 ? 'E' : 'W';

  const abs = Math.abs(value);
  const degrees = Math.floor(abs);
  const minutes = Math.floor((abs - degrees) * 60);
  const seconds = ((abs - degrees - minutes / 60) * 3600).toFixed(2);

  return `${degrees}° ${minutes}' ${seconds}" ${direction}`;
}

// Format date/time
function formatDateTime(dateString: string): string {
  try {
    const date = new Date(dateString);
    return date.toLocaleString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  } catch {
    return dateString;
  }
}

// Open Google Maps with coordinates
function openInMaps(lat: number, lng: number) {
  const url = `https://www.google.com/maps?q=${lat},${lng}`;
  window.open(url, '_blank', 'noopener,noreferrer');
}

// Section component
function MetadataSection({
  title,
  icon,
  children,
}: {
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-[var(--color-text-primary)]">
        {icon}
        <h4 className="font-medium">{title}</h4>
      </div>
      <div className="pl-7 space-y-2">{children}</div>
    </div>
  );
}

// Single metadata item
function MetadataItem({ label, value }: { label: string; value: string | number | undefined }) {
  if (value === undefined || value === null) return null;

  return (
    <div className="flex items-start gap-2 text-sm">
      <span className="text-[var(--color-text-secondary)] min-w-[100px]">{label}:</span>
      <span className="text-[var(--color-text-primary)] font-medium">{value}</span>
    </div>
  );
}

export default function EvidenceMetadata({
  exif,
  className = '',
  showMap = true,
}: EvidenceMetadataProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  const hasGPS = exif.gps_latitude !== undefined && exif.gps_longitude !== undefined;
  const hasDateTime = exif.datetime_original || exif.datetime_digitized;
  const hasDevice = exif.camera_make || exif.camera_model || exif.software;
  const hasImageProps = exif.image_width || exif.image_height;
  const hasCameraSettings = exif.iso_speed || exif.exposure_time || exif.f_number || exif.focal_length;

  const isEmpty = !hasGPS && !hasDateTime && !hasDevice && !hasImageProps && !hasCameraSettings;

  if (isEmpty) {
    return (
      <div className={`bg-[var(--color-bg-secondary)] rounded-lg p-4 ${className}`}>
        <div className="flex items-center gap-2 text-[var(--color-text-secondary)]">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="text-sm">메타데이터를 찾을 수 없습니다.</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg border border-[var(--color-border)] ${className}`}>
      {/* Header */}
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 hover:bg-[var(--color-bg-secondary)] transition-colors"
      >
        <div className="flex items-center gap-2">
          <svg className="w-5 h-5 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span className="font-medium text-[var(--color-text-primary)]">EXIF 메타데이터</span>
          {hasGPS && (
            <span className="px-2 py-0.5 text-xs bg-green-100 text-green-700 rounded-full">
              GPS 포함
            </span>
          )}
        </div>
        <svg
          className={`w-5 h-5 text-[var(--color-text-secondary)] transition-transform ${isExpanded ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Content */}
      {isExpanded && (
        <div className="p-4 pt-0 space-y-6">
          {/* GPS Section */}
          {hasGPS && (
            <MetadataSection
              title="위치 정보"
              icon={
                <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              }
            >
              <MetadataItem
                label="위도"
                value={exif.gps_latitude !== undefined ? formatCoordinate(exif.gps_latitude, true) : undefined}
              />
              <MetadataItem
                label="경도"
                value={exif.gps_longitude !== undefined ? formatCoordinate(exif.gps_longitude, false) : undefined}
              />
              {exif.gps_altitude !== undefined && (
                <MetadataItem label="고도" value={`${exif.gps_altitude.toFixed(1)}m`} />
              )}
              {exif.gps_accuracy !== undefined && (
                <MetadataItem label="정확도" value={`±${exif.gps_accuracy.toFixed(1)}m`} />
              )}

              {/* Map Link */}
              {showMap && exif.gps_latitude !== undefined && exif.gps_longitude !== undefined && (
                <button
                  type="button"
                  onClick={() => openInMaps(exif.gps_latitude!, exif.gps_longitude!)}
                  className="mt-2 inline-flex items-center gap-2 px-3 py-1.5 text-sm
                    bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)]
                    transition-colors min-h-[36px]"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                  </svg>
                  지도에서 보기
                </button>
              )}
            </MetadataSection>
          )}

          {/* DateTime Section */}
          {hasDateTime && (
            <MetadataSection
              title="촬영 시간"
              icon={
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              }
            >
              {exif.datetime_original && (
                <MetadataItem label="촬영일시" value={formatDateTime(exif.datetime_original)} />
              )}
              {exif.datetime_digitized && exif.datetime_digitized !== exif.datetime_original && (
                <MetadataItem label="디지털화" value={formatDateTime(exif.datetime_digitized)} />
              )}
            </MetadataSection>
          )}

          {/* Device Section */}
          {hasDevice && (
            <MetadataSection
              title="기기 정보"
              icon={
                <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              }
            >
              {exif.camera_make && <MetadataItem label="제조사" value={exif.camera_make} />}
              {exif.camera_model && <MetadataItem label="모델" value={exif.camera_model} />}
              {exif.software && <MetadataItem label="소프트웨어" value={exif.software} />}
            </MetadataSection>
          )}

          {/* Image Properties Section */}
          {(hasImageProps || hasCameraSettings) && (
            <MetadataSection
              title="이미지 속성"
              icon={
                <svg className="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              }
            >
              {exif.image_width && exif.image_height && (
                <MetadataItem label="해상도" value={`${exif.image_width} x ${exif.image_height}`} />
              )}
              {exif.iso_speed && <MetadataItem label="ISO" value={exif.iso_speed} />}
              {exif.exposure_time && <MetadataItem label="셔터속도" value={exif.exposure_time} />}
              {exif.f_number && <MetadataItem label="조리개" value={`f/${exif.f_number}`} />}
              {exif.focal_length && <MetadataItem label="초점거리" value={`${exif.focal_length}mm`} />}
              {exif.flash !== undefined && (
                <MetadataItem label="플래시" value={exif.flash ? '사용됨' : '사용 안 함'} />
              )}
            </MetadataSection>
          )}
        </div>
      )}
    </div>
  );
}
