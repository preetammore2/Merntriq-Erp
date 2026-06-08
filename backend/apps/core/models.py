import base64
import hashlib
import hmac
import secrets
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.db.models import Sum
from django.utils import timezone


class AuditModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SchoolStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    SUSPENDED = "suspended", "Suspended"


class SaaSPlanCode(models.TextChoices):
    BASIC = "basic", "Basic"
    STANDARD = "standard", "Standard"
    PREMIUM = "premium", "Premium"
    ENTERPRISE = "enterprise", "Enterprise"


class SubscriptionStatus(models.TextChoices):
    TRIAL = "trial", "Trial"
    ACTIVE = "active", "Active"
    GRACE = "grace", "Grace"
    EXPIRED = "expired", "Expired"
    CANCELLED = "cancelled", "Cancelled"


class BillingCycle(models.TextChoices):
    MONTHLY = "monthly", "Monthly"
    ANNUAL = "annual", "Annual"
    CUSTOM = "custom", "Custom"


class InvoiceStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ISSUED = "issued", "Issued"
    PAID = "paid", "Paid"
    OVERDUE = "overdue", "Overdue"
    CANCELLED = "cancelled", "Cancelled"


class EnterprisePaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"
    REFUNDED = "refunded", "Refunded"


class JobStatus(models.TextChoices):
    QUEUED = "queued", "Queued"
    RUNNING = "running", "Running"
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"


class BackupType(models.TextChoices):
    FULL_DATABASE = "full_database", "Full database"
    SCHOOL_DATA = "school_data", "School data"
    FILES = "files", "Files"
    PAYMENT_LOGS = "payment_logs", "Payment logs"
    AUDIT_LOGS = "audit_logs", "Audit logs"


class HealthStatus(models.TextChoices):
    OK = "ok", "OK"
    WARNING = "warning", "Warning"
    CRITICAL = "critical", "Critical"


class AdmissionApplicationStatus(models.TextChoices):
    NEW = "new", "New Application"
    UNDER_REVIEW = "under_review", "Under Review"
    INTERVIEW_SCHEDULED = "interview_scheduled", "Interview Scheduled"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    WAITLISTED = "waitlisted", "Waitlisted"
    ADMITTED = "admitted", "Admitted"


class TransportAttendanceStatus(models.TextChoices):
    PRESENT = "present", "Present"
    ABSENT = "absent", "Absent"
    MAINTENANCE = "maintenance", "Maintenance"
    REPLACED = "replaced", "Replaced"


class TransportTripType(models.TextChoices):
    PICKUP = "pickup", "Pickup"
    DROP = "drop", "Drop"


class TransportTripStatus(models.TextChoices):
    SCHEDULED = "scheduled", "Scheduled"
    RUNNING = "running", "Running"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class LibraryRequestStatus(models.TextChoices):
    REQUESTED = "requested", "Requested"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    ISSUED = "issued", "Issued"
    CANCELLED = "cancelled", "Cancelled"


class AssetCategory(models.TextChoices):
    COMPUTER = "computer", "Computer"
    LAB_EQUIPMENT = "lab_equipment", "Lab equipment"
    FURNITURE = "furniture", "Furniture"
    SMART_BOARD = "smart_board", "Smart board"
    PROJECTOR = "projector", "Projector"
    OTHER = "other", "Other"


class AssetStatus(models.TextChoices):
    AVAILABLE = "available", "Available"
    ALLOCATED = "allocated", "Allocated"
    MAINTENANCE = "maintenance", "Maintenance"
    RETIRED = "retired", "Retired"
    LOST = "lost", "Lost"


class WebsiteContentType(models.TextChoices):
    PAGE = "page", "Page"
    NEWS = "news", "News"
    NOTICE = "notice", "Notice"
    GALLERY = "gallery", "Gallery"
    EVENT = "event", "Event"
    ADMISSION = "admission", "Admission"
    CONTACT = "contact", "Contact"


class PushPlatform(models.TextChoices):
    ANDROID = "android", "Android"
    IOS = "ios", "iOS"
    WEB = "web", "Web"


class PushNotificationStatus(models.TextChoices):
    QUEUED = "queued", "Queued"
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"
    READ = "read", "Read"


class MarketplacePluginType(models.TextChoices):
    BIOMETRIC = "biometric", "Biometric"
    SMS = "sms", "SMS"
    WHATSAPP = "whatsapp", "WhatsApp"
    PAYMENT = "payment", "Payment"
    AI = "ai", "AI"
    STORAGE = "storage", "Storage"
    CUSTOM = "custom", "Custom"


class AccountingEntryType(models.TextChoices):
    INCOME = "income", "Income"
    EXPENSE = "expense", "Expense"
    GST_OUTPUT = "gst_output", "GST output"
    GST_INPUT = "gst_input", "GST input"
    LEDGER_ADJUSTMENT = "ledger_adjustment", "Ledger adjustment"


class ReportDefinitionType(models.TextChoices):
    ATTENDANCE = "attendance", "Attendance"
    FEES = "fees", "Fees"
    STUDENT = "student", "Student"
    STAFF = "staff", "Staff"
    ACCOUNTING = "accounting", "Accounting"
    CUSTOM = "custom", "Custom"


class SecurityEventType(models.TextChoices):
    LOGIN = "login", "Login"
    LOGOUT = "logout", "Logout"
    FORCE_LOGOUT = "force_logout", "Force logout"
    TWO_FACTOR = "two_factor", "Two-factor"
    IP_BLOCKED = "ip_blocked", "IP blocked"
    SUSPICIOUS_ACTIVITY = "suspicious_activity", "Suspicious activity"


class ProductionAuditStatus(models.TextChoices):
    QUEUED = "queued", "Queued"
    RUNNING = "running", "Running"
    PASSED = "passed", "Passed"
    FAILED = "failed", "Failed"
    WARNING = "warning", "Warning"


class Campus(AuditModel):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=40, blank=True)
    website = models.URLField(blank=True)
    principal_name = models.CharField(max_length=120, blank=True)
    logo_url = models.TextField(blank=True)
    logo_alt_text = models.CharField(max_length=160, blank=True)
    banner_url = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=SchoolStatus.choices, default=SchoolStatus.ACTIVE)
    subscription_plan = models.CharField(max_length=80, blank=True, default="Standard")
    subscription_status = models.CharField(max_length=40, blank=True, default="active")
    monthly_subscription_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    billing_due_date = models.DateField(null=True, blank=True)
    academic_year_label = models.CharField(max_length=80, blank=True)
    enabled_modules = models.JSONField(default=dict, blank=True)
    payment_gateway_settings = models.JSONField(default=dict, blank=True)
    messaging_settings = models.JSONField(default=dict, blank=True)
    attendance_hardware_settings = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="campuses_created",
    )
    database_alias = models.CharField(
        max_length=64,
        blank=True,
        help_text="Optional Django database alias used when this campus is isolated in its own database.",
    )
    database_name = models.CharField(
        max_length=128,
        blank=True,
        help_text="Optional physical database name for operator reference.",
    )

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["code", "status"]),
            models.Index(fields=["subscription_status"]),
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def tenant_id(self) -> str:
        return self.database_alias or self.code


class SaaSPlan(AuditModel):
    code = models.CharField(max_length=32, choices=SaaSPlanCode.choices, unique=True)
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    monthly_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    annual_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    custom_pricing_enabled = models.BooleanField(default=False)
    student_limit = models.PositiveIntegerField(default=0, help_text="0 means unlimited.")
    teacher_limit = models.PositiveIntegerField(default=0, help_text="0 means unlimited.")
    storage_limit_mb = models.PositiveIntegerField(default=0, help_text="0 means unlimited.")
    ai_monthly_limit = models.PositiveIntegerField(default=0, help_text="0 means unlimited.")
    whatsapp_monthly_limit = models.PositiveIntegerField(default=0, help_text="0 means unlimited.")
    sms_monthly_limit = models.PositiveIntegerField(default=0, help_text="0 means unlimited.")
    modules = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="saas_plans_created",
    )

    class Meta:
        ordering = ["monthly_price", "name"]
        indexes = [
            models.Index(fields=["code", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"

    def clean(self) -> None:
        if self.monthly_price < Decimal("0") or self.annual_price < Decimal("0"):
            raise ValidationError("Plan prices cannot be negative.")

    def module_enabled(self, module_key: str) -> bool:
        return bool((self.modules or {}).get(module_key))

    def limit_for(self, metric: str) -> int:
        return int(getattr(self, f"{metric}_limit", 0) or 0)


class SchoolSubscription(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey(SaaSPlan, on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField(max_length=20, choices=SubscriptionStatus.choices, default=SubscriptionStatus.ACTIVE)
    billing_cycle = models.CharField(max_length=20, choices=BillingCycle.choices, default=BillingCycle.MONTHLY)
    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField()
    grace_period_days = models.PositiveIntegerField(default=7)
    next_billing_date = models.DateField(null=True, blank=True)
    custom_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=8, default="INR")
    gst_number = models.CharField(max_length=40, blank=True)
    auto_disable_on_expiry = models.BooleanField(default=True)
    last_alert_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="school_subscriptions_created",
    )

    class Meta:
        ordering = ["-end_date", "campus__name"]
        indexes = [
            models.Index(fields=["campus", "status"]),
            models.Index(fields=["plan", "status"]),
            models.Index(fields=["end_date", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.campus.code} {self.plan.code} {self.status}"

    @property
    def effective_price(self) -> Decimal:
        if self.custom_price is not None:
            return self.custom_price
        if self.billing_cycle == BillingCycle.ANNUAL:
            return self.plan.annual_price
        return self.plan.monthly_price

    @property
    def grace_ends_on(self):
        return self.end_date + timedelta(days=self.grace_period_days)

    @property
    def is_access_allowed(self) -> bool:
        today = timezone.localdate()
        return self.status in {SubscriptionStatus.TRIAL, SubscriptionStatus.ACTIVE} or (
            self.status == SubscriptionStatus.GRACE and today <= self.grace_ends_on
        )

    def clean(self) -> None:
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "Subscription end date must be on or after start date."})
        if self.custom_price is not None and self.custom_price < Decimal("0"):
            raise ValidationError({"custom_price": "Custom price cannot be negative."})

    def sync_campus_fields(self) -> None:
        self.campus.subscription_plan = self.plan.name
        self.campus.subscription_status = self.status
        self.campus.monthly_subscription_amount = self.plan.monthly_price if self.custom_price is None else self.custom_price
        self.campus.billing_due_date = self.next_billing_date or self.end_date
        self.campus.enabled_modules = {**(self.campus.enabled_modules or {}), **(self.plan.modules or {})}
        if self.status == SubscriptionStatus.EXPIRED and self.auto_disable_on_expiry:
            self.campus.status = SchoolStatus.SUSPENDED
        self.campus.save(update_fields=[
            "subscription_plan",
            "subscription_status",
            "monthly_subscription_amount",
            "billing_due_date",
            "enabled_modules",
            "status",
            "updated_at",
        ])


class SubscriptionInvoice(AuditModel):
    subscription = models.ForeignKey(SchoolSubscription, on_delete=models.CASCADE, related_name="invoices")
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="subscription_invoices")
    invoice_number = models.CharField(max_length=80, unique=True)
    billing_period_start = models.DateField()
    billing_period_end = models.DateField()
    base_amount = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("18.00"))
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=8, default="INR")
    status = models.CharField(max_length=20, choices=InvoiceStatus.choices, default=InvoiceStatus.ISSUED)
    due_date = models.DateField()
    paid_at = models.DateTimeField(null=True, blank=True)
    pdf_url = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subscription_invoices_created",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["campus", "status", "due_date"]),
            models.Index(fields=["subscription", "status"]),
            models.Index(fields=["invoice_number"]),
        ]

    def __str__(self) -> str:
        return f"{self.invoice_number} {self.status}"

    def clean(self) -> None:
        if self.subscription_id and self.campus_id and self.subscription.campus_id != self.campus_id:
            raise ValidationError({"campus": "Invoice campus must match subscription campus."})
        if self.billing_period_end < self.billing_period_start:
            raise ValidationError({"billing_period_end": "Billing period end must be on or after start."})
        if min(self.base_amount, self.discount_amount, self.gst_rate, self.gst_amount, self.total_amount) < Decimal("0"):
            raise ValidationError("Invoice amounts cannot be negative.")

    def calculate_totals(self) -> None:
        taxable = max(self.base_amount - self.discount_amount, Decimal("0.00"))
        self.gst_amount = (taxable * self.gst_rate / Decimal("100.00")).quantize(Decimal("0.01"))
        self.total_amount = taxable + self.gst_amount

    def save(self, *args, **kwargs):
        self.calculate_totals()
        self.full_clean()
        return super().save(*args, **kwargs)


