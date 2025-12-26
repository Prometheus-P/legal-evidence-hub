"""
테스트용 PDF 파일 생성 스크립트 - 시나리오 2: 가정폭력 + 경제적 학대
진단서, 급여명세서, 카드 해지 내역서 생성
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


def create_medical_certificate():
    """병원 진단서 - 외상 진단"""

    output_path = OUTPUT_DIR / "진단서_외상.pdf"
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        topMargin=20*mm,
        bottomMargin=20*mm,
        leftMargin=20*mm,
        rightMargin=20*mm
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='KTitle', fontName=KOREAN_FONT, fontSize=22, alignment=TA_CENTER, spaceAfter=10*mm))
    styles.add(ParagraphStyle(name='KSubtitle', fontName=KOREAN_FONT, fontSize=12, alignment=TA_CENTER, spaceBefore=3*mm))
    styles.add(ParagraphStyle(name='KBody', fontName=KOREAN_FONT, fontSize=10, leading=14))
    styles.add(ParagraphStyle(name='KSmall', fontName=KOREAN_FONT, fontSize=8, textColor=colors.grey))
    styles.add(ParagraphStyle(name='KRight', fontName=KOREAN_FONT, fontSize=10, alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name='KCenter', fontName=KOREAN_FONT, fontSize=10, alignment=TA_CENTER))

    elements = []

    # 병원 헤더
    elements.append(Paragraph("서울중앙병원", styles['KTitle']))
    elements.append(Paragraph("Seoul Central Hospital", styles['KSubtitle']))
    elements.append(Spacer(1, 5*mm))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1565C0')))
    elements.append(Spacer(1, 10*mm))

    # 제목
    elements.append(Paragraph("진    단    서", styles['KTitle']))
    elements.append(Spacer(1, 10*mm))

    # 환자 정보
    patient_info = [
        ["환 자 명", "이수진", "주민등록번호", "880520-2******"],
        ["주    소", "서울특별시 강남구 역삼동 123-45", "", ""],
        ["진료과", "응급의학과", "진료일자", "2025년 11월 16일"],
    ]

    patient_table = Table(patient_info, colWidths=[30*mm, 60*mm, 30*mm, 50*mm])
    patient_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), KOREAN_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E3F2FD')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#E3F2FD')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1565C0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('SPAN', (1, 1), (3, 1)),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(patient_table)
    elements.append(Spacer(1, 10*mm))

    # 진단 내용
    elements.append(Paragraph("■ 상병명", styles['KBody']))
    elements.append(Spacer(1, 3*mm))

    diagnosis_box = [
        ["1. 우측 수부 열상 (S61.0)", ""],
        ["2. 좌측 전완부 타박상 (S50.0)", ""],
        ["3. 정서적 충격 반응 (F43.0)", ""],
    ]
    diag_table = Table(diagnosis_box, colWidths=[120*mm, 50*mm])
    diag_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), KOREAN_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(diag_table)
    elements.append(Spacer(1, 8*mm))

    # 소견
    elements.append(Paragraph("■ 의사 소견", styles['KBody']))
    elements.append(Spacer(1, 3*mm))

    opinion = """상기 환자는 2025년 11월 16일 본원 응급실에 내원하였음.

내원 당시 우측 손등에 약 3cm 길이의 열상이 관찰되었으며, 유리 파편에 의한
절상으로 추정됨. 좌측 전완부에 약 5x3cm 크기의 타박상 및 발적 소견 있음.

환자 진술에 의하면 가정 내 분쟁 중 유리 그릇이 파손되어 발생한 부상으로,
정서적 충격 반응도 동반되어 있음.

치료 내용: 열상 봉합(5바늘), 소독 및 드레싱, 항생제 처방

