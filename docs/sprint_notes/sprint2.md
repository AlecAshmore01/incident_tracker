# Sprint 2 (2025-05-15 → 2025-05-28)

## Goals
- US3: Password reset via email  
- US4: Incident creation form  
- US11: Welcome email on registration  

## Tasks
- Configure Flask-Mail & SMTP  
- Build `auth/reset_password_request` and `auth/reset_password`  
- Create `Incident` model and `incidents/create` route  
- Seed test accounts and incident data  

## Completed
- Password reset email flow working end-to-end → **US3** ✅  
- Incident creation (title, description, category) → **US4** ✅  
- Automated welcome emails on register → **US11** ✅  

## Blockers
- SMTP sometimes blocked by local firewall (fixed via app-specific password).  

## Retrospective
- Good coverage with unit tests for reset flow; next sprint add incident listing and filters.  
