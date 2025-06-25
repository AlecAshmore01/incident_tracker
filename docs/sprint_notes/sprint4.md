# Sprint 4 (2025-06-12 → 2025-06-25)

## Goals
- US9: TOTP-based 2FA optional setup & verify  
- US10: AuditLog model + display for admins  
- US12: Admin dashboard analytics  

## Tasks
- Add `pyotp` and 2FA setup/verify pages  
- Create `AuditLog` table and log CRUD actions  
- Expose `/dashboard/data` JSON API and build Chart.js frontend  

## Completed
- 2FA setup and verification flows → **US9** ✅  
- Audit trail recorded on create/update/delete → **US10** ✅  
- Analytics page showing incident trends (via Chart.js) → **US12** ✅  

## Blockers
- Chart.js bundle needed to be moved to `static/js/dashboard.js` for CSP compliance.

## Retrospective
- Strong finish; next would be API rate limiting, file attachments, and deployment scripts.  
