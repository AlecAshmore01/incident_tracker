# Incident Tracker – User Stories Backlog

Each story is estimated in story points (Fibonacci scale) and prioritized by business value.

## Current Sprint Stories

| ID  | Story                                                                                 | Points | Priority | Status   |
|-----|---------------------------------------------------------------------------------------|:------:|:--------:|:--------:|
| US1 | As a **regular user**, I want to register an account so that I can submit incidents.  |   3    | High     | Done     |
| US2 | As a **regular user**, I want to log in/out and stay "remembered" across sessions.   |   2    | High     | Done     |
| US3 | As a **regular user**, I want to reset my password via email so I never get locked out. |   5    | High     | Done     |
| US4 | As a **regular user**, I want to submit a new incident with title & description.     |   3    | High     | Done     |
| US5 | As a **regular user**, I want to view a paginated list of my incidents.              |   2    | Medium   | Done     |
| US6 | As an **admin**, I want to create/edit/delete categories so that incidents are classified. |   3    | Medium   | Done     |
| US7 | As an **admin**, I want to view/edit/delete any incident to manage tickets.           |   5    | High     | Done     |
| US8 | As any user, I want all forms protected by CSRF so that my data stays secure.        |   1    | High     | Done     |
| US9 | As any user, I want optional TOTP 2FA so I can harden my account.                    |   8    | Low      | Done     |
| US10| As an **admin**, I want an audit trail of all create/update/delete actions.           |   5    | Medium   | Done     |
| US11| As any user, I want email notifications on registration and ticket updates.          |   3    | Low      | Done     |
| US12| As an **admin**, I want a dashboard with analytics on incident counts over time.      |   8    | Low      | Done     |

## Future Backlog Stories

| ID  | Story                                                                                 | Points | Priority | Status   |
|-----|---------------------------------------------------------------------------------------|:------:|:--------:|:--------:|
| US13| As a **user**, I want to attach files to incidents so I can provide screenshots.     |   5    | Medium   | Backlog  |
| US14| As a **user**, I want to comment on incidents so I can track progress updates.       |   3    | Medium   | Backlog  |
| US15| As an **admin**, I want to assign incidents to specific users for workload distribution. |   5    | High     | Backlog  |
| US16| As a **user**, I want to search/filter incidents by keywords and criteria.           |   8    | Medium   | Backlog  |
| US17| As a **user**, I want email notifications when incidents assigned to me are updated. |   3    | Low      | Backlog  |
| US18| As an **admin**, I want to export incident reports as PDF/CSV for external reporting. |   5    | Low      | Backlog  |

---

## Detailed Stories with Acceptance Criteria

### US1: User Registration
**As a regular user, I want to register an account so that I can submit incidents.**

**Acceptance Criteria:**
- [x] Registration form requires username, email, password
- [x] Password must meet security requirements (8+ chars, mixed case, numbers)
- [x] Email validation prevents duplicate registrations
- [x] Welcome email sent upon successful registration
- [x] User redirected to login page after registration
- [x] Form shows clear error messages for validation failures

### US2: Login/Logout & Session Management
**As a regular user, I want to log in/out and stay "remembered" across sessions.**

**Acceptance Criteria:**
- [x] Login form with username/email and password
- [x] "Remember me" checkbox for persistent sessions
- [x] Secure logout that clears all session data
- [x] Session timeout after inactivity
- [x] Account lockout after failed login attempts
- [x] Redirect to intended page after login

### US3: Password Reset
**As a regular user, I want to reset my password via email so I never get locked out.**

**Acceptance Criteria:**
- [x] Password reset request form with email field
- [x] Secure reset token sent via email
- [x] Reset token expires after 1 hour
- [x] New password form with confirmation field
- [x] Password strength validation on reset
- [x] Success message and redirect to login

### US4: Submit New Incident
**As a regular user, I want to submit a new incident with title & description.**

**Acceptance Criteria:**
- [x] Form has required fields: title, description, category
- [x] Title limited to 100 characters
- [x] Description supports multi-line text input
- [x] User can select from existing categories
- [x] Incident gets auto-assigned to submitting user
- [x] Status defaults to "Open"
- [x] Timestamp recorded automatically
- [x] Success message shown after submission