향후 치료 기간: 약 2주간 통원 치료 필요
재진 예정일: 2025년 11월 23일"""

    elements.append(Paragraph(opinion.replace('\n', '<br/>'), styles['KBody']))
    elements.append(Spacer(1, 15*mm))

    # 발급 정보
    elements.append(Paragraph("위와 같이 진단함.", styles['KCenter']))
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph("2025년  11월  16일", styles['KCenter']))
    elements.append(Spacer(1, 15*mm))

    # 의사 서명
    doctor_info = [
        ["의료기관명", "서울중앙병원"],
        ["주      소", "서울특별시 강남구 테헤란로 152"],
        ["담당의사", "김정훈 (응급의학과 전문의)"],
        ["면허번호", "제 85421 호"],
    ]
    doc_table = Table(doctor_info, colWidths=[35*mm, 100*mm])
    doc_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), KOREAN_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(doc_table)

    elements.append(Spacer(1, 10*mm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph("※ 본 진단서는 「의료법」 제17조에 따라 발급되었습니다.", styles['KSmall']))
    elements.append(Paragraph("※ 문서확인번호: SCH-2025111600234", styles['KSmall']))

    doc.build(elements)
    print(f"✅ 생성 완료: {output_path}")


def create_salary_statement():
    """급여명세서 - 남편 수입 증빙"""

    output_path = OUTPUT_DIR / "급여명세서_박철민.pdf"
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        topMargin=15*mm,
        bottomMargin=15*mm,
        leftMargin=15*mm,
        rightMargin=15*mm
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='KTitle', fontName=KOREAN_FONT, fontSize=18, alignment=TA_CENTER, spaceAfter=5*mm))
    styles.add(ParagraphStyle(name='KSubtitle', fontName=KOREAN_FONT, fontSize=11, alignment=TA_LEFT, spaceBefore=3*mm))
    styles.add(ParagraphStyle(name='KBody', fontName=KOREAN_FONT, fontSize=9, leading=12))
    styles.add(ParagraphStyle(name='KSmall', fontName=KOREAN_FONT, fontSize=7, textColor=colors.grey))
    styles.add(ParagraphStyle(name='KRight', fontName=KOREAN_FONT, fontSize=9, alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name='KCenter', fontName=KOREAN_FONT, fontSize=9, alignment=TA_CENTER))

    elements = []

    # 회사 헤더
    elements.append(Paragraph("(주) 테크솔루션즈", styles['KTitle']))
    elements.append(Paragraph("서울특별시 서초구 반포대로 58 | 대표이사 정상훈", styles['KCenter']))
    elements.append(Spacer(1, 3*mm))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2E7D32')))
    elements.append(Spacer(1, 8*mm))

    # 제목
    elements.append(Paragraph("급  여  명  세  서", styles['KTitle']))
    elements.append(Paragraph("2025년 10월분", styles['KCenter']))
    elements.append(Spacer(1, 8*mm))

    # 직원 정보
    emp_info = [
        ["사 원 번 호", "TS-2018-0342", "부    서", "개발팀"],
        ["성      명", "박 철 민", "직    급", "과장"],
        ["입 사 일 자", "2018.03.05", "근속년수", "7년 8개월"],
    ]
    emp_table = Table(emp_info, colWidths=[30*mm, 55*mm, 25*mm, 55*mm])
    emp_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), KOREAN_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F5E9')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#E8F5E9')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#2E7D32')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(emp_table)
    elements.append(Spacer(1, 8*mm))

    # 지급 내역
    elements.append(Paragraph("■ 지급 내역", styles['KSubtitle']))
    elements.append(Spacer(1, 2*mm))

    payment = [
        ["항목", "금액", "항목", "금액"],
        ["기본급", "3,200,000", "식대", "150,000"],
        ["직책수당", "300,000", "교통비", "100,000"],
        ["야근수당", "420,000", "상여금", "0"],
        ["연장근로수당", "280,000", "", ""],
        ["", "", "", ""],
        ["지급액 계", "", "", "4,450,000"],
    ]
    pay_table = Table(payment, colWidths=[40*mm, 40*mm, 40*mm, 45*mm])
    pay_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), KOREAN_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E7D32')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#2E7D32')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#C8E6C9')),
        ('SPAN', (0, -1), (2, -1)),
    ]))
    elements.append(pay_table)
    elements.append(Spacer(1, 5*mm))

    # 공제 내역
    elements.append(Paragraph("■ 공제 내역", styles['KSubtitle']))
    elements.append(Spacer(1, 2*mm))

    deduction = [
        ["항목", "금액", "항목", "금액"],
        ["국민연금", "200,250", "건강보험", "156,980"],
        ["고용보험", "36,410", "장기요양보험", "20,350"],
        ["소득세", "128,500", "지방소득세", "12,850"],
        ["", "", "", ""],
        ["공제액 계", "", "", "555,340"],
    ]
    ded_table = Table(deduction, colWidths=[40*mm, 40*mm, 40*mm, 45*mm])
    ded_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), KOREAN_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D32F2F')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#D32F2F')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FFCDD2')),
        ('SPAN', (0, -1), (2, -1)),
    ]))
    elements.append(ded_table)
    elements.append(Spacer(1, 8*mm))

    # 실수령액
    net_pay = [
        ["실 수 령 액", "3,894,660 원"],
    ]
    net_table = Table(net_pay, colWidths=[80*mm, 85*mm])
    net_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), KOREAN_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1565C0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(net_table)
    elements.append(Spacer(1, 10*mm))

    # 지급 계좌
    elements.append(Paragraph("지급계좌: 신한은행 110-***-***456 (박철민)", styles['KRight']))
    elements.append(Paragraph("지급일자: 2025년 10월 25일", styles['KRight']))
    elements.append(Spacer(1, 10*mm))

    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph("※ 본 급여명세서는 「근로기준법」 제48조에 따라 발급되었습니다.", styles['KSmall']))
    elements.append(Paragraph("※ 문서확인번호: TS-PAY-202510-0342", styles['KSmall']))

    doc.build(elements)
    print(f"✅ 생성 완료: {output_path}")


def create_card_cancellation():
    """가족카드 해지 통보서"""

    output_path = OUTPUT_DIR / "가족카드_해지통보서.pdf"
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        topMargin=15*mm,
        bottomMargin=15*mm,
        leftMargin=15*mm,
        rightMargin=15*mm
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='KTitle', fontName=KOREAN_FONT, fontSize=18, alignment=TA_CENTER, spaceAfter=5*mm))
    styles.add(ParagraphStyle(name='KBody', fontName=KOREAN_FONT, fontSize=10, leading=14))
    styles.add(ParagraphStyle(name='KSmall', fontName=KOREAN_FONT, fontSize=8, textColor=colors.grey))
    styles.add(ParagraphStyle(name='KRight', fontName=KOREAN_FONT, fontSize=10, alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name='KCenter', fontName=KOREAN_FONT, fontSize=10, alignment=TA_CENTER))

    elements = []

    # KB 헤더
    elements.append(Paragraph("KB국민카드", styles['KTitle']))
    elements.append(Paragraph("서울특별시 중구 나대로 209 | 고객센터 1588-1688", styles['KCenter']))
    elements.append(Spacer(1, 3*mm))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#FFC107')))
    elements.append(Spacer(1, 10*mm))

    # 제목
    elements.append(Paragraph("가족카드 해지 통보서", styles['KTitle']))
    elements.append(Spacer(1, 10*mm))

    # 카드 정보
    card_info = [
        ["본인회원명", "박 철 민", "본인회원 카드번호", "5412-****-****-7890"],
        ["가족회원명", "이 수 진", "가족카드 번호", "5412-****-****-7891"],
        ["카드상품명", "KB국민 탄탄대로 티타늄카드", "", ""],
        ["해지사유", "본인회원 요청", "해지일자", "2025년 11월 19일"],
    ]

    card_table = Table(card_info, colWidths=[30*mm, 50*mm, 35*mm, 50*mm])
    card_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), KOREAN_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#FFF8E1')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#FFF8E1')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#FFC107')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('SPAN', (1, 2), (3, 2)),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(card_table)
    elements.append(Spacer(1, 10*mm))

    # 안내문
    notice = """안녕하세요, KB국민카드입니다.

