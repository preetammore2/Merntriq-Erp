from __future__ import annotations

import base64
from datetime import time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import UserRole
from apps.core.models import (
    AcademicEvent,
    AcademicEventType,
    AcademicSession,
    AcademicWorkStatus,
    Announcement,
    AnnouncementAudience,
    AssignedWork,
    AssignmentSubmission,
    AssignmentSubmissionStatus,
    AttendanceCaptureMethod,
    AttendanceDevice,
    AttendanceRecord,
    AttendanceStatus,
    AuditAction,
    AuditEvent,
    Campus,
    CampusMemberRole,
    CampusMembership,
    ClassSection,
    CommunicationSetting,
    DeviceSyncLog,
    DeviceSyncStatus,
    ExamSchedule,
    ExamScheduleStatus,
    ExamSubjectSetup,
    ExamType,
    FeeAssignment,
    FeeStructure,
    FinanceEvent,
    FinanceEventType,
    GatewayProvider,
    LearningResource,
    MessageChannel,
    MessageTemplate,
    Payment,
    PaymentGatewayConfig,
    PaymentMethod,
    PaymentTransaction,
    PlatformSetting,
    ResourceType,
    ResultRecord,
    ResultReviewStatus,
    StaffAttendanceRecord,
    StaffAttendanceStatus,
    StaffEmploymentType,
    StaffProfile,
    StaffProfileStatus,
    Student,
    Subject,
    TeacherSubjectAllocation,
    TimetableSlot,
    TransactionStatus,
    Weekday,
)


DEMO_CODE = "DEMO360"
DEMO_MARKER_KEY = "demo_data_marker"
DEMO_TAG = "phase8_client_demo"
DEMO_PASSWORD = "Demo@12345"

DEMO_USERNAMES = (
    "demo.schooladmin",
    "demo.account",
    "demo.teacher.math",
    "demo.teacher.science",
    "demo.student.aarav",
    "demo.student.mira",
    "demo.student.kabir",
)


def svg_data_url(label: str, background: str = "#0f172a", foreground: str = "#ffffff") -> str:
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="640" height="240" viewBox="0 0 640 240">
  <rect width="640" height="240" rx="24" fill="{background}"/>
  <text x="48" y="138" font-family="Arial, sans-serif" font-size="54" font-weight="700" fill="{foreground}">{label}</text>
  <text x="52" y="180" font-family="Arial, sans-serif" font-size="22" fill="{foreground}" opacity="0.78">Demo data - removable</text>
