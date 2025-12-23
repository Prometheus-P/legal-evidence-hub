"""
테스트용 음성 파일 생성 스크립트 - 시나리오 2: 가정폭력 + 경제적 학대
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
        "filename": "부부_생활비_싸움.mp3",
        "voice": "onyx",  # 남성 목소리 (남편)
        "text": """왜 또 돈 얘기야? 맨날 돈 돈 돈!
줄 만큼 줬잖아. 그걸로 알아서 해.
내가 번 돈 내가 쓰는데 니가 왜 상관이야?
더 이상 얘기하기 싫어. 입 닥쳐.
계속 이러면 나 진짜 화난다.""",
        "description": "남편이 생활비 문제로 언성 높이는 녹음"
    },
    {
        "filename": "아내_호소.mp3",
        "voice": "nova",  # 여성 목소리 (아내)
        "text": """여보, 제발 얘기 좀 하자.
애들 학원비도 밀렸어. 공과금도 못 냈어.
당신 월급이 얼마인데 150만원으로 어떻게 살아?
나머지 돈은 어디 쓰는 거야? 제발 알려줘.
나도 일하고 싶은데 애들 어린이집 보내려면 돈이 필요해.""",
        "description": "아내가 경제적 어려움을 호소하는 녹음"
    },
    {
        "filename": "폭력_현장.mp3",
        "voice": "onyx",  # 남성 목소리 (남편)
        "text": """내가 잔소리하지 말라고 했지?
왜 자꾸 같은 말 하게 해!
아, 진짜!
저리 가! 저리 가라고!
네가 자꾸 이러니까 내가 이러는 거야!""",
        "description": "남편이 흥분하며 물건 던지는 상황 녹음"
    },
    {
        "filename": "언니_상담.mp3",
        "voice": "nova",  # 여성 목소리 (언니와 통화)
        "text": """언니, 나 진짜 못 살겠어.
어제 또 그릇 던졌어. 손 베였어.
병원 갔다 왔는데 왜 돈 낭비하냐고 또 화내더라.
무서워. 애들한테도 안 좋은 거 알아.
이혼 생각 중인데, 어떻게 해야 해?""",
        "description": "아내가 언니에게 상황 상담하는 녹음"
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
