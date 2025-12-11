#!/usr/bin/env python3
"""
Database Seed Script for Development/Testing
005-lawyer-portal-pages Feature

Generates realistic mock data for:
- Users (lawyers, clients, detectives)
- Cases with case members
- Messages between users
- Calendar events
- Invoices
- Investigation records

Usage:
    cd backend
    python -m scripts.seed_dev_data
    # or
    python scripts/seed_dev_data.py
"""

import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add backend to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session  # noqa: E402

from app.db import session as db_session  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.db.models import (  # noqa: E402
    User, UserRole, UserStatus,
    Case, CaseStatus,
    CaseMember, CaseMemberRole,
    Message,
    CalendarEvent, CalendarEventType,
    Invoice, InvoiceStatus,
    InvestigationRecord, InvestigationRecordType,
    UserSettings,
)

# ============================================
# Seed Data Definitions
# ============================================

# Default password for all seed users
DEFAULT_PASSWORD = "test1234"

LAWYERS = [
    {"id": "user_lawyer001", "email": "kim.lawyer@leh.dev", "name": "김변호사", "role": UserRole.LAWYER},
    {"id": "user_lawyer002", "email": "lee.lawyer@leh.dev", "name": "이변호사", "role": UserRole.LAWYER},
    {"id": "user_lawyer003", "email": "park.lawyer@leh.dev", "name": "박변호사", "role": UserRole.LAWYER},
]

STAFF = [
    {"id": "user_staff001", "email": "jung.staff@leh.dev", "name": "정사무장", "role": UserRole.STAFF},
    {"id": "user_staff002", "email": "choi.staff@leh.dev", "name": "최파라리걸", "role": UserRole.STAFF},
]

CLIENTS = [
    {"id": "user_client001", "email": "hong.client@example.com", "name": "홍길동", "role": UserRole.CLIENT},
    {"id": "user_client002", "email": "kang.client@example.com", "name": "강감찬", "role": UserRole.CLIENT},
    {"id": "user_client003", "email": "shin.client@example.com", "name": "신사임당", "role": UserRole.CLIENT},
    {"id": "user_client004", "email": "yoo.client@example.com", "name": "유관순", "role": UserRole.CLIENT},
    {"id": "user_client005", "email": "ahn.client@example.com", "name": "안중근", "role": UserRole.CLIENT},
    {"id": "user_client006", "email": "kim.client@example.com", "name": "김유신", "role": UserRole.CLIENT},
    {"id": "user_client007", "email": "lee.client2@example.com", "name": "이순신", "role": UserRole.CLIENT},
    {"id": "user_client008", "email": "jang.client@example.com", "name": "장영실", "role": UserRole.CLIENT},
]

DETECTIVES = [
    {"id": "user_det001", "email": "oh.detective@leh.dev", "name": "오탐정", "role": UserRole.DETECTIVE},
    {"id": "user_det002", "email": "han.detective@leh.dev", "name": "한조사원", "role": UserRole.DETECTIVE},
    {"id": "user_det003", "email": "min.detective@leh.dev", "name": "민조사원", "role": UserRole.DETECTIVE},
]

ADMIN = [
    {"id": "user_admin001", "email": "admin@leh.dev", "name": "관리자", "role": UserRole.ADMIN},
]