### US5: View Incident List
**As a regular user, I want to view a paginated list of my incidents.**

**Acceptance Criteria:**
- [x] Paginated list showing user's incidents
- [x] Display title, status, category, and date
- [x] Sort by date (newest first)
- [x] Filter by status (Open, In Progress, Closed)
- [x] Search by title/description keywords
- [x] Items per page configurable (10, 25, 50)
- [x] Clear "No incidents found" message

### US6: Category Management (Admin)
**As an admin, I want to create/edit/delete categories so that incidents are classified.**

**Acceptance Criteria:**
- [x] Admin-only access to category management
- [x] Create new categories with name and description
- [x] Edit existing category details
- [x] Delete categories (with incident reassignment)
- [x] Category list with search functionality
- [x] Validation prevents duplicate category names
- [x] Audit trail for category changes

### US7: Incident Management (Admin)
**As an admin, I want to view/edit/delete any incident to manage tickets.**

**Acceptance Criteria:**
- [x] Admin can view all incidents regardless of owner
- [x] Edit incident title, description, status, category
- [x] Change incident assignment to other users
- [x] Delete incidents with confirmation dialog
- [x] Bulk operations for multiple incidents
- [x] Status change triggers email notifications
- [x] Access restricted to admin role only

### US8: CSRF Protection
**As any user, I want all forms protected by CSRF so that my data stays secure.**

**Acceptance Criteria:**
- [x] All POST/PUT/DELETE forms include CSRF tokens
- [x] Invalid CSRF tokens return 403 error
- [x] CSRF tokens refresh on each page load
- [x] AJAX requests include CSRF headers
- [x] Clear error messages for CSRF failures
- [x] No functional impact on user experience

### US9: Two-Factor Authentication
**As any user, I want optional TOTP 2FA so I can harden my account.**

**Acceptance Criteria:**
- [x] 2FA setup page with QR code generation
- [x] Support for standard authenticator apps (Google Auth, Authy)
- [x] Backup codes generated during setup
- [x] 2FA verification during login process
- [x] Ability to disable 2FA with password confirmation
- [x] Recovery process using backup codes
- [x] Clear setup instructions and troubleshooting

### US10: Audit Trail
**As an admin, I want an audit trail of all create/update/delete actions.**

**Acceptance Criteria:**
- [x] Log all CRUD operations with user, timestamp, action
- [x] Track changes to incidents, categories, and users
- [x] Admin-only access to audit log viewer
- [x] Searchable and filterable audit entries
- [x] Export audit logs for compliance
- [x] Retain audit data for minimum 90 days
- [x] No performance impact on normal operations

### US11: Email Notifications
**As any user, I want email notifications on registration and ticket updates.**

**Acceptance Criteria:**
- [x] Welcome email sent on successful registration
- [x] Password reset emails with secure tokens
- [x] Incident status change notifications
- [x] Professional email templates with branding
- [x] Unsubscribe option for non-critical emails
- [x] Email delivery error handling
- [x] SMTP configuration for multiple providers

### US12: Admin Dashboard Analytics
**As an admin, I want a dashboard with analytics on incident counts over time.**

**Acceptance Criteria:**
- [x] Chart showing incidents created per day/week/month
- [x] Pie chart of incidents by status distribution
- [x] Bar chart of incidents by category
- [x] Summary cards showing key metrics
- [x] Date range filter for analytics
- [x] Mobile-responsive charts
- [x] Export functionality for reports
- [x] Real-time data updates

---

## Story Point Reference

| Points | Complexity | Examples |
|--------|------------|----------|
| 1 | Trivial | Add validation message, fix typo |
| 2 | Simple | Basic CRUD form, simple page |
| 3 | Medium | Authentication flow, form with validation |
| 5 | Complex | Email integration, file uploads |
| 8 | Very Complex | Analytics dashboard, 2FA implementation |
| 13+ | Epic | Should be broken down into smaller stories |