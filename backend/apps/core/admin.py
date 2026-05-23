from django.contrib import admin

from .models import (
    AcademicSession,
    AdmitCard,
    Announcement,
    AssignedWork,
    ApprovalRequest,
    AttendanceDevice,
    AttendanceRecord,
    AuditEvent,
    Campus,
    CampusMembership,
    ClassSection,
    FeeAssignment,
    LearningResource,
    Payment,
    ResultRecord,
    StaffAttendanceRecord,
    Student,
    StudentGuardian,
    SupportTicket,
)

admin.site.register(Campus)
admin.site.register(CampusMembership)
admin.site.register(AttendanceDevice)
admin.site.register(AcademicSession)
admin.site.register(ClassSection)
admin.site.register(Student)
admin.site.register(StudentGuardian)
admin.site.register(AttendanceRecord)
admin.site.register(StaffAttendanceRecord)
admin.site.register(AssignedWork)
admin.site.register(LearningResource)
admin.site.register(ResultRecord)
admin.site.register(AdmitCard)
admin.site.register(FeeAssignment)
admin.site.register(Payment)
admin.site.register(ApprovalRequest)
admin.site.register(Announcement)
admin.site.register(SupportTicket)
admin.site.register(AuditEvent)
