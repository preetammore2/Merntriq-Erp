# Production Readiness

This ERP is designed as a responsive web application backed by a Django REST API. The codebase includes the application hooks needed for production operation, but 50 lakh+ user support depends on the deployment architecture around it.

## Web App

- The frontend is responsive across mobile, tablet, and desktop screens.
- `web/public/manifest.json` makes the app installable as a standalone browser app.
- Global loading and error boundaries prevent blank screens during route failures.
- The API client enforces request timeouts and returns consistent network, session, and rate-limit errors.
- Idle sessions expire on the client using `NEXT_PUBLIC_SESSION_IDLE_MINUTES`.
- Active sessions are periodically revalidated using `NEXT_PUBLIC_SESSION_VALIDATE_SECONDS`.

## API Traffic Control

DRF throttling is enabled globally and should use Redis in production so limits are shared across all API instances.

Recommended production variables:

```env
DJANGO_CACHE_URL=redis://redis:6379/1
DJANGO_THROTTLE_ANON_RATE=30/minute
DJANGO_THROTTLE_AUTH_RATE=10/minute
DJANGO_THROTTLE_USER_RATE=300/minute
DJANGO_THROTTLE_HARDWARE_CAPTURE_RATE=1200/minute
```

Scale these rates per institution, load balancer policy, and device volume. Keep login throttles conservative.

## Hardware Attendance Contract

Attendance devices are registered in Campus Control. Each active device can post captures to:

```http
POST /api/v1/attendance-devices/{device_id}/capture/
Authorization: Bearer <admin-or-device-token>
Content-Type: application/json
```

Student capture payload:

```json
{
  "person_type": "student",
  "external_id": "ADM-2026-001",
  "captured_at": "2026-05-21T08:15:00+05:30",
  "status": "present",
  "source_reference": "device-event-987654",
  "confidence_score": "98.50"
}
```

Staff capture payload:

```json
{
  "person_type": "staff",
  "external_id": "teacher",
  "captured_at": "2026-05-21T08:12:00+05:30",
  "status": "present",
  "source_reference": "staff-event-123456",
  "confidence_score": "97.20"
}
```

The API validates device campus, supported person type, editable attendance date, and allowed attendance statuses.

## 50 Lakh+ User Deployment Notes

Use a horizontally scaled deployment:

- CDN and edge caching for static Next.js assets.
- Multiple Next.js app instances behind a load balancer.
- Multiple Django API instances behind a load balancer.
- Redis for shared throttling, cache, and future queues.
- PostgreSQL with connection pooling, read replicas, backups, and partitioning for high-volume attendance/audit tables.
- Dedicated ingestion path for hardware traffic if device volume grows beyond standard API traffic.
- Centralized logs, metrics, tracing, uptime checks, and alerting.

The local development environment is not intended to simulate 50 lakh+ production traffic.