</svg>"""
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def demo_file_url(label: str) -> str:
    content = f"%PDF-1.4\n% MentriQ360 demo file\n1 0 obj << /Type /Catalog >> endobj\n% {label}\n%%EOF\n"
    return f"data:application/pdf;base64,{base64.b64encode(content.encode('utf-8')).decode('ascii')}"


class Command(BaseCommand):
    help = "Seed or remove one clearly marked MentriQ360 demo school."

    def add_arguments(self, parser):
        parser.add_argument("--code", default=DEMO_CODE, help="Demo school code. Defaults to DEMO360.")
        parser.add_argument("--password", default=DEMO_PASSWORD, help="Password assigned to demo users.")
        parser.add_argument("--remove", action="store_true", help="Remove the demo school and demo users.")
        parser.add_argument("--reset", action="store_true", help="Remove the existing demo school before seeding it again.")

    def handle(self, *args, **options):
        code = options["code"].strip().upper()
        password = options["password"]
        if not code:
            raise CommandError("Demo school code cannot be empty.")

        if options["remove"]:
            removed = self.remove_demo_school(code)
            self.stdout.write(self.style.SUCCESS(f"Removed demo school {code}: {removed} records/users root objects deleted."))
            return

        if options["reset"]:
            self.remove_demo_school(code, allow_missing=True)

        with transaction.atomic():
            campus = self.seed_demo_school(code=code, password=password)

        self.stdout.write(self.style.SUCCESS(f"Demo school ready: {campus.name} ({campus.code})"))
        self.stdout.write("Demo login password for all demo users: " + password)
        for username in DEMO_USERNAMES:
            self.stdout.write(f"  - {username}")
        remove_command = "python manage.py seed_demo_school --remove"
        if code != DEMO_CODE:
            remove_command = f"python manage.py seed_demo_school --code {code} --remove"
        self.stdout.write(f"Remove later with: {remove_command}")

    def is_demo_campus(self, campus: Campus) -> bool:
        return bool(
            campus.enabled_modules.get("demoData")
            or PlatformSetting.objects.filter(campus=campus, key=DEMO_MARKER_KEY).exists()
        )

    def remove_demo_school(self, code: str, *, allow_missing: bool = False) -> int:
        campus = Campus.objects.filter(code=code).first()
        if not campus:
            if allow_missing:
                return 0
            raise CommandError(f"No school with code {code} exists.")
        if not self.is_demo_campus(campus):
            raise CommandError(f"School {code} is not marked as demo data. Refusing to remove it.")

        User = get_user_model()
        demo_users = User.objects.filter(username__in=DEMO_USERNAMES)
        school_users = User.objects.filter(school=campus).exclude(role=UserRole.SUPER_ADMIN)
        deleted_users, _ = (demo_users | school_users).distinct().delete()
        AuditEvent.objects.filter(metadata__demoTag=DEMO_TAG).delete()
        deleted_campus, _ = campus.delete()
        return deleted_users + deleted_campus

    def seed_demo_school(self, *, code: str, password: str) -> Campus:
        existing = Campus.objects.filter(code=code).first()
        if existing and not self.is_demo_campus(existing):
            raise CommandError(f"School code {code} already exists and is not marked as demo data.")

        today = timezone.localdate()
        campus, _ = Campus.objects.update_or_create(
            code=code,
            defaults={
                "name": "MentriQ360 Demo School",
                "address": "Demo Campus Road, Knowledge Park",
                "city": "Pune",
                "state": "Maharashtra",
                "pincode": "411001",
                "contact_email": "demo.school@mentriq360.example",
                "contact_phone": "+91-90000-00001",
                "website": "https://demo.mentriq360.example",
                "principal_name": "Dr. Demo Principal",
                "logo_url": svg_data_url("M360 Demo", "#0f766e"),
                "logo_alt_text": "MentriQ360 demo school logo",
                "banner_url": svg_data_url("MentriQ360 Demo School", "#1d4ed8"),
                "status": "active",
                "subscription_plan": "Demo Enterprise",
                "subscription_status": "demo",
                "monthly_subscription_amount": Decimal("0.00"),
                "billing_due_date": today + timedelta(days=30),
                "academic_year_label": "2026-2027",
                "database_alias": f"campus_{code.lower()}",
                "database_name": f"mentriq360_{code.lower()}",
                "enabled_modules": {
                    "demoData": True,
                    "academics": True,
                    "finance": True,
                    "teacherPortal": True,
                    "studentPortal": True,
                    "communication": True,
                    "ai": True,
                    "hardwareAttendance": True,
                },
                "payment_gateway_settings": {"demo": True, "provider": "razorpay"},
                "messaging_settings": {"demo": True, "channels": ["email", "sms", "whatsapp"]},
                "attendance_hardware_settings": {"demo": True, "deviceType": "rfid"},
            },
        )

        super_admin = get_user_model().objects.filter(role=UserRole.SUPER_ADMIN).first()
        school_admin = self.upsert_user(
            "demo.schooladmin",
            UserRole.SCHOOL_ADMIN,
            "Demo",
            "School Admin",
            "demo.schooladmin@mentriq360.example",
            password,
            campus,
            is_staff=True,
        )
        account_user = self.upsert_user(
            "demo.account",
            UserRole.ACCOUNT,
            "Demo",
            "Account",
            "demo.account@mentriq360.example",
            password,
            campus,
            is_staff=True,
        )
        teacher_math = self.upsert_user(
            "demo.teacher.math",
            UserRole.TEACHER,
            "Ananya",
            "Rao",
            "demo.teacher.math@mentriq360.example",
            password,
            campus,
        )
        teacher_science = self.upsert_user(
            "demo.teacher.science",
            UserRole.TEACHER,
            "Rohan",
            "Mehta",
            "demo.teacher.science@mentriq360.example",
            password,
            campus,
        )
        student_users = {
            "Aarav": self.upsert_user("demo.student.aarav", UserRole.STUDENT, "Aarav", "Patil", "demo.student.aarav@mentriq360.example", password, campus),
            "Mira": self.upsert_user("demo.student.mira", UserRole.STUDENT, "Mira", "Shah", "demo.student.mira@mentriq360.example", password, campus),
            "Kabir": self.upsert_user("demo.student.kabir", UserRole.STUDENT, "Kabir", "Sen", "demo.student.kabir@mentriq360.example", password, campus),
        }

        self.membership(campus, school_admin, CampusMemberRole.IT_ADMIN, can_manage_users=True, can_configure_attendance=True)
        self.membership(campus, account_user, CampusMemberRole.FINANCE_ADMIN)
        self.membership(campus, teacher_math, CampusMemberRole.TEACHER)
        self.membership(campus, teacher_science, CampusMemberRole.TEACHER)

        for user, employee_code, designation, department in (
            (account_user, f"{code}-EMP-001", "Accounts Officer - Demo", "Finance"),
            (teacher_math, f"{code}-EMP-002", "Mathematics Teacher - Demo", "Academics"),
            (teacher_science, f"{code}-EMP-003", "Science Teacher - Demo", "Academics"),
        ):
            StaffProfile.objects.update_or_create(
                user=user,
                defaults={
                    "campus": campus,
                    "employee_code": employee_code,
                    "designation": designation,
                    "department": department,
                    "joining_date": today - timedelta(days=365),
                    "employment_type": StaffEmploymentType.FULL_TIME,
                    "qualification": "Demo qualification",
                    "emergency_contact": "+91-90000-00999",
                    "status": StaffProfileStatus.ACTIVE,
                },
            )

        session, _ = AcademicSession.objects.update_or_create(
            campus=campus,
            name="Demo Academic Year 2026-2027",
            defaults={"start_date": today.replace(month=4, day=1), "end_date": today.replace(year=today.year + 1, month=3, day=31), "is_active": True},
        )
        grade5, _ = ClassSection.objects.update_or_create(
            campus=campus,
            session=session,
            grade_name="Grade 5",
            section_name="A",
            defaults={"class_teacher": teacher_math},
        )
        grade6, _ = ClassSection.objects.update_or_create(
            campus=campus,
            session=session,
            grade_name="Grade 6",
            section_name="A",
            defaults={"class_teacher": teacher_science},
        )

        subjects = {
            "mathematics": self.subject(campus, "Mathematics", "MATH", "Grade 5"),
            "science": self.subject(campus, "Science", "SCI", "Grade 5"),
            "english": self.subject(campus, "English", "ENG", "Grade 6"),
        }
        self.allocation(campus, grade5, teacher_math, "Mathematics", 6)
        self.allocation(campus, grade5, teacher_science, "Science", 5)
        self.allocation(campus, grade6, teacher_science, "English", 5)
        self.timetable(campus, grade5, teacher_math, "Mathematics", Weekday.MONDAY, time(9, 0), time(9, 45), "Room 5A")
        self.timetable(campus, grade5, teacher_science, "Science", Weekday.TUESDAY, time(10, 0), time(10, 45), "Lab 1")
        self.timetable(campus, grade6, teacher_science, "English", Weekday.WEDNESDAY, time(11, 0), time(11, 45), "Room 6A")

        students = [
            self.student(campus, grade5, student_users["Aarav"], f"{code}-STU-001", "Aarav", "Patil", today.replace(year=today.year - 11)),
            self.student(campus, grade5, student_users["Mira"], f"{code}-STU-002", "Mira", "Shah", today.replace(year=today.year - 11)),
            self.student(campus, grade6, student_users["Kabir"], f"{code}-STU-003", "Kabir", "Sen", today.replace(year=today.year - 12)),
        ]

        device, _ = AttendanceDevice.objects.update_or_create(
            device_code=f"{code}-RFID-001",
            defaults={
                "campus": campus,
                "name": "Demo RFID Gate",
                "device_type": AttendanceCaptureMethod.CARD_SCAN,
                "location": "Main Gate",
                "provider": "Demo RFID",
                "status": "active",
                "configured_by": school_admin,
            },
        )
        DeviceSyncLog.objects.update_or_create(
            device=device,
            log_type="demo_sync",
            defaults={
                "campus": campus,
                "status": DeviceSyncStatus.SUCCESS,
                "payload": {"demo": True, "records": 6},
                "synced_at": timezone.now(),
                "created_by": school_admin,
            },
        )

        for index, student in enumerate(students):
            AttendanceRecord.objects.update_or_create(
                student=student,
                date=today,
                subject="Mathematics" if student.section_id == grade5.id else "English",
                defaults={
                    "section": student.section,
                    "status": [AttendanceStatus.PRESENT, AttendanceStatus.LATE, AttendanceStatus.PRESENT][index],
                    "marked_by": teacher_math if student.section_id == grade5.id else teacher_science,
                    "capture_method": AttendanceCaptureMethod.MANUAL,
                },
            )
        StaffAttendanceRecord.objects.update_or_create(
            campus=campus,
            staff_user=teacher_math,
            date=today,
            defaults={"clock_in": time(8, 15), "clock_out": time(15, 45), "status": StaffAttendanceStatus.PRESENT, "capture_method": AttendanceCaptureMethod.MANUAL, "marked_by": school_admin},
        )

        fee_structure, _ = FeeStructure.objects.update_or_create(
            campus=campus,
            section=grade5,
            title="Demo Quarterly Tuition Fee",
            defaults={"description": "Demo fee structure for client walkthroughs.", "amount": Decimal("15000.00"), "late_fee": Decimal("500.00"), "discount_amount": Decimal("0.00"), "due_day": 10, "is_active": True, "created_by": account_user},
        )
        fee_assignments = []
        for index, student in enumerate(students[:2], start=1):
            assignment, _ = FeeAssignment.objects.update_or_create(
                invoice_number=f"{code}-INV-00{index}",
                defaults={
                    "fee_structure": fee_structure,
                    "student": student,
                    "title": fee_structure.title,
                    "amount": fee_structure.amount,
                    "discount_amount": Decimal("0.00"),
                    "late_fee": Decimal("0.00"),
                    "due_date": today + timedelta(days=14),
                },
            )
            fee_assignments.append(assignment)

        Payment.objects.update_or_create(
            receipt_number=f"{code}-REC-001",
            defaults={
                "campus": campus,
                "fee_assignment": fee_assignments[0],
                "amount_paid": Decimal("15000.00"),
                "discount_amount": Decimal("0.00"),
                "late_fee": Decimal("0.00"),
                "paid_on": today,
                "payment_method": PaymentMethod.ONLINE,
                "reference_number": "DEMO-PAY-001",
                "payment_status": TransactionStatus.SUCCESS,
                "gateway_name": "razorpay",
                "gateway_order_id": f"order_{code.lower()}_001",
                "transaction_id": f"pay_{code.lower()}_001",
                "webhook_verified": True,
                "collected_by": account_user,
            },
        )
        Payment.objects.update_or_create(
            receipt_number=f"{code}-REC-002",
            defaults={
                "campus": campus,
                "fee_assignment": fee_assignments[1],
                "amount_paid": Decimal("5000.00"),
                "discount_amount": Decimal("0.00"),
                "late_fee": Decimal("0.00"),
                "paid_on": today,
                "payment_method": PaymentMethod.CASH,
                "reference_number": "DEMO-CASH-001",
                "payment_status": TransactionStatus.SUCCESS,
                "gateway_name": "",
                "transaction_id": f"cash_{code.lower()}_001",
                "webhook_verified": False,
                "collected_by": account_user,
            },
        )
        PaymentTransaction.objects.update_or_create(
            gateway_order_id=f"order_{code.lower()}_001",
            defaults={
                "campus": campus,
                "student": fee_assignments[0].student,
                "fee_assignment": fee_assignments[0],
                "provider": "razorpay",
                "method": PaymentMethod.ONLINE,
                "amount": Decimal("15000.00"),
                "currency": "INR",
                "status": TransactionStatus.SUCCESS,
                "gateway_name": "razorpay",
                "gateway_payment_id": f"pay_{code.lower()}_001",
                "transaction_id": f"pay_{code.lower()}_001",
                "receipt_number": f"{code}-REC-001",
                "invoice_number": f"{code}-INV-001",
                "webhook_verified": True,
                "paid_at": timezone.now(),
                "raw_payload": {"demo": True},
                "created_by": account_user,
            },
        )
        FinanceEvent.objects.update_or_create(
            campus=campus,
            event_type=FinanceEventType.FEE_PAID,
            payload={"demo": True, "receiptNumber": f"{code}-REC-001", "amount": "15000.00"},
            defaults={"created_by": account_user},
        )

        gateway, _ = PaymentGatewayConfig.objects.update_or_create(
            campus=campus,
            provider=GatewayProvider.RAZORPAY,
            defaults={"key_id": "rzp_test_demo_client_ready", "upi_id": "demo@upi", "allowed_methods": ["upi", "card", "net_banking", "wallet"], "is_active": True, "created_by": account_user},
        )
        gateway.set_key_secret("demo_razorpay_secret_not_for_production")
        gateway.set_webhook_secret("demo_webhook_secret_not_for_production")
        gateway.save()

        self.communication(campus, MessageChannel.EMAIL, "Demo SMTP", school_admin, smtp_host="smtp.demo.example", smtp_port=587, smtp_username="demo@mentriq360.example", smtp_password="demo_smtp_password")
        self.communication(campus, MessageChannel.SMS, "Demo SMS API", school_admin, api_url="https://sms.demo.example/send", api_key="demo_sms_key", api_secret="demo_sms_secret", sender_id="M360DM")
        self.communication(campus, MessageChannel.WHATSAPP, "Demo WhatsApp API", school_admin, api_url="https://graph.demo.example/messages", api_key="demo_whatsapp_token", whatsapp_phone_number_id="demo-phone-number-id")
        self.message_template(campus, "Demo Fee Reminder", "fee_reminder", MessageChannel.EMAIL, "Fee reminder for {{studentName}}", "Dear {{studentName}}, {{schoolName}} has a pending fee of {{feeAmount}} due by {{dueDate}}.", school_admin)
        self.message_template(campus, "Demo Result Published", "result_published", MessageChannel.WHATSAPP, "", "Result is published for {{studentName}}. Download: {{resultLink}}", school_admin)

        LearningResource.objects.update_or_create(
            section=grade5,
            title="Demo Mathematics Notes",
            subject="Mathematics",
            defaults={"uploaded_by": teacher_math, "resource_type": ResourceType.NOTES, "description": "Fractions and decimals notes for demo students.", "file_url": demo_file_url("Demo Mathematics Notes"), "file_name": "demo-math-notes.pdf", "file_content_type": "application/pdf", "published_on": today, "is_published": True},
        )
        assignment, _ = AssignedWork.objects.update_or_create(
            section=grade5,
            title="Demo Fractions Worksheet",
            subject="Mathematics",
            defaults={"assigned_by": teacher_math, "description": "Complete exercises 1 to 10. Demo assignment.", "due_date": today + timedelta(days=5), "status": AcademicWorkStatus.PUBLISHED, "file_url": demo_file_url("Demo Fractions Worksheet"), "file_name": "demo-fractions-worksheet.pdf", "file_content_type": "application/pdf", "published_on": today},
        )
        AssignmentSubmission.objects.update_or_create(
            assignment=assignment,
            student=students[0],
            defaults={"submitted_by": students[0].user, "file_url": demo_file_url("Aarav Demo Submission"), "file_name": "aarav-demo-submission.pdf", "file_content_type": "application/pdf", "notes": "Demo submission uploaded from student portal.", "status": AssignmentSubmissionStatus.CHECKED, "remarks": "Good work in the demo submission.", "checked_by": teacher_math, "checked_at": timezone.now()},
        )
        for student, score, grade in ((students[0], Decimal("88.00"), "A"), (students[1], Decimal("76.00"), "B+"), (students[2], Decimal("82.00"), "A-")):
            ResultRecord.objects.update_or_create(
                student=student,
                exam_name="Demo Unit Test",
                subject="Mathematics" if student.section_id == grade5.id else "English",
                defaults={"recorded_by": teacher_math if student.section_id == grade5.id else teacher_science, "score": score, "max_score": Decimal("100.00"), "grade": grade, "remarks": "Demo result for client walkthrough.", "published_on": today, "is_published": True, "review_status": ResultReviewStatus.APPROVED, "reviewed_by": school_admin, "reviewed_at": timezone.now(), "review_note": "Approved for demo."},
            )
        exam_type, _ = ExamType.objects.update_or_create(campus=campus, name="Demo Unit Test", defaults={"description": "Demo assessment cycle.", "is_active": True})
        ExamSubjectSetup.objects.update_or_create(campus=campus, exam_type=exam_type, section=grade5, subject=subjects["mathematics"], defaults={"max_marks": Decimal("100.00"), "pass_marks": Decimal("33.00"), "weightage": Decimal("100.00"), "is_active": True})
        ExamSchedule.objects.update_or_create(campus=campus, exam_type=exam_type, section=grade5, subject=subjects["mathematics"], exam_date=today + timedelta(days=10), start_time=time(9, 30), defaults={"title": "Demo Mathematics Unit Test", "end_time": time(10, 30), "max_marks": Decimal("100.00"), "venue": "Room 5A", "instructions": "Demo exam schedule for walkthrough.", "status": ExamScheduleStatus.PUBLISHED, "created_by": school_admin})

        Announcement.objects.update_or_create(
            campus=campus,
            title="Demo School Notice",
            defaults={"message": "This is a demo notice. Demo data can be removed with seed_demo_school --remove.", "audience": AnnouncementAudience.ALL, "created_by": school_admin, "is_active": True, "publish_on": timezone.now()},
        )
        AcademicEvent.objects.update_or_create(
            campus=campus,
            event_type=AcademicEventType.NOTICE_PUBLISHED,
            payload={"demo": True, "title": "Demo School Notice"},
            defaults={"created_by": school_admin},
        )
        PlatformSetting.objects.update_or_create(
            campus=campus,
            key=DEMO_MARKER_KEY,
            defaults={
                "value": {
                    "demo": True,
                    "demoTag": DEMO_TAG,
                    "createdFor": "Phase 8 client handover",
                    "removeCommand": f"python manage.py seed_demo_school --code {code} --remove",
                    "users": list(DEMO_USERNAMES),
                },
                "created_by": super_admin or school_admin,
            },
        )
        AuditEvent.objects.update_or_create(
            entity_type="Campus",
            entity_id=str(campus.id),
            action=AuditAction.CREATE,
            metadata__demoTag=DEMO_TAG,
            defaults={
                "actor": super_admin or school_admin,
                "summary": "Seeded MentriQ360 demo school for client handover",
                "metadata": {"demo": True, "demoTag": DEMO_TAG, "campusCode": campus.code},
            },
        )
        return campus

    def upsert_user(self, username: str, role: str, first_name: str, last_name: str, email: str, password: str, campus: Campus, *, is_staff: bool = False):
        User = get_user_model()
        user, _ = User.objects.get_or_create(username=username)
        user.role = role
        user.school = campus
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.is_staff = is_staff
        user.is_active = True
        user.must_change_password = False
        user.phone_number = "+91-90000-00000"
        user.address = "Demo address - removable"
        user.city = campus.city
        user.state = campus.state
        user.set_password(password)
        user.save()
        return user

    def membership(self, campus: Campus, user, role: str, *, can_manage_users: bool = False, can_configure_attendance: bool = False):
        CampusMembership.objects.update_or_create(
            campus=campus,
            user=user,
            role=role,
            defaults={"is_primary": True, "can_manage_users": can_manage_users, "can_configure_attendance": can_configure_attendance},
        )

    def subject(self, campus: Campus, name: str, code: str, grade_name: str) -> Subject:
        subject, _ = Subject.objects.update_or_create(
            campus=campus,
            name=name,
            grade_name=grade_name,
            defaults={"code": code, "description": "Demo subject", "is_active": True},
        )
        return subject

    def allocation(self, campus: Campus, section: ClassSection, teacher, subject: str, weekly_periods: int):
        TeacherSubjectAllocation.objects.update_or_create(
            campus=campus,
            section=section,
            teacher=teacher,
            subject=subject,
            defaults={"weekly_periods": weekly_periods, "is_active": True},
        )

    def timetable(self, campus: Campus, section: ClassSection, teacher, subject: str, day: int, start: time, end: time, room: str):
        TimetableSlot.objects.update_or_create(
            section=section,
            day_of_week=day,
            start_time=start,
            defaults={"campus": campus, "teacher": teacher, "subject": subject, "end_time": end, "room": room, "effective_from": timezone.localdate()},
        )

    def student(self, campus: Campus, section: ClassSection, user, admission_number: str, first_name: str, last_name: str, dob) -> Student:
        student, _ = Student.objects.update_or_create(
            admission_number=admission_number,
            defaults={
                "campus": campus,
                "section": section,
                "user": user,
                "first_name": first_name,
                "last_name": last_name,
                "date_of_birth": dob,
                "photo_url": svg_data_url(first_name, "#7c2d12"),
                "father_name": f"Demo Father {first_name}",
                "mother_name": f"Demo Mother {first_name}",
                "contact_email": user.email,
                "phone_number": "+91-90000-00100",
                "address": "Demo student address - removable",
                "blood_group": "O+",
                "medical_notes": "Demo record only",
                "status": "active",
            },
        )
        return student

    def communication(self, campus: Campus, channel: str, provider_name: str, created_by, **values):
        setting, _ = CommunicationSetting.objects.update_or_create(
            campus=campus,
            channel=channel,
            defaults={
                "provider_name": provider_name,
                "sender_id": values.get("sender_id", "M360DM"),
                "api_url": values.get("api_url", ""),
                "smtp_host": values.get("smtp_host", ""),
                "smtp_port": values.get("smtp_port"),
                "smtp_username": values.get("smtp_username", ""),
                "whatsapp_phone_number_id": values.get("whatsapp_phone_number_id", ""),
                "is_active": True,
                "created_by": created_by,
            },
        )
        setting.set_api_key(values.get("api_key", ""))
        setting.set_api_secret(values.get("api_secret", ""))
        setting.set_smtp_password(values.get("smtp_password", ""))
        setting.save()

    def message_template(self, campus: Campus, name: str, trigger: str, channel: str, subject: str, body: str, created_by):
        MessageTemplate.objects.update_or_create(
            campus=campus,
            name=name,
            channel=channel,
            defaults={
                "trigger": trigger,
                "subject": subject,
                "body": body,
                "variables": ["studentName", "schoolName", "feeAmount", "dueDate", "paymentLink", "resultLink"],
                "status": "active",
                "created_by": created_by,
            },
        )
