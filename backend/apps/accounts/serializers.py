from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .captcha import validate_captcha_response
from .models import User, UserRole


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    campuses = serializers.SerializerMethodField()
    school_name = serializers.CharField(source="school.name", read_only=True)
    school_code = serializers.CharField(source="school.code", read_only=True)
    school_status = serializers.CharField(source="school.status", read_only=True)
    linked_student_profile = serializers.SerializerMethodField()
    linked_staff_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "school",
            "school_name",
            "school_code",
            "school_status",
            "phone_number",
            "must_change_password",
            "campuses",
            "is_active",
            "gender",
            "date_of_birth",
            "address",
            "city",
            "state",
            "pincode",
            "blood_group",
            "emergency_contact_name",
            "emergency_contact_phone",
            "qualification",
            "profile_photo_url",
            "bio",
            "linked_student_profile",
            "linked_staff_profile",
        )
        read_only_fields = (
            "id",
            "username",
            "role",
            "school",
            "school_name",
            "school_code",
            "school_status",
            "must_change_password",
            "campuses",
            "is_active",
            "linked_student_profile",
            "linked_staff_profile",
        )

    def get_full_name(self, obj: User) -> str:
        return obj.get_full_name() or obj.username

    def get_campuses(self, obj: User) -> list[dict]:
        memberships = getattr(obj, "campus_memberships", None)
        if memberships is None:
            return []
        scoped_memberships = list(memberships.select_related("campus").all())
        if not scoped_memberships and obj.school_id:
            return [
                {
                    "id": obj.school_id,
                    "name": obj.school.name,
                    "code": obj.school.code,
                    "logo_url": obj.school.logo_url,
                    "logo_alt_text": obj.school.logo_alt_text,
                    "role": "school",
                    "is_primary": True,
                    "can_manage_users": obj.role == UserRole.SCHOOL_ADMIN,
                    "can_configure_attendance": obj.role == UserRole.SCHOOL_ADMIN,
                }
            ]
        return [
            {
                "id": membership.campus_id,
                "name": membership.campus.name,
                "code": membership.campus.code,
                "logo_url": membership.campus.logo_url,
                "logo_alt_text": membership.campus.logo_alt_text,
                "role": membership.role,
                "is_primary": membership.is_primary,
                "can_manage_users": membership.can_manage_users,
                "can_configure_attendance": membership.can_configure_attendance,
            }
            for membership in scoped_memberships
        ]

    def get_linked_student_profile(self, obj: User) -> dict | None:
        try:
            student = obj.student_profile
            return {
                "id": student.id,
                "admission_number": student.admission_number,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "grade_name": student.section.grade_name if student.section else "",
                "section_name": student.section.section_name if student.section else "",
                "status": student.status,
            }
        except Exception:
            return None

    def get_linked_staff_profile(self, obj: User) -> dict | None:
        try:
            staff = obj.staff_profile
            return {
                "id": staff.id,
                "employee_code": staff.employee_code,
                "designation": staff.designation,
                "department": staff.department,
                "status": staff.status,
            }
        except Exception:
            return None


class UserAdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    full_name = serializers.SerializerMethodField()
    campuses = serializers.SerializerMethodField()
    school_name = serializers.CharField(source="school.name", read_only=True)
    school_code = serializers.CharField(source="school.code", read_only=True)
    school_status = serializers.CharField(source="school.status", read_only=True)
    campus_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )
    linked_student_profile = serializers.SerializerMethodField()
    linked_staff_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "school",
            "school_name",
            "school_code",
            "school_status",
            "phone_number",
            "campuses",
            "campus_ids",
            "must_change_password",
            "is_active",
            "is_staff",
            "password",
            "gender",
            "date_of_birth",
            "address",
            "city",
            "state",
            "pincode",
            "blood_group",
            "emergency_contact_name",
            "emergency_contact_phone",
            "qualification",
            "profile_photo_url",
            "bio",
            "linked_student_profile",
            "linked_staff_profile",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")

    def get_linked_student_profile(self, obj: User) -> dict | None:
        try:
            student = obj.student_profile
            return {
                "id": student.id,
                "admission_number": student.admission_number,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "grade_name": student.section.grade_name if student.section else "",
                "section_name": student.section.section_name if student.section else "",
                "status": student.status,
            }
        except Exception:
            return None

    def get_linked_staff_profile(self, obj: User) -> dict | None:
        try:
            staff = obj.staff_profile
            return {
                "id": staff.id,
                "employee_code": staff.employee_code,
                "designation": staff.designation,
                "department": staff.department,
                "status": staff.status,
            }
        except Exception:
            return None

    def get_full_name(self, obj: User) -> str:
        return obj.get_full_name() or obj.username

    def get_campuses(self, obj: User) -> list[dict]:
        return [
            {
                "id": membership.campus_id,
                "name": membership.campus.name,
                "code": membership.campus.code,
                "logo_url": membership.campus.logo_url,
                "logo_alt_text": membership.campus.logo_alt_text,
                "role": membership.role,
                "is_primary": membership.is_primary,
                "can_manage_users": membership.can_manage_users,
                "can_configure_attendance": membership.can_configure_attendance,
            }
            for membership in obj.campus_memberships.select_related("campus").all()
        ]

    def validate_role(self, value):
        if value == UserRole.SUPER_ADMIN:
            request = self.context.get("request")
            if not request or getattr(request.user, "role", None) != UserRole.SUPER_ADMIN:
                raise serializers.ValidationError("Only a super admin can create or edit super admins.")
        return value

    def validate_campus_ids(self, value):
        if len(set(value)) > 1:
            raise serializers.ValidationError("Every non-super-admin user must belong to exactly one school.")
        request = self.context.get("request")
        if not request or getattr(request.user, "role", None) == UserRole.SUPER_ADMIN:
            return value
        from apps.core.models import CampusMembership

        allowed = set(CampusMembership.objects.filter(user=request.user).values_list("campus_id", flat=True))
        if not set(value).issubset(allowed):
            raise serializers.ValidationError("Admins can assign users only to their own campuses.")
        return value

    def validate(self, attrs):
        role = attrs.get("role", getattr(self.instance, "role", None))
        campus_ids = attrs.get("campus_ids", None)
        school = attrs.get("school", getattr(self.instance, "school", None))
        request = self.context.get("request")
        if role == UserRole.SUPER_ADMIN:
            attrs["school"] = None
            attrs["campus_ids"] = None
            return attrs
        if campus_ids is not None and not campus_ids:
            raise serializers.ValidationError({"campus_ids": "Select at least one campus for this user."})
        if campus_ids is None and school is None and self.instance is None:
            raise serializers.ValidationError({"campus_ids": "Select at least one campus for this user."})
        if school and request and getattr(request.user, "role", None) != UserRole.SUPER_ADMIN:
            from apps.core.models import CampusMembership

            allowed = set(CampusMembership.objects.filter(user=request.user).values_list("campus_id", flat=True))
            if school.id not in allowed:
                raise serializers.ValidationError({"school": "Admins can assign users only to their own school."})
        if campus_ids:
            attrs["school_id"] = campus_ids[0]
        return attrs

    def sync_campus_memberships(self, user: User, campus_ids: list[int] | None) -> None:
        if campus_ids is None and user.school_id and not user.campus_memberships.exists():
            campus_ids = [user.school_id]
        if campus_ids is None:
            return
        from apps.core.models import CampusMemberRole, CampusMembership

        CampusMembership.objects.filter(user=user).delete()
        role_map = {
            UserRole.SCHOOL_ADMIN: CampusMemberRole.IT_ADMIN,
            UserRole.ACCOUNT: CampusMemberRole.FINANCE_ADMIN,
            UserRole.TEACHER: CampusMemberRole.TEACHER,
            UserRole.STUDENT: CampusMemberRole.SUPPORT,
        }
        membership_role = role_map.get(user.role, CampusMemberRole.SUPPORT)
        unique_campus_ids = list(dict.fromkeys(campus_ids))[:1]
        if unique_campus_ids:
            user.school_id = unique_campus_ids[0]
            user.save(update_fields=["school", "updated_at"])
        for index, campus_id in enumerate(unique_campus_ids):
            CampusMembership.objects.create(
                user=user,
                campus_id=campus_id,
                role=membership_role,
                is_primary=index == 0,
                can_manage_users=user.role == UserRole.SCHOOL_ADMIN,
                can_configure_attendance=user.role == UserRole.SCHOOL_ADMIN,
            )

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        campus_ids = validated_data.pop("campus_ids", None)
        school_id = validated_data.pop("school_id", None)
        user = User(**validated_data)
        if school_id:
            user.school_id = school_id
        if user.role in (UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN):
            user.is_staff = True
        else:
            user.is_staff = False
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
            user.must_change_password = True
        user.save()
        self.sync_campus_memberships(user, campus_ids)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        campus_ids = validated_data.pop("campus_ids", None)
        school_id = validated_data.pop("school_id", None)
        if instance.is_protected_super_admin:
            blocked = {}
            requested_role = validated_data.get("role", instance.role)
            requested_active = validated_data.get("is_active", instance.is_active)
            if requested_role != UserRole.SUPER_ADMIN:
                blocked["role"] = "Super Admin accounts cannot be demoted."
            if requested_active is False:
                blocked["is_active"] = "Super Admin accounts cannot be disabled."
            if blocked:
                raise serializers.ValidationError(blocked)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if school_id:
            instance.school_id = school_id
        if instance.role in (UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN):
            instance.is_staff = True
        else:
            instance.is_staff = False
        if password:
            instance.set_password(password)
            instance.must_change_password = False
        instance.save()
        self.sync_campus_memberships(instance, campus_ids)
        return instance


class ERPTokenObtainPairSerializer(TokenObtainPairSerializer):
    captcha_id = serializers.CharField(write_only=True, required=True)
    captcha_answer = serializers.CharField(write_only=True, required=True, trim_whitespace=True)

    @classmethod
    def get_token(cls, user: User):
        token = super().get_token(user)
        token["role"] = user.role
        token["username"] = user.username
        token["schoolId"] = user.school_id
        token["schoolCode"] = user.school.code if user.school_id else ""
        return token

    def validate(self, attrs):
        captcha_id = attrs.pop("captcha_id", "")
        captcha_answer = attrs.pop("captcha_answer", "")
        if not validate_captcha_response(captcha_id, captcha_answer):
            raise serializers.ValidationError(
                {"captcha_answer": "Captcha is incorrect or expired. Refresh the captcha and try again."}
            )
        data = super().validate(attrs)
        if self.user.role != UserRole.SUPER_ADMIN:
            campus = self.user.school
            if campus is None:
                from apps.core.models import CampusMembership

                membership = (
                    CampusMembership.objects.filter(user=self.user, is_primary=True)
                    .select_related("campus")
                    .first()
                ) or CampusMembership.objects.filter(user=self.user).select_related("campus").first()
                campus = membership.campus if membership else None
            if campus is None:
                raise serializers.ValidationError({"username": "This account is not assigned to a school."})
            if campus.status != "active":
                raise serializers.ValidationError(
                    {"username": f"{campus.name} is {campus.status}. Contact the Super Admin."}
                )
        data["user"] = UserSerializer(self.user).data
        return data


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.must_change_password = False
        user.save(update_fields=["password", "must_change_password", "updated_at"])
        return user