class SubscriptionPayment(AuditModel):
    invoice = models.ForeignKey(SubscriptionInvoice, on_delete=models.CASCADE, related_name="payments")
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="subscription_payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_mode = models.CharField(max_length=32, default="online")
    provider = models.CharField(max_length=80, blank=True)
    transaction_id = models.CharField(max_length=120, blank=True)
    payment_status = models.CharField(max_length=20, choices=EnterprisePaymentStatus.choices, default=EnterprisePaymentStatus.SUCCESS)
    paid_at = models.DateTimeField(default=timezone.now)
    raw_payload = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subscription_payments_created",
    )

    class Meta:
        ordering = ["-paid_at", "-created_at"]
        indexes = [
            models.Index(fields=["campus", "payment_status", "paid_at"]),
            models.Index(fields=["invoice", "payment_status"]),
            models.Index(fields=["transaction_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.invoice.invoice_number} {self.amount}"

    def clean(self) -> None:
        if self.invoice_id and self.campus_id and self.invoice.campus_id != self.campus_id:
            raise ValidationError({"campus": "Payment campus must match invoice campus."})
        if self.amount <= Decimal("0"):
            raise ValidationError({"amount": "Payment amount must be greater than zero."})


class WhiteLabelConfig(AuditModel):
    campus = models.OneToOneField(Campus, on_delete=models.CASCADE, related_name="white_label_config")
    is_enabled = models.BooleanField(default=False)
    custom_logo_url = models.TextField(blank=True)
    custom_domain = models.CharField(max_length=180, blank=True)
    primary_color = models.CharField(max_length=20, blank=True)
    secondary_color = models.CharField(max_length=20, blank=True)
    accent_color = models.CharField(max_length=20, blank=True)
    login_heading = models.CharField(max_length=160, blank=True)
    login_subheading = models.CharField(max_length=240, blank=True)
    login_background_url = models.TextField(blank=True)
    email_template_header = models.TextField(blank=True)
    email_template_footer = models.TextField(blank=True)
    report_logo_url = models.TextField(blank=True)
    report_footer = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="white_label_configs_created",
    )

    class Meta:
        ordering = ["campus__name"]
        indexes = [
            models.Index(fields=["custom_domain"]),
            models.Index(fields=["is_enabled"]),
        ]

    def __str__(self) -> str:
        return f"{self.campus.code} white label"

    def clean(self) -> None:
        allowed = {"premium", "enterprise"}
        latest = self.campus.subscriptions.select_related("plan").order_by("-end_date", "-created_at").first()
        plan_code = latest.plan.code if latest else (self.campus.subscription_plan or "").strip().lower()
        if self.is_enabled and plan_code not in allowed:
            raise ValidationError({"is_enabled": "White label branding is available only for Premium and Enterprise plans."})


class UserActivityLog(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, null=True, blank=True, related_name="user_activity_logs")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="activity_logs")
    activity_type = models.CharField(max_length=80)
    summary = models.CharField(max_length=255)
    request_path = models.CharField(max_length=255, blank=True)
    method = models.CharField(max_length=12, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["campus", "activity_type", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.activity_type} {self.user_id or ''}".strip()


class DocumentAccessLog(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="document_access_logs")
    document = models.ForeignKey("core.Document", on_delete=models.SET_NULL, null=True, blank=True, related_name="access_logs")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="document_access_logs")
    student = models.ForeignKey("core.Student", on_delete=models.SET_NULL, null=True, blank=True, related_name="document_access_logs")
    access_type = models.CharField(max_length=40, default="download")
    file_name = models.CharField(max_length=180, blank=True)
    granted = models.BooleanField(default=True)
    reason = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["campus", "access_type", "created_at"]),
            models.Index(fields=["document", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.access_type} {self.file_name}"


class EnterpriseUsageMetric(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="enterprise_usage_metrics")
    metric_type = models.CharField(max_length=80)
    period_start = models.DateField()
    period_end = models.DateField()
    quantity = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-period_start", "campus__name", "metric_type"]
        unique_together = ("campus", "metric_type", "period_start", "period_end")
        indexes = [
            models.Index(fields=["campus", "metric_type", "period_start"]),
        ]

    def __str__(self) -> str:
        return f"{self.campus.code} {self.metric_type} {self.quantity}"


class BackupPolicy(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, null=True, blank=True, related_name="backup_policies")
    backup_type = models.CharField(max_length=40, choices=BackupType.choices)
    frequency = models.CharField(max_length=40, default="daily")
    retention_days = models.PositiveIntegerField(default=30)
    destination = models.CharField(max_length=255, blank=True)
    encryption_required = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="backup_policies_created",
    )

    class Meta:
        ordering = ["campus__name", "backup_type"]
        unique_together = ("campus", "backup_type")
        indexes = [
            models.Index(fields=["campus", "backup_type", "is_active"]),
        ]

    def __str__(self) -> str:
        scope = self.campus.code if self.campus_id else "platform"
        return f"{scope} {self.backup_type}"


class BackupJob(AuditModel):
    policy = models.ForeignKey(BackupPolicy, on_delete=models.SET_NULL, null=True, blank=True, related_name="jobs")
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, null=True, blank=True, related_name="backup_jobs")
    backup_type = models.CharField(max_length=40, choices=BackupType.choices)
    status = models.CharField(max_length=20, choices=JobStatus.choices, default=JobStatus.QUEUED)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    storage_location = models.CharField(max_length=255, blank=True)
    size_bytes = models.PositiveBigIntegerField(default=0)
    checksum = models.CharField(max_length=128, blank=True)
    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="backup_jobs_created",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["campus", "backup_type", "status"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self) -> str:
        scope = self.campus.code if self.campus_id else "platform"
        return f"{scope} {self.backup_type} {self.status}"


class QueueJob(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, null=True, blank=True, related_name="queue_jobs")
    job_type = models.CharField(max_length=80)
    status = models.CharField(max_length=20, choices=JobStatus.choices, default=JobStatus.QUEUED)
    priority = models.PositiveSmallIntegerField(default=5)
    payload = models.JSONField(default=dict, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=3)
    scheduled_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="queue_jobs_created",
    )

    class Meta:
        ordering = ["priority", "scheduled_at", "created_at"]
        indexes = [
            models.Index(fields=["status", "scheduled_at", "priority"]),
            models.Index(fields=["campus", "job_type", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.job_type} {self.status}"


class SystemHealthSnapshot(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, null=True, blank=True, related_name="health_snapshots")
    component = models.CharField(max_length=80)
    status = models.CharField(max_length=20, choices=HealthStatus.choices, default=HealthStatus.OK)
    latency_ms = models.PositiveIntegerField(default=0)
    metric_value = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    message = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    checked_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-checked_at"]
        indexes = [
            models.Index(fields=["component", "status", "checked_at"]),
            models.Index(fields=["campus", "component", "checked_at"]),
        ]

    def __str__(self) -> str:
        scope = self.campus.code if self.campus_id else "platform"
        return f"{scope} {self.component} {self.status}"


class SecureAPIToken(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, null=True, blank=True, related_name="secure_api_tokens")
    name = models.CharField(max_length=120)
    prefix = models.CharField(max_length=16)
    token_hash = models.CharField(max_length=128)
    scopes = models.JSONField(default=list, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="secure_api_tokens_created",
    )

    class Meta:
        ordering = ["campus__name", "name"]
        indexes = [
            models.Index(fields=["campus", "is_active"]),
            models.Index(fields=["prefix"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.prefix})"

    @staticmethod
    def hash_token(raw_token: str) -> str:
        return hmac.new(settings.SECRET_KEY.encode("utf-8"), raw_token.encode("utf-8"), hashlib.sha256).hexdigest()

    def verify(self, raw_token: str) -> bool:
        return hmac.compare_digest(self.token_hash, self.hash_token(raw_token))


class AcademicSession(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="sessions")
    name = models.CharField(max_length=120)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self) -> str:
        return f"{self.campus.code} {self.name}"


class ClassSection(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="sections")
    session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name="sections",
    )
    grade_name = models.CharField(max_length=50)
    section_name = models.CharField(max_length=20)
    class_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_sections",
    )

    class Meta:
        ordering = ["grade_name", "section_name"]
        unique_together = ("session", "grade_name", "section_name")

    def __str__(self) -> str:
        return f"{self.grade_name}-{self.section_name}"

    def clean(self) -> None:
        if self.session_id and self.campus_id and self.session.campus_id != self.campus_id:
            raise ValidationError({"session": "Session must belong to the selected campus."})


class TeacherSubjectAllocation(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="teacher_subject_allocations")
    section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name="subject_allocations")
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subject_allocations",
    )
    subject = models.CharField(max_length=80)
    weekly_periods = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(60)])
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["campus__name", "section__grade_name", "section__section_name", "subject"]
        unique_together = ("section", "teacher", "subject")
        indexes = [
            models.Index(fields=["teacher", "is_active"]),
            models.Index(fields=["campus", "subject"]),
        ]

    def __str__(self) -> str:
        return f"{self.teacher} - {self.section} - {self.subject}"

    def clean(self) -> None:
        self.subject = (self.subject or "").strip()
        if self.section_id and self.campus_id and self.section.campus_id != self.campus_id:
            raise ValidationError({"section": "Section must belong to the selected campus."})
        if self.teacher_id and getattr(self.teacher, "role", None) != "teacher":
            raise ValidationError({"teacher": "Subject allocation must be assigned to a teacher user."})
        if not self.subject:
            raise ValidationError({"subject": "Subject is required."})


