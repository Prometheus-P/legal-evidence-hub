"""
테스트용 음성 파일 생성 스크립트
OpenAI TTS API를 사용하여 이혼소송 증거용 모의 녹음 파일 생성
"""

from openai import OpenAI
from pathlib import Path

client = OpenAI()

# 출력 디렉토리
OUTPUT_DIR = Path(__file__).parent

# 테스트 시나리오들
SCENARIOS = [
    {
        "filename": "call_husband_mistress.mp3",
        "voice": "onyx",  # 남성 목소리
        "text": """여보세요? 응 나야.
오늘 저녁에 시간 돼?
응, 7시에 그 호텔 로비에서 만나자.
아내한테는 야근한다고 했어. 걱정 마.
그래, 이따 봐. 나도 보고 싶어.""",
        "description": "남편이 상간녀에게 전화하는 녹음"
    },
    {
        "filename": "fight_couple.mp3",
        "voice": "nova",  # 여성 목소리
        "text": """당신 요즘 왜 이렇게 늦게 들어와?
맨날 야근이라더니, 카드 내역 보니까 호텔이랑 레스토랑이 왜 이렇게 많아?
거짓말하지 마. 나 다 알아.
그 여자 누구야? 회사 사람이야?
당신 정말 너무하다.""",
        "description": "아내가 남편에게 추궁하는 녹음"
    },
    {
        "filename": "confession_husband.mp3",
        "voice": "onyx",  # 남성 목소리
        "text": """미안해. 사실 회사에 좋아하는 사람이 생겼어.
6개월 정도 됐어.
처음엔 그냥 동료였는데, 어쩌다 보니...
이혼하자는 게 아니야. 그냥 솔직하게 말하고 싶었어.
정말 미안해.""",
        "description": "남편이 외도를 고백하는 녹음"
    },
]


def generate_audio():
    """모든 시나리오에 대해 음성 파일 생성"""

    for scenario in SCENARIOS:
        output_path = OUTPUT_DIR / scenario["filename"]

        print(f"생성 중: {scenario['filename']}")
        print(f"  설명: {scenario['description']}")

        try:
            response = client.audio.speech.create(
                model="tts-1",
                voice=scenario["voice"],
                input=scenario["text"]
            )

            response.stream_to_file(str(output_path))
            print(f"  ✅ 완료: {output_path}")

        except Exception as e:
            print(f"  ❌ 실패: {e}")

    print("\n모든 파일 생성 완료!")


if __name__ == "__main__":
    generate_audio()