CASES = [
    {
        "id": "case_divorce001",
        "title": "홍길동 vs 심청 이혼소송",
        "client_name": "홍길동",
        "description": "협의이혼 불성립으로 재판이혼 진행. 재산분할 및 양육권 쟁점.",
        "status": CaseStatus.ACTIVE,
        "created_by": "user_lawyer001",
        "members": [
            ("user_lawyer001", CaseMemberRole.OWNER),
            ("user_client001", CaseMemberRole.MEMBER),
            ("user_det001", CaseMemberRole.MEMBER),
            ("user_staff001", CaseMemberRole.VIEWER),
        ]
    },
    {
        "id": "case_divorce002",
        "title": "강감찬 vs 배우자 이혼소송",
        "client_name": "강감찬",
        "description": "배우자 불륜으로 인한 이혼소송. 위자료 청구 포함.",
        "status": CaseStatus.ACTIVE,
        "created_by": "user_lawyer001",
        "members": [
            ("user_lawyer001", CaseMemberRole.OWNER),
            ("user_client002", CaseMemberRole.MEMBER),
            ("user_det002", CaseMemberRole.MEMBER),
        ]
    },
    {
        "id": "case_divorce003",
        "title": "신사임당 이혼 및 재산분할",
        "client_name": "신사임당",
        "description": "고액 재산분할 사건. 부동산 감정 필요.",
        "status": CaseStatus.ACTIVE,
        "created_by": "user_lawyer002",
        "members": [
            ("user_lawyer002", CaseMemberRole.OWNER),
            ("user_client003", CaseMemberRole.MEMBER),
            ("user_staff002", CaseMemberRole.VIEWER),
        ]
    },
    {
        "id": "case_divorce004",
        "title": "유관순 양육권 분쟁",
        "client_name": "유관순",
        "description": "양육권 변경 청구. 면접교섭권 조정 필요.",
        "status": CaseStatus.IN_PROGRESS,
        "created_by": "user_lawyer002",
        "members": [
            ("user_lawyer002", CaseMemberRole.OWNER),
            ("user_client004", CaseMemberRole.MEMBER),
            ("user_det003", CaseMemberRole.MEMBER),
        ]
    },
    {
        "id": "case_divorce005",
        "title": "안중근 vs 배우자 협의이혼",
        "client_name": "안중근",
        "description": "협의이혼 진행 중. 재산분할 합의 대기.",
        "status": CaseStatus.ACTIVE,
        "created_by": "user_lawyer001",
        "members": [
            ("user_lawyer001", CaseMemberRole.OWNER),
            ("user_client005", CaseMemberRole.MEMBER),
        ]
    },
    {
        "id": "case_closed001",
        "title": "김유신 이혼소송 (완료)",
        "client_name": "김유신",
        "description": "이혼 확정. 재산분할 완료.",
        "status": CaseStatus.CLOSED,
        "created_by": "user_lawyer003",
        "members": [
            ("user_lawyer003", CaseMemberRole.OWNER),
            ("user_client006", CaseMemberRole.MEMBER),
        ]
    },
]


def create_messages(db: Session) -> list:
    """Create sample messages between users"""
    messages = []
    now = datetime.now(timezone.utc)

    message_data = [
        # Case 1 messages
        ("case_divorce001", "user_lawyer001", "user_client001", "안녕하세요, 홍길동님. 소송 준비 상황 안내드립니다.", now - timedelta(days=5)),
        ("case_divorce001", "user_client001", "user_lawyer001", "네, 감사합니다. 서류 준비는 어떻게 하면 될까요?", now - timedelta(days=5, hours=1)),
        ("case_divorce001", "user_lawyer001", "user_client001", "첨부파일로 필요 서류 목록 보내드렸습니다. 확인 부탁드립니다.", now - timedelta(days=4)),
        ("case_divorce001", "user_det001", "user_lawyer001", "김변호사님, 현장조사 완료했습니다. 보고서 정리 중입니다.", now - timedelta(days=2)),
        ("case_divorce001", "user_lawyer001", "user_det001", "수고하셨습니다. 빠른 시일 내에 보고서 부탁드립니다.", now - timedelta(days=2, hours=2)),

        # Case 2 messages
        ("case_divorce002", "user_lawyer001", "user_client002", "강감찬님, 상대방 측에서 조정을 제안해왔습니다.", now - timedelta(days=3)),
        ("case_divorce002", "user_client002", "user_lawyer001", "조정은 원하지 않습니다. 재판으로 진행해주세요.", now - timedelta(days=3, hours=5)),
        ("case_divorce002", "user_det002", "user_lawyer001", "증거자료 추가 확보했습니다. 중요한 내용입니다.", now - timedelta(days=1)),

        # Case 3 messages
        ("case_divorce003", "user_lawyer002", "user_client003", "부동산 감정 결과가 나왔습니다. 시가 15억원으로 평가되었습니다.", now - timedelta(hours=12)),
        ("case_divorce003", "user_client003", "user_lawyer002", "예상보다 높게 나왔네요. 분할 비율은 어떻게 될까요?", now - timedelta(hours=10)),
    ]

    for case_id, sender_id, recipient_id, content, created_at in message_data:
        msg = Message(
            case_id=case_id,
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content,
            created_at=created_at
        )
        messages.append(msg)

    return messages