class Subject(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="subjects")
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=40, blank=True)
    grade_name = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["grade_name", "name"]
        unique_together = ("campus", "name", "grade_name")
        indexes = [
            models.Index(fields=["campus", "is_active"]),
            models.Index(fields=["campus", "code"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.campus.code})"

    def clean(self) -> None:
        self.name = (self.name or "").strip()
        self.code = (self.code or "").strip().upper()
        if not self.name:
            raise ValidationError({"name": "Subject name is required."})


class StudentStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    ALUMNI = "alumni", "Alumni"


class AttendanceStatus(models.TextChoices):
    PRESENT = "present", "Present"
    ABSENT = "absent", "Absent"
    LATE = "late", "Late"
    HALF_DAY = "half_day", "Half Day"
    ON_DUTY = "on_duty", "On Duty"


class FeeStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PARTIAL = "partial", "Partial"
    PAID = "paid", "Paid"
    OVERDUE = "overdue", "Overdue"


class PaymentMethod(models.TextChoices):
    CASH = "cash", "Cash"
    CARD = "card", "Card"
    BANK = "bank", "Bank"
    ONLINE = "online", "Online"
    UPI = "upi", "UPI"
    NET_BANKING = "net_banking", "Net banking"
    WALLET = "wallet", "Wallet"


class GatewayProvider(models.TextChoices):
    RAZORPAY = "razorpay", "Razorpay"
    UPI = "upi", "UPI"
    CARD = "card", "Card"
    NET_BANKING = "net_banking", "Net banking"
    WALLET = "wallet", "Wallet"


class FinanceEventType(models.TextChoices):
    FEE_PAID = "feePaid", "Fee paid"
    PAYMENT_FAILED = "paymentFailed", "Payment failed"
    OFFLINE_PAYMENT_ADDED = "offlinePaymentAdded", "Offline payment added"
    RECEIPT_GENERATED = "receiptGenerated", "Receipt generated"
    SALARY_PAID = "salaryPaid", "Salary paid"
    FEE_REMINDER_SENT = "feeReminderSent", "Fee reminder sent"


class CampusMemberRole(models.TextChoices):
    IT_ADMIN = "it_admin", "School Admin"
    FINANCE_ADMIN = "finance_admin", "Account"
    TEACHER = "teacher", "Teacher"
    SUPPORT = "support", "Student Portal"


class AttendanceCaptureMethod(models.TextChoices):
    MANUAL = "manual", "Manual"
    FACE_RECOGNITION = "face_recognition", "Face Recognition"
    FINGERPRINT = "fingerprint", "Fingerprint"
    CARD_SCAN = "card_scan", "Card Scan"


class DeviceStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    MAINTENANCE = "maintenance", "Maintenance"


class RS485Function(models.TextChoices):
    SOFTWARE = "software", "Software"
    HARDWARE = "hardware", "Hardware"
    DISABLED = "disabled", "Disabled"


class StaffAttendanceStatus(models.TextChoices):
    PRESENT = "present", "Present"
    ABSENT = "absent", "Absent"
    LATE = "late", "Late"
    HALF_DAY = "half_day", "Half Day"
    ON_LEAVE = "on_leave", "On Leave"


class StaffEmploymentType(models.TextChoices):
    FULL_TIME = "full_time", "Full time"
    PART_TIME = "part_time", "Part time"
    CONTRACT = "contract", "Contract"


class StaffProfileStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    EXITED = "exited", "Exited"


class Weekday(models.IntegerChoices):
    MONDAY = 1, "Monday"
    TUESDAY = 2, "Tuesday"
    WEDNESDAY = 3, "Wednesday"
    THURSDAY = 4, "Thursday"
    FRIDAY = 5, "Friday"
    SATURDAY = 6, "Saturday"
    SUNDAY = 7, "Sunday"


class LibraryBookStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    LOST = "lost", "Lost"


class LibraryLoanStatus(models.TextChoices):
    ISSUED = "issued", "Issued"
    RETURNED = "returned", "Returned"
    OVERDUE = "overdue", "Overdue"


class ApprovalStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class AnnouncementAudience(models.TextChoices):
    ALL = "all", "All users"
    ADMINS = "admins", "Admins"
    STAFF = "staff", "Teachers and staff"
    LEARNERS = "learners", "Students"


class SupportTicketStatus(models.TextChoices):
    OPEN = "open", "Open"
    IN_PROGRESS = "in_progress", "In Progress"
    RESOLVED = "resolved", "Resolved"


class SupportTicketPriority(models.TextChoices):
    NORMAL = "normal", "Normal"
    HIGH = "high", "High"
    URGENT = "urgent", "Urgent"


class AuditAction(models.TextChoices):
    CREATE = "create", "Create"
    UPDATE = "update", "Update"
    DELETE = "delete", "Delete"
    LOGIN = "login", "Login"
    EXPORT = "export", "Export"


class AcademicWorkStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    CLOSED = "closed", "Closed"


class AssignmentSubmissionStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    CHECKED = "checked", "Checked"


class ResultReviewStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SUBMITTED = "submitted", "Submitted"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class AcademicEventType(models.TextChoices):
    ATTENDANCE_MARKED = "attendanceMarked", "Attendance marked"
    NOTES_UPLOADED = "notesUploaded", "Notes uploaded"
    ASSIGNMENT_UPLOADED = "assignmentUploaded", "Assignment uploaded"
    ASSIGNMENT_PUBLISHED = "assignmentPublished", "Assignment published"
    ASSIGNMENT_SUBMITTED = "assignmentSubmitted", "Assignment submitted"
    MARKS_UPLOADED = "marksUploaded", "Marks uploaded"
    RESULT_PUBLISHED = "resultPublished", "Result published"
    NOTICE_PUBLISHED = "noticePublished", "Notice published"
    PAYMENT_UPDATED = "paymentUpdated", "Payment updated"
    DEVICE_SYNCED = "deviceSynced", "Device synced"
    SCHOOL_STATUS_CHANGED = "schoolStatusChanged", "School status changed"


class ResourceType(models.TextChoices):
    NOTES = "notes", "Notes"
    SYLLABUS = "syllabus", "Syllabus"
    ASSIGNMENT_HELP = "assignment_help", "Assignment Help"
    REFERENCE = "reference", "Reference"


class AdmitCardStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ISSUED = "issued", "Issued"
    BLOCKED = "blocked", "Blocked"


class ExamScheduleStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    ARCHIVED = "archived", "Archived"


class AuditEvent(AuditModel):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_events",
    )
    action = models.CharField(max_length=20, choices=AuditAction.choices)
    entity_type = models.CharField(max_length=80)
    entity_id = models.CharField(max_length=80, blank=True)
    summary = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["actor", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.action} {self.entity_type} {self.entity_id}".strip()


class CampusMembership(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="campus_memberships",
    )
    role = models.CharField(max_length=32, choices=CampusMemberRole.choices)
    is_primary = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)
    can_configure_attendance = models.BooleanField(default=False)

    class Meta:
        ordering = ["campus__name", "user__username", "role"]
        unique_together = ("campus", "user", "role")
        indexes = [
            models.Index(fields=["campus", "role"]),
            models.Index(fields=["user", "is_primary"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} @ {self.campus} ({self.role})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if getattr(self.user, "role", None) != "super_admin":
            should_sync_school = self.is_primary or not getattr(self.user, "school_id", None)
            if should_sync_school:
                type(self.user).objects.filter(pk=self.user_id).update(school_id=self.campus_id)


class AttendanceDevice(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="attendance_devices")
    name = models.CharField(max_length=120)
    device_code = models.CharField(max_length=60, unique=True)
    device_type = models.CharField(max_length=32, choices=AttendanceCaptureMethod.choices)
    location = models.CharField(max_length=160, blank=True)
    provider = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=DeviceStatus.choices, default=DeviceStatus.ACTIVE)
    is_enabled_for_students = models.BooleanField(default=True)
    is_enabled_for_staff = models.BooleanField(default=True)
    server_required = models.BooleanField(default=True)
    use_domain_name = models.BooleanField(default=True)
    domain_name = models.CharField(max_length=180, blank=True, default="device.nialabs.in")
    server_ip = models.CharField(max_length=45, blank=True, default="192.168.000.109")
    server_port = models.PositiveIntegerField(default=7743, validators=[MinValueValidator(1), MaxValueValidator(65535)])
    heartbeat_seconds = models.PositiveIntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(3600)])
    server_approval_required = models.BooleanField(default=False)
    device_numeric_id = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(999999)])
    local_port = models.PositiveIntegerField(default=5005, validators=[MinValueValidator(1), MaxValueValidator(65535)])
    baud_rate = models.PositiveIntegerField(default=38400, validators=[MinValueValidator(1200), MaxValueValidator(921600)])
    rs485_function = models.CharField(max_length=32, choices=RS485Function.choices, default=RS485Function.SOFTWARE)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    configured_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendance_devices_configured",
    )

    class Meta:
        ordering = ["campus__name", "name"]
        indexes = [
            models.Index(fields=["campus", "device_type"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.device_code})"


class Student(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="students")
    section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name="students")
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_profile",
    )
    admission_number = models.CharField(max_length=40, unique=True, blank=True)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80, blank=True)
    date_of_birth = models.DateField()
    photo_url = models.TextField(blank=True)
    father_name = models.CharField(max_length=120, blank=True)
    mother_name = models.CharField(max_length=120, blank=True)
    contact_email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    alternate_phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    blood_group = models.CharField(max_length=8, blank=True)
    medical_notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=StudentStatus.choices, default=StudentStatus.ACTIVE)

    class Meta:
        ordering = ["first_name", "last_name"]
        indexes = [
            models.Index(fields=["campus", "status"]),
            models.Index(fields=["section", "status"]),
            models.Index(fields=["admission_number"]),
        ]

    def __str__(self) -> str:
        return self.full_name

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def clean(self) -> None:
        if self.section_id and self.campus_id and self.section.campus_id != self.campus_id:
            raise ValidationError({"section": "Section must belong to the selected campus."})
        if self.user_id and getattr(self.user, "role", None) != "student":
            raise ValidationError({"user": "Linked login user must have the student role."})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.user_id and getattr(self.user, "role", None) != "super_admin":
            type(self.user).objects.filter(pk=self.user_id).update(school_id=self.campus_id)


class StudentGuardian(AuditModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="guardianships")
    guardian = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_links",
    )
    relationship = models.CharField(max_length=40, default="Guardian")

    class Meta:
        unique_together = ("student", "guardian")

    def __str__(self) -> str:
        return f"{self.guardian.username} -> {self.student.full_name}"


class AttendanceRecord(AuditModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance_records")
    section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name="attendance_records")
    date = models.DateField()
    subject = models.CharField(max_length=80, blank=True, default="")
    status = models.CharField(max_length=20, choices=AttendanceStatus.choices)
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendance_marked",
    )
    capture_method = models.CharField(
        max_length=32,
        choices=AttendanceCaptureMethod.choices,
        default=AttendanceCaptureMethod.MANUAL,
    )
    device = models.ForeignKey(
        AttendanceDevice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_attendance_records",
    )
    source_reference = models.CharField(max_length=120, blank=True)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ["-date", "student__first_name"]
        unique_together = ("student", "date", "subject")
        indexes = [
            models.Index(fields=["section", "date", "subject"]),
            models.Index(fields=["student", "date"]),
            models.Index(fields=["date", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.student.full_name} {self.date} {self.status}"

    def clean(self) -> None:
        self.subject = (self.subject or "").strip()
        if self.student_id and self.section_id and self.student.section_id != self.section_id:
            raise ValidationError({"section": "Attendance section must match the student's assigned section."})
        if self.device_id and self.student_id and self.device.campus_id != self.student.campus_id:
            raise ValidationError({"device": "Attendance device must belong to the student's campus."})


class StaffAttendanceRecord(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="staff_attendance_records")
    staff_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="staff_attendance_records",
    )
    date = models.DateField()
    clock_in = models.TimeField(null=True, blank=True)
    clock_out = models.TimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=StaffAttendanceStatus.choices,
        default=StaffAttendanceStatus.PRESENT,
    )
    capture_method = models.CharField(
        max_length=32,
        choices=AttendanceCaptureMethod.choices,
        default=AttendanceCaptureMethod.MANUAL,
    )
    device = models.ForeignKey(
        AttendanceDevice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="staff_attendance_records",
    )
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="staff_attendance_marked",
    )
    source_reference = models.CharField(max_length=120, blank=True)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date", "staff_user__username"]
        unique_together = ("staff_user", "date")
        indexes = [
            models.Index(fields=["campus", "date"]),
            models.Index(fields=["staff_user", "date"]),
        ]

    def __str__(self) -> str:
        return f"{self.staff_user} {self.date} {self.status}"

    def clean(self) -> None:
        if self.device_id and self.campus_id and self.device.campus_id != self.campus_id:
            raise ValidationError({"device": "Attendance device must belong to the selected campus."})
        if self.staff_user_id and getattr(self.staff_user, "role", None) == "student":
            raise ValidationError({"staff_user": "Staff attendance cannot be recorded for student users."})


