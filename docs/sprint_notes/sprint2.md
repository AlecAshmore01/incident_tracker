# Sprint 2 (2025-05-15 → 2025-05-28)

## Sprint Goals
**Theme**: Core Functionality & Communication
- Enable password recovery via email
- Implement incident creation workflow
- Establish email notification system

## Stories Planned (11 Story Points)
- **US3**: Password reset via email (5 pts)
- **US4**: Incident creation form (3 pts)  
- **US11**: Welcome email on registration (3 pts)

## Technical Tasks
- [x] Configure Flask-Mail with SMTP settings
- [x] Create `Incident` model with relationships
- [x] Build password reset request and confirmation flows
- [x] Design email templates (welcome, password reset)
- [x] Implement incident creation form and validation
- [x] Add database seeding script for test data
- [x] Create incident categories seed data
- [x] Set up email template inheritance structure
- [x] Add email delivery error handling

## Completed User Stories
- **US3** ✅ Password reset email flow working end-to-end
  - Secure token generation with 1-hour expiration
  - Password reset request form with email validation
  - Password confirmation with strength requirements
  - Clear success/error messaging throughout flow
- **US4** ✅ Incident creation (title, description, category)
  - Form validation for required fields
  - Category dropdown populated from database
  - Auto-assignment to current user
  - Default status set to "Open"
  - Success redirect to incident list
- **US11** ✅ Automated welcome emails on registration
  - Professional HTML email template
  - Personalized welcome message with username
  - Clear next steps for new users

## Sprint Metrics
- **Velocity**: 11/11 story points completed
- **Burndown**: Steady progress, finished on schedule
- **Code Coverage**: 82% (↑4% from Sprint 1)
- **Bugs Found**: 2 (email encoding issue, category validation - both fixed)
- **Email Delivery Rate**: 98% (2% failed due to invalid addresses)

## Blockers Encountered
- **SMTP Configuration**: Initially blocked by local firewall
  - **Resolution**: Switched to Gmail app-specific password
  - **Impact**: 1 day delay, resolved by Sprint day 3

## What Went Well
- Email system integration smoother than expected
- Incident model design accommodated future requirements well
- Good collaboration on email template design
- Database migrations handled cleanly

## What Could Be Improved
- Email template could be more mobile-responsive
- Incident form needs better UX feedback during submission
- Category management needed sooner than planned (moved to Sprint 3)

## Technical Debt Identified
- Email configuration should be more environment-aware
- Incident validation logic could be extracted to service layer
- Need better error handling for email delivery failures

## Database Changes
- Added `incidents` table with foreign keys to users/categories
- Added default categories via seed script
- Updated user model to track email preferences

## Testing Notes
- Added integration tests for email sending
- Mocked SMTP for automated test runs
- Manual testing performed with real email providers

## Next Sprint Preparation
- Category CRUD operations prioritized for Sprint 3
- Incident listing and filtering ready for implementation
- Admin role permissions need to be defined

## Retrospective Actions
- ✅ Create email template style guide for consistency
- ✅ Add email delivery monitoring to backlog
- ✅ Plan category management UI wireframes for Sprint 3
- ⏳ Research mobile email template best practices