"""
테스트용 PDF 파일 생성 스크립트
실제 카드사/통신사 양식을 모방한 이혼소송 증거 문서 생성
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from pathlib import Path
import os

# 출력 디렉토리
OUTPUT_DIR = Path(__file__).parent

# 한글 폰트 등록 (macOS)
FONT_PATHS = [
    "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "/Library/Fonts/NanumGothic.ttf",
]

KOREAN_FONT = 'Helvetica'
for font_path in FONT_PATHS:
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont('AppleGothic', font_path))
            KOREAN_FONT = 'AppleGothic'
            break
        except Exception:
            continue


def create_card_statement():
    """신한카드 실제 양식 스타일 이용대금명세서"""

    output_path = OUTPUT_DIR / "카드_결제_내역서.pdf"
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        topMargin=15*mm,
        bottomMargin=15*mm,
        leftMargin=15*mm,
        rightMargin=15*mm
    )

    styles = getSampleStyleSheet()

    # 스타일 정의
    styles.add(ParagraphStyle(name='KHeader', fontName=KOREAN_FONT, fontSize=8, textColor=colors.grey))
    styles.add(ParagraphStyle(name='KTitle', fontName=KOREAN_FONT, fontSize=18, alignment=TA_CENTER, spaceAfter=5*mm))
    styles.add(ParagraphStyle(name='KSubtitle', fontName=KOREAN_FONT, fontSize=11, alignment=TA_LEFT, spaceBefore=3*mm))
    styles.add(ParagraphStyle(name='KBody', fontName=KOREAN_FONT, fontSize=9, leading=12))
    styles.add(ParagraphStyle(name='KSmall', fontName=KOREAN_FONT, fontSize=7, textColor=colors.grey, leading=9))
    styles.add(ParagraphStyle(name='KRight', fontName=KOREAN_FONT, fontSize=9, alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name='KCenter', fontName=KOREAN_FONT, fontSize=9, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='KFooter', fontName=KOREAN_FONT, fontSize=7, textColor=colors.grey, alignment=TA_CENTER))

    elements = []

    # 상단 헤더 (회사 정보)
    header_data = [
        [
            Paragraph("신한카드 주식회사", styles['KBody']),
            Paragraph("서울특별시 중구 을지로 66", styles['KSmall']),
            Paragraph("고객센터 1544-7000", styles['KSmall']),
        ]
    ]
    header_table = Table(header_data, colWidths=[50*mm, 70*mm, 50*mm])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 3*mm))

    # 구분선
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0046FF')))
    elements.append(Spacer(1, 5*mm))

    # 제목
    elements.append(Paragraph("신용카드 이용대금 명세서", styles['KTitle']))
    elements.append(Spacer(1, 3*mm))

    # 발행정보
    elements.append(Paragraph("결제년월: 2024년 11월 | 명세서 발행일: 2024.11.05", styles['KCenter']))
    elements.append(Spacer(1, 5*mm))

    # 고객 정보 박스
    customer_box = [
        ["회 원 명", "김 동 우", "결제계좌", "신한 110-***-***890"],
        ["카드번호", "9411-****-****-1234", "결제일", "매월 15일"],
        ["청구기간", "2024.10.01 ~ 2024.10.31", "이번달 결제금액", "10,767,000원"],
    ]
    cust_table = Table(customer_box, colWidths=[28*mm, 55*mm, 28*mm, 55*mm])
    cust_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), KOREAN_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F0FE')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#E8F0FE')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#0046FF')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('TEXTCOLOR', (3, 2), (3, 2), colors.HexColor('#0046FF')),  # 결제금액 강조
    ]))
    elements.append(cust_table)
    elements.append(Spacer(1, 8*mm))

    # 이용내역 섹션
    elements.append(Paragraph("■ 국내 이용내역", styles['KSubtitle']))
    elements.append(Spacer(1, 2*mm))

    # 거래 내역 테이블 - 실제 카드사 양식처럼
    transactions = [
        ["이용일자", "이용가맹점", "이용금액", "할부", "잔여금액"],
        ["10/03", "노보텔앰배서더강남 / 서울", "289,000", "일시불", "289,000"],
        ["10/03", "라망레스토랑 청담 / 서울", "187,000", "일시불", "187,000"],
        ["10/07", "티파니앤코 청담플래그십 / 서울", "2,450,000", "3개월", "816,667"],
        ["10/12", "JW메리어트호텔서울 / 서울", "356,000", "일시불", "356,000"],
        ["10/12", "정식당 / 서울", "320,000", "일시불", "320,000"],
        ["10/15", "신라호텔 / 서울", "412,000", "일시불", "412,000"],
        ["10/18", "SK-II 갤러리아명품관 / 서울", "890,000", "일시불", "890,000"],
        ["10/21", "파크하얏트서울 / 서울", "485,000", "일시불", "485,000"],
        ["10/21", "밍글스 / 서울", "280,000", "일시불", "280,000"],
        ["10/25", "반얀트리클럽앤스파서울 / 서울", "520,000", "일시불", "520,000"],
        ["10/28", "샤넬 청담부티크 / 서울", "4,200,000", "6개월", "700,000"],
        ["10/31", "그랜드인터컨티넨탈서울 / 서울", "378,000", "일시불", "378,000"],
    ]

    trans_table = Table(transactions, colWidths=[22*mm, 75*mm, 30*mm, 20*mm, 28*mm])
    trans_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), KOREAN_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0046FF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),
        ('ALIGN', (4, 1), (4, -1), 'RIGHT'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#0046FF')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
    ]))
    elements.append(trans_table)
    elements.append(Spacer(1, 5*mm))

    # 합계
    summary_data = [
        ["국내이용 합계", "", "10,767,000원", "", "5,633,667원"],
    ]
    summary_table = Table(summary_data, colWidths=[22*mm, 75*mm, 30*mm, 20*mm, 28*mm])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), KOREAN_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFF3E0')),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ('ALIGN', (4, 0), (4, 0), 'RIGHT'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#FF6F00')),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 10*mm))

    # 하단 안내문
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph(
        "※ 본 명세서는 「여신전문금융업법」 제24조에 따라 발급되었습니다.",
        styles['KSmall']
    ))
    elements.append(Paragraph(
        "※ 이용대금 명세서 관련 문의: 신한카드 고객센터 1544-7000",
        styles['KSmall']
    ))
    elements.append(Paragraph(
        "※ 명세서 수령 후 14일 이내 이의제기 없을 시 승인된 것으로 간주합니다.",
        styles['KSmall']
    ))
    elements.append(Spacer(1, 5*mm))

    # 발급 확인
    elements.append(Paragraph("발급일시: 2024년 11월 05일 09:32:15", styles['KRight']))
    elements.append(Paragraph("문서확인번호: SC2024110500012847", styles['KRight']))

    doc.build(elements)
    print(f"✅ 생성 완료: {output_path}")


def create_call_history():
    """SKT 실제 양식 스타일 통화내역 조회서"""

    output_path = OUTPUT_DIR / "통화_내역서.pdf"
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        topMargin=15*mm,
        bottomMargin=15*mm,
        leftMargin=15*mm,
        rightMargin=15*mm
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='SKHeader', fontName=KOREAN_FONT, fontSize=8, textColor=colors.grey))
    styles.add(ParagraphStyle(name='SKTitle', fontName=KOREAN_FONT, fontSize=18, alignment=TA_CENTER, spaceAfter=5*mm))
    styles.add(ParagraphStyle(name='SKSubtitle', fontName=KOREAN_FONT, fontSize=11, alignment=TA_LEFT, spaceBefore=3*mm))
    styles.add(ParagraphStyle(name='SKBody', fontName=KOREAN_FONT, fontSize=9, leading=12))
    styles.add(ParagraphStyle(name='SKSmall', fontName=KOREAN_FONT, fontSize=7, textColor=colors.grey, leading=9))
    styles.add(ParagraphStyle(name='SKRight', fontName=KOREAN_FONT, fontSize=9, alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name='SKCenter', fontName=KOREAN_FONT, fontSize=9, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='SKWarning', fontName=KOREAN_FONT, fontSize=8, textColor=colors.red))

    elements = []

    # SKT 헤더
    header_data = [[
        Paragraph("SK텔레콤", styles['SKBody']),
        Paragraph("www.tworld.co.kr", styles['SKSmall']),
        Paragraph("고객센터 114", styles['SKSmall']),
    ]]
    header_table = Table(header_data, colWidths=[50*mm, 70*mm, 50*mm])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 3*mm))

    # 구분선 (SKT 레드)
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#E4002B')))
    elements.append(Spacer(1, 5*mm))

    # 제목
    elements.append(Paragraph("통 화 내 역 조 회 서", styles['SKTitle']))
    elements.append(Spacer(1, 5*mm))

    # 발급 안내
    elements.append(Paragraph(
        "본 조회서는 고객님의 요청에 의해 발급된 공식 문서입니다.",
        styles['SKCenter']
    ))
    elements.append(Spacer(1, 5*mm))

    # 고객/조회 정보
    info_box = [
        ["가 입 자 명", "김동우", "주민등록번호", "850315-1******"],
        ["서비스번호", "010-1234-5678", "요 금 제", "T플랜 에센셜"],
        ["조 회 기 간", "2024.10.01 ~ 2024.10.31", "발 급 일 자", "2024.11.10"],
        ["발 급 사 유", "본인요청 (법적증빙용)", "발 급 번 호", "SKT-2024111000847"],
    ]
    info_table = Table(info_box, colWidths=[28*mm, 55*mm, 28*mm, 55*mm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), KOREAN_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#FDE8E8')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#FDE8E8')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E4002B')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 8*mm))

    # 통화내역 섹션
    elements.append(Paragraph("■ 음성통화 상세내역", styles['SKSubtitle']))
    elements.append(Spacer(1, 2*mm))

    # 통화 내역 (실제 양식처럼 상세하게)
    calls = [
        ["No", "일시", "상대방번호", "발/수신", "통화시간", "통화료"],
        ["1", "10/01 09:15", "010-9876-5432", "발신", "12분 34초", "0원"],
        ["2", "10/01 22:30", "010-9876-5432", "발신", "45분 12초", "0원"],
        ["3", "10/02 12:00", "010-5555-1234", "발신", "2분 10초", "0원"],
        ["4", "10/03 08:45", "010-9876-5432", "수신", "8분 22초", "-"],
        ["5", "10/03 23:10", "010-9876-5432", "발신", "1시간 05분", "0원"],
        ["6", "10/05 19:30", "010-9876-5432", "발신", "32분 45초", "0원"],
        ["7", "10/07 21:00", "010-9876-5432", "발신", "28분 18초", "0원"],
        ["8", "10/10 10:00", "02-1234-5678", "발신", "5분 30초", "0원"],
        ["9", "10/12 07:30", "010-9876-5432", "수신", "15분 40초", "-"],
        ["10", "10/12 22:45", "010-9876-5432", "발신", "52분 33초", "0원"],
        ["11", "10/15 20:15", "010-9876-5432", "발신", "38분 27초", "0원"],
        ["12", "10/18 23:30", "010-9876-5432", "발신", "1시간 12분", "0원"],
        ["13", "10/20 09:00", "010-5555-1234", "수신", "3분 45초", "-"],
        ["14", "10/21 21:40", "010-9876-5432", "발신", "47분 55초", "0원"],
        ["15", "10/25 22:00", "010-9876-5432", "발신", "55분 20초", "0원"],
        ["16", "10/28 19:45", "010-9876-5432", "발신", "41분 15초", "0원"],
        ["17", "10/31 23:55", "010-9876-5432", "발신", "1시간 03분", "0원"],
    ]

    call_table = Table(calls, colWidths=[12*mm, 28*mm, 38*mm, 18*mm, 28*mm, 20*mm])
    call_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), KOREAN_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E4002B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),
        ('ALIGN', (4, 1), (4, -1), 'CENTER'),
        ('ALIGN', (5, 1), (5, -1), 'RIGHT'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E4002B')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFF5F5')]),
    ]))
    elements.append(call_table)
    elements.append(Spacer(1, 5*mm))

    # 통계 요약
    elements.append(Paragraph("■ 통화 통계 요약", styles['SKSubtitle']))
    elements.append(Spacer(1, 2*mm))

    stats = [
        ["상대방 번호", "통화 횟수", "발신", "수신", "총 통화시간", "비율"],
        ["010-9876-5432", "15회", "13회", "2회", "9시간 37분 01초", "98.1%"],
        ["010-5555-1234", "2회", "1회", "1회", "5분 55초", "1.0%"],
        ["02-1234-5678", "1회", "1회", "0회", "5분 30초", "0.9%"],
        ["합    계", "18회", "15회", "3회", "9시간 48분 26초", "100%"],
    ]

    stats_table = Table(stats, colWidths=[38*mm, 22*mm, 18*mm, 18*mm, 35*mm, 18*mm])
    stats_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), KOREAN_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#333333')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#FFEBEE')),  # 첫 번째 번호 강조
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E0E0E0')),  # 합계 행
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#333333')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(stats_table)
    elements.append(Spacer(1, 8*mm))

    # 하단 안내문
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph(
        "※ 본 조회서는 「전기통신사업법」 제83조 및 동법 시행령 제45조에 의거하여 발급되었습니다.",
        styles['SKSmall']
    ))
    elements.append(Paragraph(
        "※ 통화료 '0원'은 기본제공 무료통화 차감분입니다. '-'는 수신통화로 요금 미발생입니다.",
        styles['SKSmall']
    ))
    elements.append(Paragraph(
        "※ 본 문서는 법적 증빙자료로 활용 가능하며, 위변조 시 형사처벌 대상입니다.",
        styles['SKSmall']
    ))
    elements.append(Spacer(1, 5*mm))

    # 발급 확인 (공식 문서 느낌)
    confirm_box = [
        ["발급일시", "2024년 11월 10일 14:27:33"],
        ["문서확인번호", "SKT-2024111000847-VRFY"],
        ["발급담당", "T월드 고객센터 (자동발급)"],
    ]
    confirm_table = Table(confirm_box, colWidths=[35*mm, 80*mm])
    confirm_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), KOREAN_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.grey),
        ('PADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(confirm_table)

    doc.build(elements)
    print(f"✅ 생성 완료: {output_path}")


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print("PDF 문서 생성 중...")
    create_card_statement()
    create_call_history()
    print("\n모든 PDF 생성 완료!")