class StaffProfile(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="staff_profiles")
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="staff_profile",
    )
    employee_code = models.CharField(max_length=40, unique=True, blank=True)
    designation = models.CharField(max_length=120)
    department = models.CharField(max_length=120, blank=True)
    photo_url = models.TextField(blank=True)
    employment_type = models.CharField(
        max_length=20,
        choices=StaffEmploymentType.choices,
        default=StaffEmploymentType.FULL_TIME,
    )
    joining_date = models.DateField()
    qualification = models.CharField(max_length=180, blank=True)
    emergency_contact = models.CharField(max_length=40, blank=True)
    status = models.CharField(
        max_length=20,
        choices=StaffProfileStatus.choices,
        default=StaffProfileStatus.ACTIVE,
    )

    class Meta:
        ordering = ["campus__name", "employee_code"]
        indexes = [
            models.Index(fields=["campus", "status"]),
            models.Index(fields=["department"]),
        ]

    def __str__(self) -> str:
        return f"{self.employee_code} - {self.user}"

    def clean(self) -> None:
        if self.user_id and getattr(self.user, "role", None) == "student":
            raise ValidationError({"user": "Staff profile users must be administrators or teachers."})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.user_id and getattr(self.user, "role", None) != "super_admin":
            type(self.user).objects.filter(pk=self.user_id).update(school_id=self.campus_id)


class TimetableSlot(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="timetable_slots")
    section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name="timetable_slots")
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="timetable_slots",
    )
    subject = models.CharField(max_length=80)
    day_of_week = models.PositiveSmallIntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=80, blank=True)
    effective_from = models.DateField(default=timezone.localdate)
    effective_to = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["day_of_week", "start_time", "section__grade_name", "section__section_name"]
        unique_together = ("section", "day_of_week", "start_time")
        indexes = [
            models.Index(fields=["campus", "day_of_week"]),
            models.Index(fields=["teacher", "day_of_week"]),
        ]

    def __str__(self) -> str:
        return f"{self.section} {self.get_day_of_week_display()} {self.start_time} {self.subject}"

    def clean(self) -> None:
        self.subject = (self.subject or "").strip()
        if self.section_id and self.campus_id and self.section.campus_id != self.campus_id:
            raise ValidationError({"section": "Section must belong to the selected campus."})
        if self.teacher_id and getattr(self.teacher, "role", None) != "teacher":
            raise ValidationError({"teacher": "Timetable teacher must be a teacher user."})
        if self.end_time and self.start_time and self.end_time <= self.start_time:
            raise ValidationError({"end_time": "End time must be after start time."})
        if self.effective_to and self.effective_from and self.effective_to < self.effective_from:
            raise ValidationError({"effective_to": "End date must be on or after the effective from date."})
        if not self.subject:
            raise ValidationError({"subject": "Subject is required."})


class ExamType(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="exam_types")
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("campus", "name")
        indexes = [
            models.Index(fields=["campus", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.campus.code})"

    def clean(self) -> None:
        self.name = (self.name or "").strip()
        if not self.name:
            raise ValidationError({"name": "Exam type name is required."})


class ExamSubjectSetup(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="exam_subject_setups")
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE, related_name="subject_setups")
    section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name="exam_subject_setups")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="exam_subject_setups")
    max_marks = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    pass_marks = models.DecimalField(max_digits=6, decimal_places=2, default=33)
    weightage = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["exam_type__name", "section__grade_name", "section__section_name", "subject__name"]
        unique_together = ("exam_type", "section", "subject")
        indexes = [
            models.Index(fields=["campus", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.exam_type.name} - {self.section} - {self.subject.name}"

    def clean(self) -> None:
        if self.exam_type_id and self.campus_id and self.exam_type.campus_id != self.campus_id:
            raise ValidationError({"exam_type": "Exam type must belong to the selected campus."})
        if self.section_id and self.campus_id and self.section.campus_id != self.campus_id:
            raise ValidationError({"section": "Section must belong to the selected campus."})
        if self.subject_id and self.campus_id and self.subject.campus_id != self.campus_id:
            raise ValidationError({"subject": "Subject must belong to the selected campus."})
        if self.max_marks <= Decimal("0"):
            raise ValidationError({"max_marks": "Max marks must be greater than zero."})
        if self.pass_marks < Decimal("0") or self.pass_marks > self.max_marks:
            raise ValidationError({"pass_marks": "Pass marks must be between zero and max marks."})
        if self.weightage <= Decimal("0") or self.weightage > Decimal("100"):
            raise ValidationError({"weightage": "Weightage must be between 0 and 100."})


class ExamSchedule(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="exam_schedules")
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE, related_name="schedules")
    section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name="exam_schedules")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="exam_schedules")
    title = models.CharField(max_length=160)
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_marks = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    venue = models.CharField(max_length=160, blank=True)
    instructions = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=ExamScheduleStatus.choices,
        default=ExamScheduleStatus.DRAFT,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="exam_schedules_created",
    )

    class Meta:
        ordering = ["exam_date", "start_time", "section__grade_name", "subject__name"]
        unique_together = ("section", "subject", "exam_date", "start_time")
        indexes = [
            models.Index(fields=["campus", "exam_date", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} - {self.section} - {self.subject.name}"

    def clean(self) -> None:
        self.title = (self.title or "").strip()
        if self.exam_type_id and self.campus_id and self.exam_type.campus_id != self.campus_id:
            raise ValidationError({"exam_type": "Exam type must belong to the selected campus."})
        if self.section_id and self.campus_id and self.section.campus_id != self.campus_id:
            raise ValidationError({"section": "Section must belong to the selected campus."})
        if self.subject_id and self.campus_id and self.subject.campus_id != self.campus_id:
            raise ValidationError({"subject": "Subject must belong to the selected campus."})
        if self.end_time and self.start_time and self.end_time <= self.start_time:
            raise ValidationError({"end_time": "End time must be after start time."})
        if self.max_marks <= Decimal("0"):
            raise ValidationError({"max_marks": "Max marks must be greater than zero."})
        if not self.title:
            raise ValidationError({"title": "Exam schedule title is required."})


class LibraryBook(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="library_books")
    accession_number = models.CharField(max_length=60, unique=True)
    title = models.CharField(max_length=180)
    author = models.CharField(max_length=160, blank=True)
    isbn = models.CharField(max_length=40, blank=True)
    category = models.CharField(max_length=80, blank=True)
    total_copies = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    available_copies = models.PositiveIntegerField(default=1)
    shelf_location = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=20, choices=LibraryBookStatus.choices, default=LibraryBookStatus.ACTIVE)

    class Meta:
        ordering = ["title", "accession_number"]
        indexes = [
            models.Index(fields=["campus", "status"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.accession_number})"

    def clean(self) -> None:
        if self.available_copies > self.total_copies:
            raise ValidationError({"available_copies": "Available copies cannot exceed total copies."})


class LibraryLoan(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="library_loans")
    book = models.ForeignKey(LibraryBook, on_delete=models.CASCADE, related_name="loans")
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="library_loans",
    )
    staff_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="library_loans",
    )
    issued_on = models.DateField(default=timezone.localdate)
    due_on = models.DateField()
    returned_on = models.DateField(null=True, blank=True)
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=20, choices=LibraryLoanStatus.choices, default=LibraryLoanStatus.ISSUED)

    class Meta:
        ordering = ["status", "due_on", "-issued_on"]
        indexes = [
            models.Index(fields=["campus", "status"]),
            models.Index(fields=["student", "status"]),
            models.Index(fields=["staff_user", "status"]),
        ]

    def __str__(self) -> str:
        borrower = self.student.full_name if self.student_id else self.staff_user
        return f"{self.book.title} -> {borrower}"

    def clean(self) -> None:
        if bool(self.student_id) == bool(self.staff_user_id):
            raise ValidationError({"student": "Select exactly one borrower: student or staff user."})
        if self.book_id and self.campus_id and self.book.campus_id != self.campus_id:
            raise ValidationError({"book": "Book must belong to the selected campus."})
        if self.student_id and self.campus_id and self.student.campus_id != self.campus_id:
            raise ValidationError({"student": "Student must belong to the selected campus."})
        if self.staff_user_id and getattr(self.staff_user, "role", None) == "student":
            raise ValidationError({"staff_user": "Use the student borrower field for student users."})
        if self.due_on and self.issued_on and self.due_on < self.issued_on:
            raise ValidationError({"due_on": "Due date must be on or after issue date."})
        if self.returned_on and self.issued_on and self.returned_on < self.issued_on:
            raise ValidationError({"returned_on": "Return date must be on or after issue date."})
        if self.fine_amount < Decimal("0"):
            raise ValidationError({"fine_amount": "Fine amount cannot be negative."})