def create_calendar_events(db: Session) -> list:
    """Create sample calendar events"""
    events = []
    now = datetime.now(timezone.utc)

    event_data = [
        # Lawyer 1 events
        ("user_lawyer001", "case_divorce001", "홍길동 사건 변론기일", CalendarEventType.COURT,
         now + timedelta(days=7, hours=10), "서울가정법원 301호", "첫 번째 변론기일"),
        ("user_lawyer001", "case_divorce002", "강감찬 사건 조정기일", CalendarEventType.COURT,
         now + timedelta(days=14, hours=14), "서울가정법원 조정실 2", "조정 불성립 시 본안 진행"),
        ("user_lawyer001", None, "신규 상담 - 박OO", CalendarEventType.MEETING,
         now + timedelta(days=2, hours=15), "사무실 상담실", "이혼 상담 예약"),
        ("user_lawyer001", "case_divorce005", "안중근 서류 검토 마감", CalendarEventType.DEADLINE,
         now + timedelta(days=5), None, "재산분할 합의서 최종 검토"),

        # Lawyer 2 events
        ("user_lawyer002", "case_divorce003", "신사임당 사건 감정인 심문", CalendarEventType.COURT,
         now + timedelta(days=21, hours=11), "서울가정법원 402호", "부동산 감정인 출석"),
        ("user_lawyer002", "case_divorce004", "유관순 면접교섭 조정", CalendarEventType.COURT,
         now + timedelta(days=10, hours=14), "가정법원 조정실", "양육권 관련 조정"),
        ("user_lawyer002", None, "변호사 교육 세미나", CalendarEventType.OTHER,
         now + timedelta(days=30, hours=9), "대한변호사협회", "가사소송 실무 교육"),

        # Detective events
        ("user_det001", "case_divorce001", "홍길동 사건 현장조사", CalendarEventType.OTHER,
         now - timedelta(days=2, hours=9), "강남구 역삼동", "상대방 거주지 조사"),
        ("user_det002", "case_divorce002", "강감찬 사건 증거수집", CalendarEventType.OTHER,
         now + timedelta(days=3, hours=10), "서초구 서초동", "추가 증거 확보"),
    ]

    for user_id, case_id, title, event_type, start_time, location, description in event_data:
        event = CalendarEvent(
            user_id=user_id,
            case_id=case_id,
            title=title,
            event_type=event_type,
            start_time=start_time,
            end_time=start_time + timedelta(hours=2) if event_type != CalendarEventType.DEADLINE else None,
            location=location,
            description=description,
        )
        events.append(event)

    return events


