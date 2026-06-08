from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class UserRole(models.TextChoices):
    SUPER_ADMIN = "super_admin", "Super Admin"
    SCHOOL_ADMIN = "school_admin", "School Admin"
    ACCOUNT = "account", "Account"
    TEACHER = "teacher", "Teacher"
    STUDENT = "student", "Student"


class GenderChoice(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"
    OTHER = "other", "Other"


class User(AbstractUser):
    role = models.CharField(max_length=32, choices=UserRole.choices, default=UserRole.SCHOOL_ADMIN)
    school = models.ForeignKey(
        "core.Campus",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="users",
        help_text="Single school tenant assigned to this account. Super Admin accounts are global.",
    )
    phone_number = models.CharField(max_length=20, blank=True)
    must_change_password = models.BooleanField(default=False)
    gender = models.CharField(max_length=20, choices=GenderChoice.choices, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=20, blank=True)
    blood_group = models.CharField(max_length=8, blank=True)
    emergency_contact_name = models.CharField(max_length=120, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    qualification = models.CharField(max_length=180, blank=True)
    profile_photo_url = models.URLField(blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["username"]
        indexes = [
            models.Index(fields=["school", "role", "is_active"], name="accounts_us_school_97f214_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"

    @property
    def is_protected_super_admin(self) -> bool:
        return self.role == UserRole.SUPER_ADMIN or self.is_superuser

    def save(self, *args, **kwargs):
        if self.role == UserRole.SUPER_ADMIN or self.is_superuser:
            self.role = UserRole.SUPER_ADMIN
            self.school = None
            self.is_staff = True
            self.is_superuser = True
            self.is_active = True
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_protected_super_admin:
            raise ValidationError("Super Admin accounts cannot be deleted.")
        return super().delete(*args, **kwargs)