class TransportRoute(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="transport_routes")
    name = models.CharField(max_length=120)
    route_code = models.CharField(max_length=40, unique=True)
    start_point = models.CharField(max_length=120)
    end_point = models.CharField(max_length=120)
    stops = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["campus__name", "route_code"]
        indexes = [
            models.Index(fields=["campus", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.route_code} - {self.name}"


class TransportVehicle(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="transport_vehicles")
    route = models.ForeignKey(
        TransportRoute,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vehicles",
    )
    vehicle_number = models.CharField(max_length=40, unique=True)
    driver_name = models.CharField(max_length=120)
    driver_phone = models.CharField(max_length=40, blank=True)
    capacity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    gps_device_id = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["campus__name", "vehicle_number"]
        indexes = [
            models.Index(fields=["campus", "is_active"]),
        ]

    def __str__(self) -> str:
        return self.vehicle_number

    def clean(self) -> None:
        if self.route_id and self.campus_id and self.route.campus_id != self.campus_id:
            raise ValidationError({"route": "Route must belong to the selected campus."})


class StudentTransportAssignment(AuditModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="transport_assignments")
    route = models.ForeignKey(TransportRoute, on_delete=models.CASCADE, related_name="student_assignments")
    vehicle = models.ForeignKey(
        TransportVehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_assignments",
    )
    pickup_stop = models.CharField(max_length=120)
    drop_stop = models.CharField(max_length=120)
    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField(null=True, blank=True)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["student__first_name", "start_date"]
        unique_together = ("student", "route", "start_date")
        indexes = [
            models.Index(fields=["route", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.student.full_name} - {self.route.route_code}"

    def clean(self) -> None:
        if self.student_id and self.route_id and self.student.campus_id != self.route.campus_id:
            raise ValidationError({"route": "Route must belong to the student's campus."})
        if self.vehicle_id and self.route_id and self.vehicle.campus_id != self.route.campus_id:
            raise ValidationError({"vehicle": "Vehicle must belong to the route campus."})
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date must be on or after start date."})
        if self.fee_amount < Decimal("0"):
            raise ValidationError({"fee_amount": "Transport fee cannot be negative."})


class HostelRoom(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="hostel_rooms")
    hostel_name = models.CharField(max_length=120)
    room_number = models.CharField(max_length=40)
    floor = models.CharField(max_length=40, blank=True)
    capacity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["campus__name", "hostel_name", "room_number"]
        unique_together = ("campus", "hostel_name", "room_number")
        indexes = [
            models.Index(fields=["campus", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.hostel_name} {self.room_number}"


class HostelAllocation(AuditModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="hostel_allocations")
    room = models.ForeignKey(HostelRoom, on_delete=models.CASCADE, related_name="allocations")
    bed_number = models.CharField(max_length=40)
    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField(null=True, blank=True)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["student__first_name", "start_date"]
        unique_together = ("room", "bed_number", "start_date")
        indexes = [
            models.Index(fields=["room", "is_active"]),
            models.Index(fields=["student", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.student.full_name} - {self.room} Bed {self.bed_number}"

    def clean(self) -> None:
        if self.student_id and self.room_id and self.student.campus_id != self.room.campus_id:
            raise ValidationError({"room": "Hostel room must belong to the student's campus."})
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date must be on or after start date."})
        if self.fee_amount < Decimal("0"):
            raise ValidationError({"fee_amount": "Hostel fee cannot be negative."})


class AssignedWork(AuditModel):
    section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name="assigned_work")
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_work_created",
    )
    title = models.CharField(max_length=160)
    subject = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=AcademicWorkStatus.choices,
        default=AcademicWorkStatus.PUBLISHED,
    )
    file_url = models.TextField(blank=True)
    file_name = models.CharField(max_length=180, blank=True)
    file_content_type = models.CharField(max_length=100, blank=True)
    published_on = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["due_date", "subject", "title"]

    def __str__(self) -> str:
        return f"{self.subject} - {self.title}"

    def clean(self) -> None:
        self.title = (self.title or "").strip()
        self.subject = (self.subject or "").strip()
        self.file_name = (self.file_name or "").strip()
        self.file_content_type = (self.file_content_type or "").strip()
        if not self.title:
            raise ValidationError({"title": "Assignment title is required."})
        if not self.subject:
            raise ValidationError({"subject": "Assignment subject is required."})


class LearningResource(AuditModel):
    section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name="learning_resources")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="learning_resources_uploaded",
    )
    title = models.CharField(max_length=160)
    subject = models.CharField(max_length=80)
    resource_type = models.CharField(max_length=32, choices=ResourceType.choices, default=ResourceType.NOTES)
    description = models.TextField(blank=True)
    file_url = models.TextField(blank=True)
    file_name = models.CharField(max_length=180, blank=True)
    file_content_type = models.CharField(max_length=100, blank=True)
    published_on = models.DateField(default=timezone.localdate)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-published_on", "subject", "title"]

    def __str__(self) -> str:
        return f"{self.subject} - {self.title}"

    def clean(self) -> None:
        self.title = (self.title or "").strip()
        self.subject = (self.subject or "").strip()
        self.file_name = (self.file_name or "").strip()
        self.file_content_type = (self.file_content_type or "").strip()
        if not self.title:
            raise ValidationError({"title": "Resource title is required."})
        if not self.subject:
            raise ValidationError({"subject": "Resource subject is required."})


class ResultRecord(AuditModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="result_records")
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="results_recorded",
    )
    exam_name = models.CharField(max_length=120)
    subject = models.CharField(max_length=80)
    score = models.DecimalField(max_digits=6, decimal_places=2)
    max_score = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    grade = models.CharField(max_length=12, blank=True)
    remarks = models.TextField(blank=True)
    published_on = models.DateField(default=timezone.localdate)
    is_published = models.BooleanField(default=True)
    review_status = models.CharField(
        max_length=20,
        choices=ResultReviewStatus.choices,
        default=ResultReviewStatus.DRAFT,
    )
    marks_file_url = models.TextField(blank=True)
    marks_file_name = models.CharField(max_length=180, blank=True)
    marks_file_content_type = models.CharField(max_length=100, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="results_reviewed",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True)

    class Meta:
        ordering = ["-published_on", "exam_name", "subject"]
        unique_together = ("student", "exam_name", "subject")

    def __str__(self) -> str:
        return f"{self.student.full_name} - {self.exam_name} - {self.subject}"

    def clean(self) -> None:
        self.exam_name = (self.exam_name or "").strip()
        self.subject = (self.subject or "").strip()
        self.marks_file_name = (self.marks_file_name or "").strip()
        self.marks_file_content_type = (self.marks_file_content_type or "").strip()
        if self.score < Decimal("0"):
            raise ValidationError({"score": "Score cannot be negative."})
        if self.max_score <= Decimal("0"):
            raise ValidationError({"max_score": "Max score must be greater than zero."})
        if self.score > self.max_score:
            raise ValidationError({"score": "Score cannot exceed max score."})
        if not self.exam_name:
            raise ValidationError({"exam_name": "Exam name is required."})
        if not self.subject:
            raise ValidationError({"subject": "Result subject is required."})


class AssignmentSubmission(AuditModel):
    assignment = models.ForeignKey(AssignedWork, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="assignment_submissions")
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assignment_submissions",
    )
    file_url = models.TextField(blank=True)
    file_name = models.CharField(max_length=180, blank=True)
    file_content_type = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=AssignmentSubmissionStatus.choices,
        default=AssignmentSubmissionStatus.PENDING,
    )
    remarks = models.TextField(blank=True)
    checked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assignment_submissions_checked",
    )
    checked_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-submitted_at"]
        unique_together = ("assignment", "student")
        indexes = [
            models.Index(fields=["assignment", "status"]),
            models.Index(fields=["student", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.student.full_name} - {self.assignment.title}"

    def clean(self) -> None:
        self.file_name = (self.file_name or "").strip()
        self.file_content_type = (self.file_content_type or "").strip()
        if self.assignment_id and self.student_id and self.assignment.section_id != self.student.section_id:
            raise ValidationError({"student": "Submission student must belong to the assignment section."})


class AdmitCard(AuditModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="admit_cards")
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="admit_cards_issued",
    )
    exam_name = models.CharField(max_length=120)
    roll_number = models.CharField(max_length=40)
    exam_date = models.DateField()
    reporting_time = models.TimeField()
    venue = models.CharField(max_length=160)
    instructions = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=AdmitCardStatus.choices, default=AdmitCardStatus.ISSUED)
    issued_on = models.DateField(default=timezone.localdate)

    class Meta:
        ordering = ["-exam_date", "exam_name"]
        unique_together = ("student", "exam_name")

    def __str__(self) -> str:
        return f"{self.student.full_name} - {self.exam_name}"


def _secret_key_stream(nonce: bytes, length: int) -> bytes:
    seed = settings.SECRET_KEY.encode("utf-8")
    output = bytearray()
    counter = 0
    while len(output) < length:
        output.extend(hmac.new(seed, nonce + counter.to_bytes(4, "big"), hashlib.sha256).digest())
        counter += 1
    return bytes(output[:length])


def encrypt_gateway_secret(value: str) -> str:
    if not value:
        return ""
    raw = value.encode("utf-8")
    nonce = secrets.token_bytes(16)
    stream = _secret_key_stream(nonce, len(raw))
    cipher = bytes(left ^ right for left, right in zip(raw, stream))
    signature = hmac.new(settings.SECRET_KEY.encode("utf-8"), nonce + cipher, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(nonce + signature + cipher).decode("ascii")


def decrypt_gateway_secret(value: str) -> str:
    if not value:
        return ""
    try:
        payload = base64.urlsafe_b64decode(value.encode("ascii"))
        nonce, signature, cipher = payload[:16], payload[16:48], payload[48:]
        expected = hmac.new(settings.SECRET_KEY.encode("utf-8"), nonce + cipher, hashlib.sha256).digest()
        if not hmac.compare_digest(signature, expected):
            return ""
        stream = _secret_key_stream(nonce, len(cipher))
        return bytes(left ^ right for left, right in zip(cipher, stream)).decode("utf-8")
    except Exception:
        return ""


class FeeStructure(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="fee_structures")
    section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, null=True, blank=True, related_name="fee_structures")
    title = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    due_day = models.PositiveSmallIntegerField(default=10, validators=[MinValueValidator(1), MaxValueValidator(31)])
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fee_structures_created",
    )

    class Meta:
        ordering = ["campus__name", "section__grade_name", "title"]
        unique_together = ("campus", "section", "title")
        indexes = [
            models.Index(fields=["campus", "is_active"]),
            models.Index(fields=["section", "is_active"]),
            models.Index(fields=["due_day", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.campus.code})"

    def clean(self) -> None:
        if self.section_id and self.section.campus_id != self.campus_id:
            raise ValidationError({"section": "Fee structure section must belong to the selected campus."})
        if self.amount <= Decimal("0"):
            raise ValidationError({"amount": "Fee structure amount must be greater than zero."})
        if self.late_fee < Decimal("0") or self.discount_amount < Decimal("0"):
            raise ValidationError("Late fee and discount cannot be negative.")
        if self.discount_amount > self.amount + self.late_fee:
            raise ValidationError({"discount_amount": "Discount cannot exceed payable fee."})


class PaymentGatewayConfig(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="payment_gateway_configs")
    provider = models.CharField(max_length=32, choices=GatewayProvider.choices, default=GatewayProvider.RAZORPAY)
    key_id = models.CharField(max_length=160, blank=True)
    key_secret_encrypted = models.TextField(blank=True)
    webhook_secret_encrypted = models.TextField(blank=True)
    upi_id = models.CharField(max_length=120, blank=True)
    allowed_methods = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payment_gateway_configs_created",
    )

    class Meta:
        ordering = ["campus__name", "provider"]
        unique_together = ("campus", "provider")
        indexes = [
            models.Index(fields=["campus", "provider", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.campus.code} {self.provider}"

    def set_key_secret(self, value: str) -> None:
        if value:
            self.key_secret_encrypted = encrypt_gateway_secret(value)

    def get_key_secret(self) -> str:
        return decrypt_gateway_secret(self.key_secret_encrypted)

    def set_webhook_secret(self, value: str) -> None:
        if value:
            self.webhook_secret_encrypted = encrypt_gateway_secret(value)

    def get_webhook_secret(self) -> str:
        return decrypt_gateway_secret(self.webhook_secret_encrypted)


class SalarySetup(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="salary_setups")
    staff_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="salary_setups",
    )
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2)
    default_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    default_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="salary_setups_created",
    )

    class Meta:
        ordering = ["campus__name", "staff_user__username"]
        unique_together = ("campus", "staff_user")
        indexes = [
            models.Index(fields=["campus", "is_active"]),
            models.Index(fields=["staff_user", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.staff_user} salary setup ({self.campus.code})"

    def clean(self) -> None:
        if getattr(self.staff_user, "role", None) == "student":
            raise ValidationError({"staff_user": "Salary setup cannot be created for student users."})
        if getattr(self.staff_user, "school_id", None) and self.staff_user.school_id != self.campus_id:
            raise ValidationError({"staff_user": "Staff user must belong to the selected campus."})
        if self.gross_salary <= Decimal("0"):
            raise ValidationError({"gross_salary": "Gross salary must be greater than zero."})
        if self.default_deductions < Decimal("0") or self.default_bonus < Decimal("0"):
            raise ValidationError("Salary deductions and bonus cannot be negative.")


class FeeAssignment(AuditModel):
    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assignments",
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="fee_assignments")
    title = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    due_date = models.DateField()
    invoice_number = models.CharField(max_length=80, blank=True, null=True, unique=True)
    invoice_generated_at = models.DateTimeField(null=True, blank=True)
    reminder_count = models.PositiveIntegerField(default=0)
    last_reminder_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=FeeStatus.choices, default=FeeStatus.PENDING)

    class Meta:
        ordering = ["due_date"]
        indexes = [
            models.Index(fields=["student", "status"]),
            models.Index(fields=["due_date", "status"]),
            models.Index(fields=["fee_structure", "status"]),
            models.Index(fields=["invoice_number"]),
        ]

    def __str__(self) -> str:
        return f"{self.student.full_name} - {self.title}"

    @property
    def payable_amount(self) -> Decimal:
        return max(self.amount + self.late_fee - self.discount_amount, Decimal("0"))

    def refresh_status(self) -> None:
        total_paid = self.payments.aggregate(total=Sum("amount_paid")).get("total") or Decimal("0")
        if total_paid >= self.payable_amount:
            self.status = FeeStatus.PAID
        elif total_paid > 0:
            self.status = FeeStatus.PARTIAL
        elif self.due_date < timezone.localdate():
            self.status = FeeStatus.OVERDUE
        else:
            self.status = FeeStatus.PENDING
        self.save(update_fields=["status", "updated_at"])

    def clean(self) -> None:
        if self.amount <= Decimal("0"):
            raise ValidationError({"amount": "Fee amount must be greater than zero."})
        if self.fee_structure_id and self.fee_structure.campus_id != self.student.campus_id:
            raise ValidationError({"fee_structure": "Fee structure must belong to the student's campus."})
        if self.discount_amount < Decimal("0") or self.late_fee < Decimal("0"):
            raise ValidationError("Discount and late fee cannot be negative.")
        if self.discount_amount > self.amount + self.late_fee:
            raise ValidationError({"discount_amount": "Discount cannot exceed payable fee."})


