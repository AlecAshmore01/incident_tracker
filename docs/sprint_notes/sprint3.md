# Sprint 3 (2025-05-29 → 2025-06-11)

## Goals
- US5: Paginated & filterable incident list  
- US6: Category CRUD (admin only)  
- US7: Incident edit & delete (roles)  

## Tasks
- Integrate Flask-Paginate & build list view  
- Build `categories/create`, `edit`, `delete` routes + templates  
- Implement role checks for incident `edit`/`delete`  

## Completed
- Incident list view with search, filters, pagination → **US5** ✅  
- Category management UI & routes (admin) → **US6** ✅  
- Incident edit/delete with access control → **US7** ✅  

## Blockers
- Needed CSRF token on delete forms (fixed by adding `{{ csrf_token() }}`).

## Retrospective
- Templates across blueprints are consistent; consider consolidating nav bar links dynamically for new features.  
