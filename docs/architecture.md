# Mentriq360 Production Architecture

## System Overview

```text
Next.js responsive web app
  -> Django REST API
  -> PostgreSQL or SQLite
  -> Redis for cache and async expansion
```

The backend owns business rules, role checks, and relational integrity. The frontend owns the device-responsive user experience for admins, teachers, and parents.

## Role Model

- `super_admin`: full platform control
- `admin`: campus setup, users, students, fees, payments, reports
- `teacher`: assigned section attendance and student reads
- `parent`: linked student profile, attendance, fees, and payments

## Core Data Flow

```text
User logs in
  -> role returned in JWT response
  -> app shell selects workspace
  -> admin creates campus/session/section/student
  -> teacher marks attendance
  -> admin assigns fee and records payment
  -> reports update from source tables
  -> parent sees scoped student data
```

## Backend Modules

- `apps.accounts`: custom user model, role enum, JWT serializer, current user, admin user API
- `apps.core`: academic setup, students, guardians, attendance, fees, payments, reports, audit events
- `config.settings`: split local and production settings

## Frontend Modules

- `AppShell`: login gate and role-aware navigation
- `AdminDashboard`: campuses, sessions, sections, users, students, parent links
- `AttendancePanel`: teacher attendance entry
- `FeesPaymentsDashboard`: fee assignment and payment collection
- `ParentDashboard`: parent read-only view
- `ReportsDashboard`: analytics and audit trail
- `ERPWorkspace`: blueprint view at `/blueprint`

## Database Entities

- `User`
- `Campus`
- `AcademicSession`
- `ClassSection`
- `Student`
- `StudentGuardian`
- `AttendanceRecord`
- `FeeAssignment`
- `Payment`
- `AuditEvent`

## Security Boundaries

- JWT authentication is required by default.
- API querysets are role-scoped.
- Teachers cannot mark attendance outside assigned sections.
- Parents cannot read unlinked student data.
- Audit endpoints are admin-only.
- Production settings enable secure cookies, HSTS, HTTPS redirect, and CORS allowlists.

## Deployment Shape

The repository includes Dockerfiles and `docker-compose.yml` for:

- PostgreSQL
- Redis
- Django API
- Next.js web app

For production, run the web app behind HTTPS and run the Django API with `config.settings.production`.