class TransactionStatus(models.TextChoices):
    CREATED = "created", "Created"
    PENDING = "pending", "Pending"
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"
    REFUNDED = "refunded", "Refunded"


class Payment(AuditModel):
    campus = models.ForeignKey(
        Campus,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="payments",
    )
    fee_assignment = models.ForeignKey(
        FeeAssignment,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    pending_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    paid_on = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    reference_number = models.CharField(max_length=60, blank=True)
    payment_status = models.CharField(max_length=20, choices=TransactionStatus.choices, default=TransactionStatus.SUCCESS)
    gateway_name = models.CharField(max_length=40, blank=True)
    gateway_order_id = models.CharField(max_length=120, blank=True)
    transaction_id = models.CharField(max_length=120, blank=True)
    receipt_number = models.CharField(max_length=80, blank=True, null=True, unique=True)
    invoice_number = models.CharField(max_length=80, blank=True)
    webhook_verified = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    receipt_pdf_url = models.TextField(blank=True)
    collected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments_collected",
    )

    class Meta:
        ordering = ["-paid_on", "-created_at"]
        indexes = [
            models.Index(fields=["campus", "payment_status"]),
            models.Index(fields=["campus", "paid_on"]),
            models.Index(fields=["fee_assignment", "payment_status"]),
            models.Index(fields=["receipt_number"]),
            models.Index(fields=["transaction_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.fee_assignment} - {self.amount_paid}"

    def clean(self) -> None:
        if self.amount_paid <= Decimal("0"):
            raise ValidationError({"amount_paid": "Payment amount must be greater than zero."})
        if self.discount_amount < Decimal("0") or self.late_fee < Decimal("0") or self.pending_amount < Decimal("0"):
            raise ValidationError("Payment discount, late fee, and pending amount cannot be negative.")
        if self.fee_assignment_id:
            if self.campus_id and self.campus_id != self.fee_assignment.student.campus_id:
                raise ValidationError({"campus": "Payment campus must match the fee assignment campus."})
            existing_total = (
                self.fee_assignment.payments.exclude(pk=self.pk)
                .aggregate(total=Sum("amount_paid"))
                .get("total")
                or Decimal("0")
            )
            if existing_total + self.amount_paid > self.fee_assignment.payable_amount:
                raise ValidationError({"amount_paid": "Payment cannot exceed the fee outstanding amount."})

    def save(self, *args, **kwargs):
        if self.fee_assignment_id and not self.campus_id:
            self.campus_id = self.fee_assignment.student.campus_id
        if not self.paid_at and self.payment_status == TransactionStatus.SUCCESS:
            self.paid_at = timezone.now()
        if self.fee_assignment_id:
            existing_total = (
                self.fee_assignment.payments.exclude(pk=self.pk)
                .aggregate(total=Sum("amount_paid"))
                .get("total")
                or Decimal("0")
            )
            self.pending_amount = max(self.fee_assignment.payable_amount - existing_total - self.amount_paid, Decimal("0"))
            self.invoice_number = self.invoice_number or self.fee_assignment.invoice_number or ""
        self.full_clean()
        with transaction.atomic():
            super().save(*args, **kwargs)
            self.fee_assignment.refresh_status()


class SalaryPaymentStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PAYABLE = "payable", "Payable"
    PAID = "paid", "Paid"
    HOLD = "hold", "Hold"


class MessageChannel(models.TextChoices):
    EMAIL = "email", "Email"
    SMS = "sms", "SMS"
    WHATSAPP = "whatsapp", "WhatsApp"


class DeviceSyncStatus(models.TextChoices):
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"
    RETRYING = "retrying", "Retrying"


class MessageStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    QUEUED = "queued", "Queued"
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"


class RecordStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    ARCHIVED = "archived", "Archived"


class PaymentTransaction(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="payment_transactions")
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name="payment_transactions")
    fee_assignment = models.ForeignKey(
        FeeAssignment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name="transactions")
    provider = models.CharField(max_length=40, default="razorpay")
    method = models.CharField(max_length=32, choices=PaymentMethod.choices, default=PaymentMethod.ONLINE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    pending_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=8, default="INR")
    status = models.CharField(max_length=20, choices=TransactionStatus.choices, default=TransactionStatus.CREATED)
    gateway_name = models.CharField(max_length=40, blank=True)
    gateway_order_id = models.CharField(max_length=120, blank=True)
    gateway_payment_id = models.CharField(max_length=120, blank=True)
    gateway_signature = models.CharField(max_length=255, blank=True)
    transaction_id = models.CharField(max_length=120, blank=True)
    receipt_number = models.CharField(max_length=80, blank=True, null=True, unique=True)
    invoice_number = models.CharField(max_length=80, blank=True)
    webhook_verified = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    raw_payload = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payment_transactions_created",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["campus", "status"]),
            models.Index(fields=["campus", "status", "created_at"]),
            models.Index(fields=["student", "status"]),
            models.Index(fields=["fee_assignment", "status"]),
            models.Index(fields=["gateway_order_id"]),
            models.Index(fields=["gateway_payment_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.provider} {self.amount} {self.status}"

    def clean(self) -> None:
        if self.amount <= Decimal("0"):
            raise ValidationError({"amount": "Transaction amount must be greater than zero."})
        if self.discount_amount < Decimal("0") or self.late_fee < Decimal("0") or self.pending_amount < Decimal("0"):
            raise ValidationError("Transaction discount, late fee, and pending amount cannot be negative.")
        if self.student_id and self.student.campus_id != self.campus_id:
            raise ValidationError({"student": "Student must belong to the transaction campus."})
        if self.fee_assignment_id and self.fee_assignment.student.campus_id != self.campus_id:
            raise ValidationError({"fee_assignment": "Fee assignment must belong to the transaction campus."})


class SalaryRecord(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="salary_records")
    salary_setup = models.ForeignKey(
        SalarySetup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="salary_records",
    )
    staff_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="salary_records",
    )
    month = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.PositiveIntegerField(validators=[MinValueValidator(2000), MaxValueValidator(2100)])
    present_days = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    absent_days = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    leave_days = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    half_days = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    final_salary = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    payment_status = models.CharField(max_length=20, choices=SalaryPaymentStatus.choices, default=SalaryPaymentStatus.DRAFT)
    paid_on = models.DateField(null=True, blank=True)
    slip_url = models.URLField(blank=True)
    slip_number = models.CharField(max_length=80, blank=True, null=True, unique=True)
    payment_reference = models.CharField(max_length=120, blank=True)
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="salary_records_paid",
    )
    status = models.CharField(max_length=20, choices=RecordStatus.choices, default=RecordStatus.ACTIVE)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="salary_records_created",
    )

    class Meta:
        ordering = ["-year", "-month", "staff_user__username"]
        unique_together = ("campus", "staff_user", "month", "year")
        indexes = [
            models.Index(fields=["campus", "year", "month"]),
            models.Index(fields=["staff_user", "payment_status"]),
        ]

    def __str__(self) -> str:
        return f"{self.staff_user} salary {self.month}/{self.year}"

    def clean(self) -> None:
        if getattr(self.staff_user, "role", None) == "student":
            raise ValidationError({"staff_user": "Salary records cannot be created for student users."})
        if self.salary_setup_id and self.salary_setup.campus_id != self.campus_id:
            raise ValidationError({"salary_setup": "Salary setup must belong to the salary record campus."})
        if self.salary_setup_id and self.salary_setup.staff_user_id != self.staff_user_id:
            raise ValidationError({"salary_setup": "Salary setup must belong to the selected staff user."})
        if getattr(self.staff_user, "school_id", None) and self.staff_user.school_id != self.campus_id:
            raise ValidationError({"staff_user": "Staff user must belong to the selected campus."})
        if min(self.present_days, self.absent_days, self.leave_days, self.half_days, self.gross_salary, self.deductions, self.bonus, self.final_salary) < Decimal("0"):
            raise ValidationError("Salary values cannot be negative.")


class FinanceEvent(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="finance_events")
    event_type = models.CharField(max_length=40, choices=FinanceEventType.choices)
    payload = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="finance_events_created",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["campus", "event_type", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} {self.campus.code}"


class AcademicEvent(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="academic_events")
    event_type = models.CharField(max_length=40, choices=AcademicEventType.choices)
    payload = models.JSONField(default=dict, blank=True)
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="academic_events",
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="academic_events_for_teacher",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="academic_events_created",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["campus", "event_type", "created_at"]),
            models.Index(fields=["student", "created_at"]),
            models.Index(fields=["teacher", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} {self.campus.code}"


class MessageTemplate(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, null=True, blank=True, related_name="message_templates")
    name = models.CharField(max_length=120)
    trigger = models.CharField(max_length=80)
    channel = models.CharField(max_length=20, choices=MessageChannel.choices)
    subject = models.CharField(max_length=160, blank=True)
    body = models.TextField()
    variables = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, choices=RecordStatus.choices, default=RecordStatus.ACTIVE)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="message_templates_created",
    )

    class Meta:
        ordering = ["campus__name", "channel", "name"]
        unique_together = ("campus", "name", "channel")
        indexes = [
            models.Index(fields=["campus", "channel", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.channel})"


class CommunicationSetting(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="communication_settings")
    channel = models.CharField(max_length=20, choices=MessageChannel.choices)
    provider_name = models.CharField(max_length=120, blank=True)
    sender_id = models.CharField(max_length=120, blank=True)
    api_url = models.URLField(blank=True)
    api_key = models.TextField(blank=True)
    api_secret = models.TextField(blank=True)
    smtp_host = models.CharField(max_length=180, blank=True)
    smtp_port = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(65535)])
    smtp_username = models.CharField(max_length=180, blank=True)
    smtp_password = models.TextField(blank=True)
    whatsapp_phone_number_id = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="communication_settings_created",
    )

    class Meta:
        ordering = ["campus__name", "channel"]
        unique_together = ("campus", "channel")
        indexes = [
            models.Index(fields=["campus", "channel", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.campus.code} {self.channel}"

    def set_api_key(self, value: str) -> None:
        if value:
            self.api_key = encrypt_gateway_secret(value)

    def get_api_key(self) -> str:
        return decrypt_gateway_secret(self.api_key)

    def set_api_secret(self, value: str) -> None:
        if value:
            self.api_secret = encrypt_gateway_secret(value)

    def get_api_secret(self) -> str:
        return decrypt_gateway_secret(self.api_secret)

    def set_smtp_password(self, value: str) -> None:
        if value:
            self.smtp_password = encrypt_gateway_secret(value)

    def get_smtp_password(self) -> str:
        return decrypt_gateway_secret(self.smtp_password)


class OutboundMessage(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="outbound_messages")
    template = models.ForeignKey(MessageTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name="messages")
    recipient_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="messages_received",
    )
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name="messages")
    channel = models.CharField(max_length=20, choices=MessageChannel.choices)
    recipient = models.CharField(max_length=180)
    subject = models.CharField(max_length=160, blank=True)
    body = models.TextField()
    status = models.CharField(max_length=20, choices=MessageStatus.choices, default=MessageStatus.QUEUED)
    provider = models.CharField(max_length=80, blank=True)
    provider_reference = models.CharField(max_length=160, blank=True)
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="messages_created",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["campus", "channel", "status"]),
            models.Index(fields=["recipient_user", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.channel} to {self.recipient}"

    def clean(self) -> None:
        if self.student_id and self.student.campus_id != self.campus_id:
            raise ValidationError({"student": "Student must belong to the message campus."})
        if self.template_id and self.template.campus_id and self.template.campus_id != self.campus_id:
            raise ValidationError({"template": "Template must belong to the message campus or be global."})


class DeviceSyncLog(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="device_sync_logs")
    device = models.ForeignKey(AttendanceDevice, on_delete=models.CASCADE, related_name="sync_logs")
    status = models.CharField(max_length=20, choices=DeviceSyncStatus.choices, default=DeviceSyncStatus.SUCCESS)
    log_type = models.CharField(max_length=40, default="sync")
    payload = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    attempt_count = models.PositiveIntegerField(default=1)
    synced_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="device_sync_logs_created",
    )

    class Meta:
        ordering = ["-synced_at"]
        indexes = [
            models.Index(fields=["campus", "status", "synced_at"]),
            models.Index(fields=["device", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.device.device_code} {self.status}"

    def clean(self) -> None:
        if self.device_id and self.campus_id and self.device.campus_id != self.campus_id:
            raise ValidationError({"device": "Device must belong to the sync log campus."})


class AILog(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, null=True, blank=True, related_name="ai_logs")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="ai_logs")
    role = models.CharField(max_length=32)
    feature = models.CharField(max_length=80)
    prompt = models.TextField()
    response = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=RecordStatus.choices, default=RecordStatus.ACTIVE)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_logs_created",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["campus", "role", "feature"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.role} AI - {self.feature}"


