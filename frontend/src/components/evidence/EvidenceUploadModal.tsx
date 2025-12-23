'use client';

/**
 * EvidenceUploadModal - Modal for uploading evidence with metadata
 * Allows setting evidence name and legal number (갑제1호증, 을제1호증 etc.)
 */

import { useState, useCallback, useRef } from 'react';
import { UploadCloud, X, FileText, File } from 'lucide-react';
import { Modal, Button, Input } from '@/components/primitives';

interface UploadedFile {
  file: File;
  name: string;
  legalNumber: string;
}

interface EvidenceUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpload: (files: { file: File; name: string; legalNumber: string }[]) => void;
  caseId: string;
  /** Next suggested legal number (e.g., "갑제2호증") */
  nextLegalNumber?: string;
  isLoading?: boolean;
}

const LEGAL_NUMBER_PRESETS = [
  { label: '갑제', prefix: '갑제' },
  { label: '을제', prefix: '을제' },
  { label: '병제', prefix: '병제' },
  { label: '정제', prefix: '정제' },
];

export default function EvidenceUploadModal({
  isOpen,
  onClose,
  onUpload,
  caseId: _caseId,
  nextLegalNumber: _nextLegalNumber = '갑제1호증',
  isLoading = false,
}: EvidenceUploadModalProps) {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [selectedPrefix, setSelectedPrefix] = useState('갑제');
  const inputRef = useRef<HTMLInputElement>(null);

  const getNextNumber = useCallback((prefix: string) => {
    const existingNumbers = uploadedFiles
      .filter(f => f.legalNumber.startsWith(prefix))
      .map(f => {
        const match = f.legalNumber.match(/(\d+)/);
        return match ? parseInt(match[1], 10) : 0;
      });
    const maxNumber = Math.max(0, ...existingNumbers);
    return maxNumber + 1;
  }, [uploadedFiles]);

  const handleFilesSelected = useCallback((files: FileList | File[]) => {
    const fileArray = Array.from(files);
    const newFiles: UploadedFile[] = fileArray.map((file, index) => {
      const nextNum = getNextNumber(selectedPrefix) + index;
      return {
        file,
        name: file.name.replace(/\.[^/.]+$/, ''), // Remove extension for display name
        legalNumber: `${selectedPrefix}${nextNum}호증`,
      };
    });
    setUploadedFiles(prev => [...prev, ...newFiles]);
  }, [selectedPrefix, getNextNumber]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFilesSelected(e.dataTransfer.files);
    }
  }, [handleFilesSelected]);

  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFilesSelected(e.target.files);
    }
  }, [handleFilesSelected]);

  const handleRemoveFile = useCallback((index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  }, []);

  const handleUpdateFile = useCallback((index: number, field: 'name' | 'legalNumber', value: string) => {
    setUploadedFiles(prev => prev.map((f, i) =>
      i === index ? { ...f, [field]: value } : f
    ));
  }, []);

  const handleSubmit = useCallback(() => {
    if (uploadedFiles.length === 0) return;
    onUpload(uploadedFiles);
    setUploadedFiles([]);
    onClose();
  }, [uploadedFiles, onUpload, onClose]);

  const handleClose = useCallback(() => {
    setUploadedFiles([]);
    onClose();
  }, [onClose]);

  const getFileIcon = (fileName: string) => {
    const ext = fileName.split('.').pop()?.toLowerCase();
    if (['pdf'].includes(ext || '')) return <FileText className="w-5 h-5 text-red-500" />;
    if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext || '')) return <File className="w-5 h-5 text-blue-500" />;
    if (['mp3', 'wav', 'm4a'].includes(ext || '')) return <File className="w-5 h-5 text-purple-500" />;
    return <File className="w-5 h-5 text-gray-500" />;
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="증거 업로드"
      description="증거 파일을 업로드하고 증거 번호를 지정합니다."
      size="lg"
      footer={
        <>
          <Button variant="ghost" onClick={handleClose} disabled={isLoading}>
            취소
          </Button>
          <Button
            variant="secondary"
            onClick={handleSubmit}
            disabled={uploadedFiles.length === 0 || isLoading}
            isLoading={isLoading}
          >
            {uploadedFiles.length > 0 ? `${uploadedFiles.length}개 업로드` : '업로드'}
          </Button>
        </>
      }
    >
      {/* Legal Number Prefix Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          증거 구분 선택
        </label>
        <div className="flex gap-2">
          {LEGAL_NUMBER_PRESETS.map(preset => (
            <button
              key={preset.prefix}
              onClick={() => setSelectedPrefix(preset.prefix)}
              className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                selectedPrefix === preset.prefix
                  ? 'bg-primary text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {preset.label}
            </button>
          ))}
        </div>
      </div>

      {/* Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-colors duration-200
          ${isDragging
            ? 'border-primary bg-primary-light'
            : 'border-gray-300 hover:border-primary hover:bg-gray-50'
          }
        `}
      >
        <input
          ref={inputRef}
          type="file"
          multiple
          className="sr-only"
          onChange={handleFileInputChange}
          accept=".pdf,.jpg,.jpeg,.png,.gif,.webp,.mp3,.wav,.m4a,.txt,.doc,.docx"
        />
        <div className="flex flex-col items-center">
          <div className={`p-3 rounded-full mb-3 ${isDragging ? 'bg-primary-light' : 'bg-gray-100'}`}>
            <UploadCloud className={`w-8 h-8 ${isDragging ? 'text-primary' : 'text-gray-400'}`} />
          </div>
          <p className="text-sm font-medium text-gray-900">
            파일을 끌어다 놓거나 클릭하여 업로드
          </p>
          <p className="mt-1 text-xs text-gray-500">
            PDF, 이미지, 음성, 문서 파일 지원
          </p>
        </div>
      </div>

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div className="mt-4 space-y-3">
          <h4 className="text-sm font-medium text-gray-700">
            업로드할 파일 ({uploadedFiles.length}개)
          </h4>
          <div className="max-h-64 overflow-y-auto space-y-2">
            {uploadedFiles.map((uploadedFile, index) => (
              <div
                key={index}
                className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg"
              >
                {getFileIcon(uploadedFile.file.name)}
                <div className="flex-1 min-w-0 grid grid-cols-2 gap-2">
                  <Input
                    placeholder="증거명"
                    value={uploadedFile.name}
                    onChange={(e) => handleUpdateFile(index, 'name', e.target.value)}
                    className="text-sm"
                  />
                  <Input
                    placeholder="증거번호"
                    value={uploadedFile.legalNumber}
                    onChange={(e) => handleUpdateFile(index, 'legalNumber', e.target.value)}
                    className="text-sm"
                  />
                </div>
                <button
                  onClick={() => handleRemoveFile(index)}
                  className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                  aria-label="파일 제거"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </Modal>
  );
}