위 가족카드가 본인회원의 요청에 따라 해지되었음을 알려드립니다.

■ 해지 안내사항

1. 해지일(2025년 11월 19일) 이후 해당 가족카드의 모든 거래가 중단됩니다.
2. 해지 전 발생한 미결제 금액은 본인회원 결제계좌에서 정상 출금됩니다.
3. 해지된 가족카드는 폐기하여 주시기 바랍니다.
4. 가족회원 본인의 신용도에는 영향이 없습니다.

■ 문의사항

가족카드 해지와 관련하여 문의사항이 있으시면 KB국민카드 고객센터
(1588-1688)로 연락 주시기 바랍니다.

감사합니다."""

    elements.append(Paragraph(notice.replace('\n', '<br/>'), styles['KBody']))
    elements.append(Spacer(1, 15*mm))

    elements.append(Paragraph("2025년  11월  19일", styles['KCenter']))
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph("KB국민카드 주식회사", styles['KCenter']))
    elements.append(Spacer(1, 15*mm))

    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph("※ 본 통보서는 「여신전문금융업법」 제24조에 따라 발급되었습니다.", styles['KSmall']))
    elements.append(Paragraph("※ 문서확인번호: KB-2025111900458", styles['KSmall']))

    doc.build(elements)
    print(f"✅ 생성 완료: {output_path}")


def create_bank_transfer_record():
    """계좌이체 내역서 - 생활비 증빙"""

    output_path = OUTPUT_DIR / "계좌이체_내역서.pdf"
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        topMargin=15*mm,
        bottomMargin=15*mm,
        leftMargin=15*mm,
        rightMargin=15*mm
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='KTitle', fontName=KOREAN_FONT, fontSize=18, alignment=TA_CENTER, spaceAfter=5*mm))
    styles.add(ParagraphStyle(name='KSubtitle', fontName=KOREAN_FONT, fontSize=11, alignment=TA_LEFT, spaceBefore=3*mm))
    styles.add(ParagraphStyle(name='KBody', fontName=KOREAN_FONT, fontSize=9, leading=12))
    styles.add(ParagraphStyle(name='KSmall', fontName=KOREAN_FONT, fontSize=7, textColor=colors.grey))
    styles.add(ParagraphStyle(name='KRight', fontName=KOREAN_FONT, fontSize=9, alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name='KCenter', fontName=KOREAN_FONT, fontSize=9, alignment=TA_CENTER))

    elements = []

    # 신한은행 헤더
    elements.append(Paragraph("신한은행", styles['KTitle']))
    elements.append(Paragraph("www.shinhan.com | 고객센터 1599-8000", styles['KCenter']))
    elements.append(Spacer(1, 3*mm))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0046FF')))
    elements.append(Spacer(1, 8*mm))

    # 제목
    elements.append(Paragraph("계 좌 이 체 내 역 서", styles['KTitle']))
    elements.append(Paragraph("조회기간: 2025.08.01 ~ 2025.11.30", styles['KCenter']))
    elements.append(Spacer(1, 8*mm))

    # 계좌 정보
    acc_info = [
        ["예 금 주", "박 철 민", "계좌번호", "110-***-***456"],
        ["계좌종류", "급여통장(보통예금)", "발급일자", "2025.11.25"],
    ]
    acc_table = Table(acc_info, colWidths=[28*mm, 55*mm, 28*mm, 55*mm])
    acc_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), KOREAN_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E3F2FD')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#E3F2FD')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#0046FF')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(acc_table)
    elements.append(Spacer(1, 8*mm))

    # 이체 내역 - 생활비 명목
    elements.append(Paragraph("■ 이체 내역 (받는분: 이수진 / 계좌: 신한 110-***-***789)", styles['KSubtitle']))
    elements.append(Spacer(1, 2*mm))

    transfers = [
        ["No", "거래일시", "적요", "출금액", "잔액"],
        ["1", "2025.08.25 09:00", "생활비", "1,500,000", "2,394,660"],
        ["2", "2025.09.25 09:00", "생활비", "1,500,000", "2,394,660"],
        ["3", "2025.10.25 09:00", "생활비", "1,500,000", "2,394,660"],
        ["4", "2025.11.25 09:00", "생활비", "1,500,000", "2,394,660"],
    ]

    trans_table = Table(transfers, colWidths=[15*mm, 40*mm, 40*mm, 35*mm, 35*mm])
    trans_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), KOREAN_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0046FF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (3, 1), (4, -1), 'RIGHT'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#0046FF')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
    ]))
    elements.append(trans_table)
    elements.append(Spacer(1, 5*mm))

    # 요약
    summary = [
        ["조회기간 총 이체금액", "6,000,000 원 (4회)"],
        ["월평균 이체금액", "1,500,000 원"],
    ]
    sum_table = Table(summary, colWidths=[60*mm, 80*mm])
    sum_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), KOREAN_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFF3E0')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#FF6F00')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    elements.append(sum_table)
    elements.append(Spacer(1, 10*mm))

    # 참고사항
    note = """※ 참고사항
- 상기 이체내역은 예금주(박철민)가 이수진 앞으로 이체한 내역만 조회한 것입니다.
- 월 실수령 급여 약 389만원 중 생활비 명목으로 월 150만원만 이체하고 있습니다.
- 나머지 금액(약 239만원)의 사용처는 본 내역서에 포함되지 않습니다."""

    elements.append(Paragraph(note.replace('\n', '<br/>'), styles['KBody']))
    elements.append(Spacer(1, 15*mm))

    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph("※ 본 내역서는 「금융실명거래 및 비밀보장에 관한 법률」에 따라 발급되었습니다.", styles['KSmall']))
    elements.append(Paragraph("※ 문서확인번호: SH-2025112500892", styles['KSmall']))

    doc.build(elements)
    print(f"✅ 생성 완료: {output_path}")


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print("PDF 문서 생성 중... (시나리오 2: 가정폭력 + 경제적 학대)")
    create_medical_certificate()
    create_salary_statement()
    create_card_cancellation()
    create_bank_transfer_record()
    print("\n모든 PDF 생성 완료!")