class Document(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="documents")
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name="documents")
    staff_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="staff_documents",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents_uploaded",
    )
    title = models.CharField(max_length=160)
    document_type = models.CharField(max_length=80)
    file_url = models.TextField()
    status = models.CharField(max_length=20, choices=RecordStatus.choices, default=RecordStatus.ACTIVE)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents_created",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["campus", "document_type", "status"]),
            models.Index(fields=["student", "document_type"]),
            models.Index(fields=["staff_user", "document_type"]),
        ]

    def __str__(self) -> str:
        return self.title

    def clean(self) -> None:
        if self.student_id and self.student.campus_id != self.campus_id:
            raise ValidationError({"student": "Document student must belong to the selected campus."})
        if self.staff_user_id:
            if getattr(self.staff_user, "role", None) == "student":
                raise ValidationError({"staff_user": "Staff document cannot be linked to a student user."})
            if self.staff_user.school_id and self.staff_user.school_id != self.campus_id:
                raise ValidationError({"staff_user": "Staff user must belong to the selected campus."})


class PlatformSetting(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, null=True, blank=True, related_name="settings")
    key = models.CharField(max_length=120)
    value = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=RecordStatus.choices, default=RecordStatus.ACTIVE)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="platform_settings_created",
    )

    class Meta:
        ordering = ["campus__name", "key"]
        unique_together = ("campus", "key")
        indexes = [
            models.Index(fields=["campus", "status"]),
            models.Index(fields=["key"]),
        ]

    def __str__(self) -> str:
        scope = self.campus.code if self.campus_id else "global"
        return f"{scope}:{self.key}"


class ApprovalRequest(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="approval_requests")
    title = models.CharField(max_length=160)
    entity_type = models.CharField(max_length=80)
    entity_id = models.CharField(max_length=80, blank=True)
    description = models.TextField(blank=True)
    payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=ApprovalStatus.choices, default=ApprovalStatus.PENDING)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approval_requests_created",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approval_requests_reviewed",
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    decision_note = models.TextField(blank=True)

    class Meta:
        ordering = ["status", "-created_at"]
        indexes = [
            models.Index(fields=["campus", "status"]),
            models.Index(fields=["entity_type", "entity_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.status})"

    def decide(self, *, status_value: str, reviewer, note: str = "") -> None:
        if status_value not in {ApprovalStatus.APPROVED, ApprovalStatus.REJECTED}:
            raise ValidationError({"status": "Decision must be approved or rejected."})
        self.status = status_value
        self.reviewed_by = reviewer
        self.decided_at = timezone.now()
        self.decision_note = note
        self.save(update_fields=["status", "reviewed_by", "decided_at", "decision_note", "updated_at"])


class Announcement(AuditModel):
    campus = models.ForeignKey(
        Campus,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="announcements",
        help_text="Null campus is reserved for global Super Admin announcements.",
    )
    title = models.CharField(max_length=160)
    message = models.TextField()
    audience = models.CharField(
        max_length=20,
        choices=AnnouncementAudience.choices,
        default=AnnouncementAudience.ALL,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="announcements_created",
    )
    is_active = models.BooleanField(default=True)
    publish_on = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-publish_on", "-created_at"]
        indexes = [
            models.Index(fields=["campus", "audience", "is_active"]),
            models.Index(fields=["audience", "is_active"]),
            models.Index(fields=["publish_on"]),
        ]

    def __str__(self) -> str:
        return self.title


class SupportTicket(AuditModel):
    campus = models.ForeignKey(
        Campus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="support_tickets",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="support_tickets_created",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="support_tickets_reviewed",
    )
    subject = models.CharField(max_length=160)
    message = models.TextField()
    category = models.CharField(max_length=40, default="general")
    priority = models.CharField(
        max_length=20,
        choices=SupportTicketPriority.choices,
        default=SupportTicketPriority.NORMAL,
    )
    status = models.CharField(
        max_length=20,
        choices=SupportTicketStatus.choices,
        default=SupportTicketStatus.OPEN,
    )
    response_note = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["status", "-created_at"]
        indexes = [
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["created_by", "created_at"]),
            models.Index(fields=["campus", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.subject} ({self.status})"


class AdmissionFormTemplate(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="admission_form_templates")
    name = models.CharField(max_length=140)
    academic_year = models.CharField(max_length=40, blank=True)
    form_schema = models.JSONField(default=list, blank=True)
    admission_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    is_public = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=RecordStatus.choices, default=RecordStatus.ACTIVE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="admission_forms_created")

    class Meta:
        ordering = ["campus__name", "name"]
        unique_together = ("campus", "name", "academic_year")
        indexes = [
            models.Index(fields=["campus", "is_public", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.campus.code} {self.name}"

    def clean(self) -> None:
        if self.admission_fee < Decimal("0"):
            raise ValidationError({"admission_fee": "Admission fee cannot be negative."})


class AdmissionApplication(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="admission_applications")
    form_template = models.ForeignKey(AdmissionFormTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name="applications")
    target_section = models.ForeignKey(ClassSection, on_delete=models.SET_NULL, null=True, blank=True, related_name="admission_applications")
    application_number = models.CharField(max_length=80, unique=True)
    tracking_code = models.CharField(max_length=80, unique=True)
    applicant_first_name = models.CharField(max_length=80)
    applicant_last_name = models.CharField(max_length=80, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    guardian_name = models.CharField(max_length=140)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=40)
    form_data = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=32, choices=AdmissionApplicationStatus.choices, default=AdmissionApplicationStatus.NEW)
    admission_fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    payment_status = models.CharField(max_length=20, choices=TransactionStatus.choices, default=TransactionStatus.PENDING)
    payment_reference = models.CharField(max_length=120, blank=True)
    interview_at = models.DateTimeField(null=True, blank=True)
    decision_note = models.TextField(blank=True)
    admitted_student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name="admission_applications")
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="admission_applications_reviewed")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="admission_applications_created")

    class Meta:
        ordering = ["status", "-created_at"]
        indexes = [
            models.Index(fields=["campus", "status", "created_at"]),
            models.Index(fields=["tracking_code"]),
            models.Index(fields=["target_section", "status"]),
        ]

    @property
    def applicant_name(self) -> str:
        return " ".join(part for part in [self.applicant_first_name, self.applicant_last_name] if part).strip()

    def __str__(self) -> str:
        return f"{self.application_number} - {self.applicant_name}"

    def clean(self) -> None:
        if self.form_template_id and self.form_template.campus_id != self.campus_id:
            raise ValidationError({"form_template": "Admission form must belong to the selected campus."})
        if self.target_section_id and self.target_section.campus_id != self.campus_id:
            raise ValidationError({"target_section": "Target class must belong to the selected campus."})
        if self.admitted_student_id and self.admitted_student.campus_id != self.campus_id:
            raise ValidationError({"admitted_student": "Admitted student must belong to the selected campus."})
        if self.admission_fee_amount < Decimal("0"):
            raise ValidationError({"admission_fee_amount": "Admission fee cannot be negative."})


class AdmissionDocument(AuditModel):
    application = models.ForeignKey(AdmissionApplication, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=160)
    document_type = models.CharField(max_length=80)
    file_url = models.TextField()
    file_name = models.CharField(max_length=180, blank=True)
    file_content_type = models.CharField(max_length=100, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="admission_documents_uploaded")

    class Meta:
        ordering = ["application__application_number", "title"]
        indexes = [
            models.Index(fields=["application", "document_type"]),
        ]

    def __str__(self) -> str:
        return f"{self.application.application_number} {self.title}"


class TransportDriver(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="transport_drivers")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="transport_driver_profiles")
    full_name = models.CharField(max_length=140)
    phone = models.CharField(max_length=40)
    license_number = models.CharField(max_length=80)
    emergency_contact = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=20, choices=RecordStatus.choices, default=RecordStatus.ACTIVE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="transport_drivers_created")

    class Meta:
        ordering = ["campus__name", "full_name"]
        unique_together = ("campus", "license_number")
        indexes = [
            models.Index(fields=["campus", "status"]),
        ]

    def __str__(self) -> str:
        return self.full_name

    def clean(self) -> None:
        if self.user_id and self.user.school_id and self.user.school_id != self.campus_id:
            raise ValidationError({"user": "Driver user must belong to the selected campus."})


class TransportVehicleAttendance(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="vehicle_attendance")
    vehicle = models.ForeignKey(TransportVehicle, on_delete=models.CASCADE, related_name="attendance_records")
    driver = models.ForeignKey(TransportDriver, on_delete=models.SET_NULL, null=True, blank=True, related_name="attendance_records")
    date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=20, choices=TransportAttendanceStatus.choices, default=TransportAttendanceStatus.PRESENT)
    odometer_reading = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    marked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="vehicle_attendance_marked")

    class Meta:
        ordering = ["-date", "vehicle__vehicle_number"]
        unique_together = ("vehicle", "date")
        indexes = [
            models.Index(fields=["campus", "date", "status"]),
            models.Index(fields=["vehicle", "date"]),
        ]

    def __str__(self) -> str:
        return f"{self.vehicle.vehicle_number} {self.date}"

    def clean(self) -> None:
        if self.vehicle_id and self.vehicle.campus_id != self.campus_id:
            raise ValidationError({"vehicle": "Vehicle must belong to the selected campus."})
        if self.driver_id and self.driver.campus_id != self.campus_id:
            raise ValidationError({"driver": "Driver must belong to the selected campus."})