def create_invoices(db: Session) -> list:
    """Create sample invoices"""
    invoices = []
    now = datetime.now(timezone.utc)

    invoice_data = [
        # Case 1 invoices
        ("case_divorce001", "user_client001", "user_lawyer001", "3000000", InvoiceStatus.PAID,
         "착수금", now - timedelta(days=30), now - timedelta(days=28)),
        ("case_divorce001", "user_client001", "user_lawyer001", "2000000", InvoiceStatus.PENDING,
         "변론기일 수임료", now + timedelta(days=14), None),

        # Case 2 invoices
        ("case_divorce002", "user_client002", "user_lawyer001", "5000000", InvoiceStatus.PAID,
         "착수금", now - timedelta(days=20), now - timedelta(days=18)),
        ("case_divorce002", "user_client002", "user_lawyer001", "3000000", InvoiceStatus.PENDING,
         "추가 증거수집 비용", now + timedelta(days=7), None),

        # Case 3 invoices
        ("case_divorce003", "user_client003", "user_lawyer002", "10000000", InvoiceStatus.PAID,
         "착수금 (고액재산분할)", now - timedelta(days=15), now - timedelta(days=14)),
        ("case_divorce003", "user_client003", "user_lawyer002", "2000000", InvoiceStatus.PENDING,
         "감정비용", now + timedelta(days=10), None),

        # Case 4 invoices
        ("case_divorce004", "user_client004", "user_lawyer002", "2000000", InvoiceStatus.PENDING,
         "양육권 변경 착수금", now + timedelta(days=7), None),

        # Closed case - all paid
        ("case_closed001", "user_client006", "user_lawyer003", "4000000", InvoiceStatus.PAID,
         "착수금", now - timedelta(days=90), now - timedelta(days=88)),
        ("case_closed001", "user_client006", "user_lawyer003", "6000000", InvoiceStatus.PAID,
         "성공보수", now - timedelta(days=30), now - timedelta(days=25)),
    ]

    for case_id, client_id, lawyer_id, amount, status, desc, due_date, paid_at in invoice_data:
        invoice = Invoice(
            case_id=case_id,
            client_id=client_id,
            lawyer_id=lawyer_id,
            amount=amount,
            status=status,
            description=desc,
            due_date=due_date,
            paid_at=paid_at,
        )
        invoices.append(invoice)

    return invoices


def create_investigation_records(db: Session) -> list:
    """Create sample investigation records"""
    records = []
    now = datetime.now(timezone.utc)

    record_data = [
        # Case 1 - Detective 1
        ("case_divorce001", "user_det001", InvestigationRecordType.LOCATION,
         "상대방 차량 이동 경로 추적", "37.5012", "127.0396", "서울시 강남구 역삼동", now - timedelta(days=3)),
        ("case_divorce001", "user_det001", InvestigationRecordType.PHOTO,
         "상대방 거주지 외관 촬영", "37.5015", "127.0400", "서울시 강남구 역삼동 123-45", now - timedelta(days=2)),
        ("case_divorce001", "user_det001", InvestigationRecordType.MEMO,
         "상대방은 평일 오후 6시경 퇴근, 주말에는 외출 빈번함", None, None, None, now - timedelta(days=1)),

        # Case 2 - Detective 2
        ("case_divorce002", "user_det002", InvestigationRecordType.PHOTO,
         "불륜 증거 사진 확보", "37.4979", "127.0276", "서울시 서초구 서초동", now - timedelta(days=5)),
        ("case_divorce002", "user_det002", InvestigationRecordType.AUDIO,
         "목격자 진술 녹음", None, None, None, now - timedelta(days=4)),
        ("case_divorce002", "user_det002", InvestigationRecordType.MEMO,
         "추가 목격자 2명 확인. 연락처 확보 완료.", None, None, None, now - timedelta(days=1)),

        # Case 4 - Detective 3
        ("case_divorce004", "user_det003", InvestigationRecordType.LOCATION,
         "아이 등하교 경로 확인", "37.5665", "126.9780", "서울시 중구 명동", now - timedelta(days=7)),
        ("case_divorce004", "user_det003", InvestigationRecordType.MEMO,
         "양육환경 적합성 조사 진행 중", None, None, None, now - timedelta(days=3)),
    ]

    for case_id, det_id, record_type, content, lat, lng, address, recorded_at in record_data:
        record = InvestigationRecord(
            case_id=case_id,
            detective_id=det_id,
            record_type=record_type,
            content=content,
            location_lat=lat,
            location_lng=lng,
            location_address=address,
            recorded_at=recorded_at,
        )
        records.append(record)

    return records


def create_user_settings(db: Session, users: list) -> list:
    """Create default settings for all users"""
    settings = []
    for user in users:
        setting = UserSettings(
            user_id=user.id,
            notification_email=True,
            notification_push=True,
            notification_sms=False,
            theme="light",
            language="ko",
        )
        settings.append(setting)
    return settings


