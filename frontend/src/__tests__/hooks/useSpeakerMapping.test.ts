/**
 * Tests for useSpeakerMapping hook
 * 015-evidence-speaker-mapping
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { useSpeakerMapping, extractSpeakersFromContent } from '@/hooks/useSpeakerMapping';
import type { PartyNode } from '@/types/party';
import type { SpeakerMappingUpdateResponse } from '@/types/evidence';

describe('useSpeakerMapping hook', () => {
  const mockParties: PartyNode[] = [
    {
      id: 'party_001',
      case_id: 'case_123',
      name: '김철수',
      type: 'plaintiff',
      relation: '본인',
      description: '원고',
    },
    {
      id: 'party_002',
      case_id: 'case_123',
      name: '이영희',
      type: 'defendant',
      relation: '배우자',
      description: '피고',
    },
    {
      id: 'party_003',
      case_id: 'case_123',
      name: '박민수',
      type: 'witness',
      relation: '친구',
      description: '증인',
    },
  ];

  describe('initialization', () => {
    it('should initialize with empty mapping when no initial mapping provided', () => {
      const { result } = renderHook(() =>
        useSpeakerMapping({ parties: mockParties })
      );

      expect(result.current.mapping).toEqual({});
      expect(result.current.isDirty).toBe(false);
      expect(result.current.isValid).toBe(true);
      expect(result.current.saveStatus).toBe('idle');
    });

    it('should initialize with provided initial mapping', () => {
      const initialMapping = {
        '나': { party_id: 'party_001', party_name: '김철수' },
      };

      const { result } = renderHook(() =>
        useSpeakerMapping({
          initialMapping,
          parties: mockParties,
        })
      );

      expect(result.current.mapping).toEqual(initialMapping);
      expect(result.current.isDirty).toBe(false);
    });
  });

  describe('setMappingItem', () => {
    it('should add new mapping item', () => {
      const { result } = renderHook(() =>
        useSpeakerMapping({ parties: mockParties })
      );

      act(() => {
        result.current.setMappingItem('나', 'party_001', '김철수');
      });

      expect(result.current.mapping['나']).toEqual({
        party_id: 'party_001',
        party_name: '김철수',
      });
      expect(result.current.isDirty).toBe(true);
    });

    it('should update existing mapping item', () => {
      const initialMapping = {
        '나': { party_id: 'party_001', party_name: '김철수' },
      };

      const { result } = renderHook(() =>
        useSpeakerMapping({
          initialMapping,
          parties: mockParties,
        })
      );

      act(() => {
        result.current.setMappingItem('나', 'party_002', '이영희');
      });

      expect(result.current.mapping['나'].party_id).toBe('party_002');
      expect(result.current.isDirty).toBe(true);
    });
  });

  describe('removeMappingItem', () => {
    it('should remove existing mapping item', () => {
      const initialMapping = {
        '나': { party_id: 'party_001', party_name: '김철수' },
        '상대방': { party_id: 'party_002', party_name: '이영희' },
      };

      const { result } = renderHook(() =>
        useSpeakerMapping({
          initialMapping,
          parties: mockParties,
        })
      );

      act(() => {
        result.current.removeMappingItem('나');
      });

      expect(result.current.mapping['나']).toBeUndefined();
      expect(result.current.mapping['상대방']).toBeDefined();
      expect(result.current.isDirty).toBe(true);
    });

    it('should not throw when removing non-existent item', () => {
      const { result } = renderHook(() =>
        useSpeakerMapping({ parties: mockParties })
      );

      expect(() => {
        act(() => {
          result.current.removeMappingItem('존재하지않는화자');
        });
      }).not.toThrow();
    });
  });

  describe('clearMapping', () => {
    it('should clear all mapping items', () => {
      const initialMapping = {
        '나': { party_id: 'party_001', party_name: '김철수' },
        '상대방': { party_id: 'party_002', party_name: '이영희' },
      };

      const { result } = renderHook(() =>
        useSpeakerMapping({
          initialMapping,
          parties: mockParties,
        })
      );

      act(() => {
        result.current.clearMapping();
      });

      expect(result.current.mapping).toEqual({});
      expect(result.current.isDirty).toBe(true);
    });
  });

  describe('resetMapping', () => {
    it('should reset to initial mapping', () => {
      const initialMapping = {
        '나': { party_id: 'party_001', party_name: '김철수' },
      };

      const { result } = renderHook(() =>
        useSpeakerMapping({
          initialMapping,
          parties: mockParties,
        })
      );

      act(() => {
        result.current.setMappingItem('상대방', 'party_002', '이영희');
      });

      expect(result.current.isDirty).toBe(true);

      act(() => {
        result.current.resetMapping();
      });

      expect(result.current.mapping).toEqual(initialMapping);
      expect(result.current.isDirty).toBe(false);
    });
  });

  describe('validation', () => {
    it('should validate max speakers limit (10)', () => {
      const { result } = renderHook(() =>
        useSpeakerMapping({ parties: mockParties })
      );

      // Add 11 speakers
      act(() => {
        for (let i = 0; i <= 10; i++) {
          result.current.setMappingItem(`화자${i}`, 'party_001', '김철수');
        }
      });

      expect(result.current.isValid).toBe(false);
      expect(result.current.validationErrors.some(e => e.includes('10명'))).toBe(true);
    });

    it('should validate speaker label length (max 50)', () => {
      const { result } = renderHook(() =>
        useSpeakerMapping({ parties: mockParties })
      );

      const longLabel = '가'.repeat(51);

      act(() => {
        result.current.setMappingItem(longLabel, 'party_001', '김철수');
      });

      expect(result.current.isValid).toBe(false);
      expect(result.current.validationErrors.some(e => e.includes('너무 깁니다'))).toBe(true);
    });

    it('should validate party_id is not empty', () => {
      const { result } = renderHook(() =>
        useSpeakerMapping({ parties: mockParties })
      );

      act(() => {
        result.current.setMappingItem('나', '', '');
      });

      expect(result.current.isValid).toBe(false);
      expect(result.current.validationErrors.some(e => e.includes('인물을 선택'))).toBe(true);
    });

    it('should validate party exists in case', () => {
      const { result } = renderHook(() =>
        useSpeakerMapping({ parties: mockParties })
      );

      act(() => {
        result.current.setMappingItem('나', 'non_existent_party', '없는인물');
      });

      expect(result.current.isValid).toBe(false);
      expect(result.current.validationErrors.some(e => e.includes('존재하지 않습니다'))).toBe(true);
    });

    it('should be valid with proper mapping', () => {
      const { result } = renderHook(() =>
        useSpeakerMapping({ parties: mockParties })
      );

      act(() => {
        result.current.setMappingItem('나', 'party_001', '김철수');
        result.current.setMappingItem('상대방', 'party_002', '이영희');
      });

      expect(result.current.isValid).toBe(true);
      expect(result.current.validationErrors).toEqual([]);
    });
  });

  describe('save', () => {
    it('should save mapping successfully', async () => {
      const onSaveSuccess = jest.fn();
      const mockResponse: SpeakerMappingUpdateResponse = {
        evidence_id: 'evt_123',
        speaker_mapping: { '나': { party_id: 'party_001', party_name: '김철수' } },
        updated_at: '2024-01-15T10:00:00Z',
        updated_by: 'user_001',
      };
      const saveFn = jest.fn().mockResolvedValue(mockResponse);

      const { result } = renderHook(() =>
        useSpeakerMapping({
          parties: mockParties,
          onSaveSuccess,
        })
      );

      act(() => {
        result.current.setMappingItem('나', 'party_001', '김철수');
      });

      let saveResult: boolean;
      await act(async () => {
        saveResult = await result.current.save(saveFn);
      });

      expect(saveResult!).toBe(true);
      expect(saveFn).toHaveBeenCalledWith({
        speaker_mapping: { '나': { party_id: 'party_001', party_name: '김철수' } },
      });
      expect(onSaveSuccess).toHaveBeenCalledWith(mockResponse);
      expect(result.current.saveStatus).toBe('saved');
    });

    it('should handle save error', async () => {
      const onSaveError = jest.fn();
      const saveFn = jest.fn().mockRejectedValue(new Error('Save failed'));

      const { result } = renderHook(() =>
        useSpeakerMapping({
          parties: mockParties,
          onSaveError,
        })
      );

      act(() => {
        result.current.setMappingItem('나', 'party_001', '김철수');
      });

      let saveResult: boolean;
      await act(async () => {
        saveResult = await result.current.save(saveFn);
      });

      expect(saveResult!).toBe(false);
      expect(onSaveError).toHaveBeenCalled();
      expect(result.current.saveStatus).toBe('error');
    });

    it('should not save when validation fails', async () => {
      const saveFn = jest.fn();

      const { result } = renderHook(() =>
        useSpeakerMapping({ parties: mockParties })
      );

      // Add invalid mapping (empty party_id)
      act(() => {
        result.current.setMappingItem('나', '', '');
      });

      let saveResult: boolean;
      await act(async () => {
        saveResult = await result.current.save(saveFn);
      });

      expect(saveResult!).toBe(false);
      expect(saveFn).not.toHaveBeenCalled();
    });

    it('should transition save status correctly', async () => {
      jest.useFakeTimers();
      const mockResponse: SpeakerMappingUpdateResponse = {
        evidence_id: 'evt_123',
        speaker_mapping: {},
        updated_at: '2024-01-15T10:00:00Z',
        updated_by: 'user_001',
      };
      const saveFn = jest.fn().mockResolvedValue(mockResponse);

      const { result } = renderHook(() =>
        useSpeakerMapping({ parties: mockParties })
      );

      act(() => {
        result.current.setMappingItem('나', 'party_001', '김철수');
      });

      expect(result.current.saveStatus).toBe('idle');

      await act(async () => {
        await result.current.save(saveFn);
      });

      expect(result.current.saveStatus).toBe('saved');

      // After timeout, should reset to idle
      act(() => {
        jest.advanceTimersByTime(2000);
      });

      expect(result.current.saveStatus).toBe('idle');

      jest.useRealTimers();
    });
  });

  describe('helper functions', () => {
    it('getPartyById should return correct party', () => {
      const { result } = renderHook(() =>
        useSpeakerMapping({ parties: mockParties })
      );

      const party = result.current.getPartyById('party_002');
      expect(party?.name).toBe('이영희');
    });

    it('getPartyById should return undefined for non-existent party', () => {
      const { result } = renderHook(() =>
        useSpeakerMapping({ parties: mockParties })
      );

      const party = result.current.getPartyById('non_existent');
      expect(party).toBeUndefined();
    });

    it('getUnmappedSpeakers should return unmapped speakers only', () => {
      const initialMapping = {
        '나': { party_id: 'party_001', party_name: '김철수' },
      };

      const { result } = renderHook(() =>
        useSpeakerMapping({
          initialMapping,
          parties: mockParties,
        })
      );

      const unmapped = result.current.getUnmappedSpeakers(['나', '상대방', '친구']);
      expect(unmapped).toEqual(['상대방', '친구']);
    });
  });

  describe('isDirty detection', () => {
    it('should detect when mapping count changes', () => {
      const initialMapping = {
        '나': { party_id: 'party_001', party_name: '김철수' },
      };

      const { result } = renderHook(() =>
        useSpeakerMapping({
          initialMapping,
          parties: mockParties,
        })
      );

      expect(result.current.isDirty).toBe(false);

      act(() => {
        result.current.setMappingItem('상대방', 'party_002', '이영희');
      });

      expect(result.current.isDirty).toBe(true);
    });

    it('should detect when party_id changes', () => {
      const initialMapping = {
        '나': { party_id: 'party_001', party_name: '김철수' },
      };

      const { result } = renderHook(() =>
        useSpeakerMapping({
          initialMapping,
          parties: mockParties,
        })
      );

      act(() => {
        result.current.setMappingItem('나', 'party_002', '이영희');
      });

      expect(result.current.isDirty).toBe(true);
    });

    it('should not be dirty when same value is set', () => {
      const initialMapping = {
        '나': { party_id: 'party_001', party_name: '김철수' },
      };

      const { result } = renderHook(() =>
        useSpeakerMapping({
          initialMapping,
          parties: mockParties,
        })
      );

      act(() => {
        result.current.setMappingItem('나', 'party_001', '김철수');
      });

      expect(result.current.isDirty).toBe(false);
    });
  });
});

describe('extractSpeakersFromContent', () => {
  it('should extract speakers with colon format', () => {
    const content = `
      나: 안녕하세요
      상대방: 네 안녕하세요
      나: 오늘 날씨 좋네요
    `;

    const speakers = extractSpeakersFromContent(content);
    expect(speakers).toContain('나');
    expect(speakers).toContain('상대방');
  });

  it('should extract speakers with bracket format', () => {
    // Bracket format needs to be at the start of line (no leading spaces)
    const content = `[김철수] 안녕하세요
[이영희] 네 안녕하세요`;

    const speakers = extractSpeakersFromContent(content);
    expect(speakers).toContain('김철수');
    expect(speakers).toContain('이영희');
  });

  it('should extract common chat speakers', () => {
    const content = `
      본인: 안녕
      배우자: 응 안녕
    `;

    const speakers = extractSpeakersFromContent(content);
    expect(speakers).toContain('본인');
    expect(speakers).toContain('배우자');
  });

  it('should return sorted unique speakers', () => {
    const content = `
      나: 첫번째
      상대방: 응답
      나: 두번째
      상대방: 또 응답
    `;

    const speakers = extractSpeakersFromContent(content);
    expect(speakers).toEqual(['나', '상대방']);
  });

  it('should handle empty content', () => {
    expect(extractSpeakersFromContent('')).toEqual([]);
    expect(extractSpeakersFromContent(null as unknown as string)).toEqual([]);
  });

  it('should filter out labels longer than 50 characters', () => {
    const longLabel = '가'.repeat(51);
    const content = `${longLabel}: 긴 이름`;

    const speakers = extractSpeakersFromContent(content);
    expect(speakers).not.toContain(longLabel);
  });

  it('should handle mixed formats', () => {
    // Bracket format at line start, colon format with leading spaces
    const content = `나: 카톡 형식
[친구] 대괄호 형식
상대방 : 공백 있는 형식`;

    const speakers = extractSpeakersFromContent(content);
    expect(speakers).toContain('나');
    expect(speakers).toContain('친구');
    expect(speakers).toContain('상대방');
  });
});