class TransportTripLog(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="transport_trip_logs")
    route = models.ForeignKey(TransportRoute, on_delete=models.SET_NULL, null=True, blank=True, related_name="trip_logs")
    vehicle = models.ForeignKey(TransportVehicle, on_delete=models.CASCADE, related_name="trip_logs")
    driver = models.ForeignKey(TransportDriver, on_delete=models.SET_NULL, null=True, blank=True, related_name="trip_logs")
    trip_date = models.DateField(default=timezone.localdate)
    trip_type = models.CharField(max_length=20, choices=TransportTripType.choices, default=TransportTripType.PICKUP)
    status = models.CharField(max_length=20, choices=TransportTripStatus.choices, default=TransportTripStatus.SCHEDULED)
    scheduled_time = models.TimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    gps_payload = models.JSONField(default=dict, blank=True)
    pickup_drop_report = models.JSONField(default=list, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="transport_trips_created")

    class Meta:
        ordering = ["-trip_date", "trip_type"]
        indexes = [
            models.Index(fields=["campus", "trip_date", "trip_type"]),
            models.Index(fields=["vehicle", "trip_date"]),
            models.Index(fields=["status", "trip_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.vehicle.vehicle_number} {self.trip_type} {self.trip_date}"

    def clean(self) -> None:
        if self.route_id and self.route.campus_id != self.campus_id:
            raise ValidationError({"route": "Route must belong to the selected campus."})
        if self.vehicle_id and self.vehicle.campus_id != self.campus_id:
            raise ValidationError({"vehicle": "Vehicle must belong to the selected campus."})
        if self.driver_id and self.driver.campus_id != self.campus_id:
            raise ValidationError({"driver": "Driver must belong to the selected campus."})


class DigitalLibraryResource(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="digital_library_resources")
    book = models.ForeignKey(LibraryBook, on_delete=models.SET_NULL, null=True, blank=True, related_name="digital_resources")
    title = models.CharField(max_length=180)
    resource_type = models.CharField(max_length=40, default="ebook")
    file_url = models.TextField()
    file_name = models.CharField(max_length=180, blank=True)
    file_content_type = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=RecordStatus.choices, default=RecordStatus.ACTIVE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="digital_library_resources_created")

    class Meta:
        ordering = ["campus__name", "title"]
        indexes = [
            models.Index(fields=["campus", "status", "resource_type"]),
        ]

    def __str__(self) -> str:
        return self.title

    def clean(self) -> None:
        if self.book_id and self.book.campus_id != self.campus_id:
            raise ValidationError({"book": "Book must belong to the selected campus."})


class LibraryBookRequest(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="library_book_requests")
    book = models.ForeignKey(LibraryBook, on_delete=models.CASCADE, related_name="book_requests")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True, related_name="library_book_requests")
    staff_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="library_book_requests")
    status = models.CharField(max_length=20, choices=LibraryRequestStatus.choices, default=LibraryRequestStatus.REQUESTED)
    request_note = models.TextField(blank=True)
    decision_note = models.TextField(blank=True)
    decided_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="library_book_requests_decided")

    class Meta:
        ordering = ["status", "-created_at"]
        indexes = [
            models.Index(fields=["campus", "status"]),
            models.Index(fields=["student", "status"]),
            models.Index(fields=["staff_user", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.book.title} {self.status}"

    def clean(self) -> None:
        if bool(self.student_id) == bool(self.staff_user_id):
            raise ValidationError({"student": "Select exactly one requester: student or staff user."})
        if self.book_id and self.book.campus_id != self.campus_id:
            raise ValidationError({"book": "Book must belong to the selected campus."})
        if self.student_id and self.student.campus_id != self.campus_id:
            raise ValidationError({"student": "Student must belong to the selected campus."})
        if self.staff_user_id and getattr(self.staff_user, "role", None) == "student":
            raise ValidationError({"staff_user": "Use the student requester field for student users."})


class InventoryAsset(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="inventory_assets")
    asset_code = models.CharField(max_length=80, unique=True)
    name = models.CharField(max_length=160)
    category = models.CharField(max_length=32, choices=AssetCategory.choices, default=AssetCategory.OTHER)
    serial_number = models.CharField(max_length=120, blank=True)
    location = models.CharField(max_length=160, blank=True)
    allocated_to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="allocated_assets")
    allocated_to_student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name="allocated_assets")
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    current_value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    depreciation_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=20, choices=AssetStatus.choices, default=AssetStatus.AVAILABLE)
    metadata = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="inventory_assets_created")

    class Meta:
        ordering = ["campus__name", "category", "name"]
        indexes = [
            models.Index(fields=["campus", "category", "status"]),
            models.Index(fields=["asset_code"]),
            models.Index(fields=["serial_number"]),
        ]

    def __str__(self) -> str:
        return f"{self.asset_code} {self.name}"

    def clean(self) -> None:
        if self.allocated_to_user_id and self.allocated_to_user.school_id and self.allocated_to_user.school_id != self.campus_id:
            raise ValidationError({"allocated_to_user": "Allocated user must belong to the selected campus."})
        if self.allocated_to_student_id and self.allocated_to_student.campus_id != self.campus_id:
            raise ValidationError({"allocated_to_student": "Allocated student must belong to the selected campus."})
        if min(self.purchase_cost, self.current_value, self.depreciation_rate) < Decimal("0"):
            raise ValidationError("Asset cost, current value, and depreciation cannot be negative.")


class AssetMaintenanceLog(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="asset_maintenance_logs")
    asset = models.ForeignKey(InventoryAsset, on_delete=models.CASCADE, related_name="maintenance_logs")
    issue = models.CharField(max_length=180)
    service_provider = models.CharField(max_length=160, blank=True)
    maintenance_date = models.DateField(default=timezone.localdate)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=20, choices=RecordStatus.choices, default=RecordStatus.ACTIVE)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="asset_maintenance_logs_created")

    class Meta:
        ordering = ["-maintenance_date", "asset__asset_code"]
        indexes = [
            models.Index(fields=["campus", "maintenance_date"]),
            models.Index(fields=["asset", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.asset.asset_code} {self.issue}"

    def clean(self) -> None:
        if self.asset_id and self.asset.campus_id != self.campus_id:
            raise ValidationError({"asset": "Asset must belong to the selected campus."})
        if self.cost < Decimal("0"):
            raise ValidationError({"cost": "Maintenance cost cannot be negative."})


class SchoolWebsiteContent(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="website_contents")
    content_type = models.CharField(max_length=20, choices=WebsiteContentType.choices, default=WebsiteContentType.PAGE)
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=180)
    body = models.TextField(blank=True)
    summary = models.CharField(max_length=240, blank=True)
    media_url = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    publish_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="website_contents_created")

    class Meta:
        ordering = ["sort_order", "-publish_at", "title"]
        unique_together = ("campus", "slug")
        indexes = [
            models.Index(fields=["campus", "content_type", "is_published"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self) -> str:
        return f"{self.campus.code} {self.slug}"


class PushNotificationDevice(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, null=True, blank=True, related_name="push_devices")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="push_devices")
    platform = models.CharField(max_length=20, choices=PushPlatform.choices)
    device_id = models.CharField(max_length=160, blank=True)
    token = models.TextField()
    is_active = models.BooleanField(default=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["user__username", "platform"]
        unique_together = ("user", "platform", "device_id")
        indexes = [
            models.Index(fields=["campus", "platform", "is_active"]),
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} {self.platform}"

    def clean(self) -> None:
        if self.campus_id and self.user.school_id and self.user.school_id != self.campus_id:
            raise ValidationError({"user": "Push device user must belong to the selected campus."})


class PushNotificationLog(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, null=True, blank=True, related_name="push_notification_logs")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="push_notification_logs")
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name="push_notification_logs")
    event_type = models.CharField(max_length=80)
    title = models.CharField(max_length=160)
    body = models.TextField()
    payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=PushNotificationStatus.choices, default=PushNotificationStatus.QUEUED)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="push_notifications_created")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["campus", "event_type", "status"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["student", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} {self.status}"

    def clean(self) -> None:
        if self.student_id and self.campus_id and self.student.campus_id != self.campus_id:
            raise ValidationError({"student": "Student must belong to the selected campus."})


class MarketplacePlugin(AuditModel):
    code = models.CharField(max_length=80, unique=True)
    name = models.CharField(max_length=140)
    plugin_type = models.CharField(max_length=20, choices=MarketplacePluginType.choices, default=MarketplacePluginType.CUSTOM)
    provider_name = models.CharField(max_length=140, blank=True)
    description = models.TextField(blank=True)
    config_schema = models.JSONField(default=dict, blank=True)
    is_enabled = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="marketplace_plugins_created")

    class Meta:
        ordering = ["plugin_type", "name"]
        indexes = [
            models.Index(fields=["plugin_type", "is_enabled"]),
            models.Index(fields=["code"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.plugin_type})"


class SchoolPluginConfig(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="plugin_configs")
    plugin = models.ForeignKey(MarketplacePlugin, on_delete=models.CASCADE, related_name="school_configs")
    is_enabled = models.BooleanField(default=True)
    config = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="school_plugin_configs_created")

    class Meta:
        ordering = ["campus__name", "plugin__name"]
        unique_together = ("campus", "plugin")
        indexes = [
            models.Index(fields=["campus", "is_enabled"]),
            models.Index(fields=["plugin", "is_enabled"]),
        ]

    def __str__(self) -> str:
        return f"{self.campus.code} {self.plugin.code}"


class AccountingLedgerEntry(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name="accounting_ledger_entries")
    entry_type = models.CharField(max_length=32, choices=AccountingEntryType.choices)
    ledger_name = models.CharField(max_length=140)
    reference_type = models.CharField(max_length=80, blank=True)
    reference_id = models.CharField(max_length=80, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    entry_date = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="accounting_entries_created")

    class Meta:
        ordering = ["-entry_date", "-created_at"]
        indexes = [
            models.Index(fields=["campus", "entry_type", "entry_date"]),
            models.Index(fields=["reference_type", "reference_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.ledger_name} {self.amount}"

    def clean(self) -> None:
        if self.amount < Decimal("0") or self.tax_rate < Decimal("0") or self.gst_amount < Decimal("0"):
            raise ValidationError("Accounting amounts and tax cannot be negative.")


class ReportDefinition(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, null=True, blank=True, related_name="report_definitions")
    name = models.CharField(max_length=140)
    report_type = models.CharField(max_length=32, choices=ReportDefinitionType.choices, default=ReportDefinitionType.CUSTOM)
    description = models.TextField(blank=True)
    columns = models.JSONField(default=list, blank=True)
    filters = models.JSONField(default=dict, blank=True)
    sort = models.JSONField(default=list, blank=True)
    chart_config = models.JSONField(default=dict, blank=True)
    is_public_to_school = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="report_definitions_created")

    class Meta:
        ordering = ["campus__name", "report_type", "name"]
        indexes = [
            models.Index(fields=["campus", "report_type"]),
            models.Index(fields=["is_public_to_school"]),
        ]

    def __str__(self) -> str:
        return self.name


class SecurityPolicy(AuditModel):
    campus = models.OneToOneField(Campus, on_delete=models.CASCADE, null=True, blank=True, related_name="security_policy")
    two_factor_required = models.BooleanField(default=False)
    allowed_ip_ranges = models.JSONField(default=list, blank=True)
    blocked_ip_ranges = models.JSONField(default=list, blank=True)
    max_active_sessions = models.PositiveIntegerField(default=5)
    force_password_change_days = models.PositiveIntegerField(default=90)
    suspicious_login_threshold = models.PositiveIntegerField(default=5)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="security_policies_created")

    class Meta:
        ordering = ["campus__name"]

    def __str__(self) -> str:
        return self.campus.code if self.campus_id else "platform security policy"


class DeviceLoginSession(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, null=True, blank=True, related_name="device_login_sessions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="device_login_sessions")
    device_id = models.CharField(max_length=180, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    login_at = models.DateTimeField(default=timezone.now)
    logout_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    forced_logout = models.BooleanField(default=False)
    risk_score = models.PositiveSmallIntegerField(default=0)
    event_type = models.CharField(max_length=32, choices=SecurityEventType.choices, default=SecurityEventType.LOGIN)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-login_at"]
        indexes = [
            models.Index(fields=["campus", "is_active", "login_at"]),
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["event_type", "risk_score"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} {self.login_at}"


class SecurityEvent(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, null=True, blank=True, related_name="security_events")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="security_events")
    event_type = models.CharField(max_length=32, choices=SecurityEventType.choices)
    severity = models.CharField(max_length=20, default="info")
    summary = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="security_events_resolved")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["campus", "event_type", "created_at"]),
            models.Index(fields=["severity", "resolved_at"]),
        ]

    def __str__(self) -> str:
        return self.summary


class ProductionAuditRun(AuditModel):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, null=True, blank=True, related_name="production_audit_runs")
    status = models.CharField(max_length=20, choices=ProductionAuditStatus.choices, default=ProductionAuditStatus.QUEUED)
    checks = models.JSONField(default=list, blank=True)
    summary = models.JSONField(default=dict, blank=True)
    report_url = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="production_audit_runs_created")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["campus", "status", "created_at"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self) -> str:
        scope = self.campus.code if self.campus_id else "platform"
        return f"{scope} production audit {self.status}"