def seed_database():
    """Main seeding function"""
    print("=" * 60)
    print("LEH Database Seed Script")
    print("=" * 60)

    # Initialize database connection
    print("\nInitializing database connection...")
    db_session.init_db()

    db = db_session.SessionLocal()

    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            response = input(f"\n{existing_users} users already exist. Clear and reseed? (y/N): ")
            if response.lower() != 'y':
                print("Aborted.")
                return

            # Clear existing data in order (respecting foreign keys)
            print("\nClearing existing data...")
            db.query(InvestigationRecord).delete()
            db.query(Invoice).delete()
            db.query(CalendarEvent).delete()
            db.query(Message).delete()
            db.query(UserSettings).delete()
            db.query(CaseMember).delete()
            db.query(Case).delete()
            db.query(User).delete()
            db.commit()
            print("Existing data cleared.")

        # Create users
        print("\n[1/7] Creating users...")
        all_user_data = ADMIN + LAWYERS + STAFF + CLIENTS + DETECTIVES
        users = []
        hashed_pw = hash_password(DEFAULT_PASSWORD)

        for user_data in all_user_data:
            user = User(
                id=user_data["id"],
                email=user_data["email"],
                name=user_data["name"],
                role=user_data["role"],
                status=UserStatus.ACTIVE,
                hashed_password=hashed_pw,
            )
            users.append(user)
            db.add(user)

        db.commit()
        print(f"  Created {len(users)} users")

        # Create cases
        print("\n[2/7] Creating cases...")
        cases = []
        for case_data in CASES:
            case = Case(
                id=case_data["id"],
                title=case_data["title"],
                client_name=case_data["client_name"],
                description=case_data["description"],
                status=case_data["status"],
                created_by=case_data["created_by"],
            )
            cases.append(case)
            db.add(case)

        db.commit()
        print(f"  Created {len(cases)} cases")

        # Create case members
        print("\n[3/7] Creating case members...")
        member_count = 0
        for case_data in CASES:
            for user_id, role in case_data["members"]:
                member = CaseMember(
                    case_id=case_data["id"],
                    user_id=user_id,
                    role=role,
                )
                db.add(member)
                member_count += 1

        db.commit()
        print(f"  Created {member_count} case memberships")

        # Create messages
        print("\n[4/7] Creating messages...")
        messages = create_messages(db)
        for msg in messages:
            db.add(msg)
        db.commit()
        print(f"  Created {len(messages)} messages")

        # Create calendar events
        print("\n[5/7] Creating calendar events...")
        events = create_calendar_events(db)
        for event in events:
            db.add(event)
        db.commit()
        print(f"  Created {len(events)} calendar events")

        # Create invoices
        print("\n[6/7] Creating invoices...")
        invoices = create_invoices(db)
        for invoice in invoices:
            db.add(invoice)
        db.commit()
        print(f"  Created {len(invoices)} invoices")

        # Create investigation records
        print("\n[7/7] Creating investigation records...")
        records = create_investigation_records(db)
        for record in records:
            db.add(record)
        db.commit()
        print(f"  Created {len(records)} investigation records")

        # Summary
        print("\n" + "=" * 60)
        print("SEED COMPLETE!")
        print("=" * 60)
        print(f"""
Summary:
  - Users: {len(users)}
    - Admins: {len(ADMIN)}
    - Lawyers: {len(LAWYERS)}
    - Staff: {len(STAFF)}
    - Clients: {len(CLIENTS)}
    - Detectives: {len(DETECTIVES)}
  - Cases: {len(cases)}
  - Case Members: {member_count}
  - Messages: {len(messages)}
  - Calendar Events: {len(events)}
  - Invoices: {len(invoices)}
  - Investigation Records: {len(records)}

Default login credentials:
  Email: kim.lawyer@leh.dev
  Password: {DEFAULT_PASSWORD}

Other test accounts:
  - lee.lawyer@leh.dev (Lawyer)
  - hong.client@example.com (Client)
  - oh.detective@leh.dev (Detective)
  - admin@leh.dev (Admin)
  All use password: {DEFAULT_PASSWORD}
""")

    except Exception as e:
        print(f"\nError during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
