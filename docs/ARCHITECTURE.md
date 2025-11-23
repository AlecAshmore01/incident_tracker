# Application Architecture

This document describes the architecture, design patterns, and implementation decisions for the Incident Tracker application.

## Table of Contents

- [Overview](#overview)
- [Architecture Patterns](#architecture-patterns)
- [Code Organization](#code-organization)
- [Design Patterns](#design-patterns)
- [Error Handling Strategy](#error-handling-strategy)
- [Validation Approach](#validation-approach)
- [Database Design](#database-design)
- [Security Considerations](#security-considerations)

## Overview

The Incident Tracker is a Flask-based web application following a **layered architecture** pattern with clear separation of concerns:

- **Presentation Layer**: Routes and templates
- **Service Layer**: Business logic
- **Data Layer**: Models and database access
- **Utility Layer**: Shared utilities and helpers

## Architecture Patterns

### 1. Application Factory Pattern

The application uses Flask's application factory pattern (`create_app()`) for:
- Flexible configuration management
- Easy testing with different configurations
- Multiple application instances

**Location**: `app/__init__.py`

### 2. Blueprint Pattern

The application is organized into blueprints for modular routing:
- `main_bp`: Public pages and dashboard
- `auth_bp`: Authentication and user management
- `incident_bp`: Incident management
- `category_bp`: Category management

**Benefits**:
- Clear separation of concerns
- Easy to maintain and extend
- Reusable components

### 3. Service Layer Pattern

Business logic is encapsulated in service classes, separating it from route handlers:

- `IncidentService`: All incident-related business logic
- `CategoryService`: All category-related business logic

**Benefits**:
- **Modularity**: Business logic is isolated and reusable
- **Testability**: Services can be tested independently
- **Maintainability**: Changes to business logic don't affect routes
- **No Duplication**: Shared logic is centralized

**Example**:
```python
# Route handler (thin)
@incident_bp.route('/create', methods=['GET', 'POST'])
def create_incident():
    if form.validate_on_submit():
        incident = IncidentService.create_incident(...)
        # Handle response

# Service (business logic)
class IncidentService:
    @staticmethod
    def create_incident(...):
        # Validation, business rules, database operations
```

## Code Organization

```
app/
├── __init__.py          # Application factory
├── config.py            # Configuration classes
├── extensions.py        # Flask extensions initialization
├── auth/                # Authentication blueprint
│   ├── routes.py        # Auth routes
│   └── forms.py         # Auth forms
├── incidents/           # Incidents blueprint
│   ├── routes.py        # Incident routes (thin controllers)
│   └── forms.py        # Incident forms
├── categories/          # Categories blueprint
│   ├── routes.py        # Category routes (thin controllers)
│   └── forms.py        # Category forms
├── main/                # Main blueprint
│   └── routes.py        # Dashboard and public routes
├── models/              # Data models
│   ├── user.py         # User model with validation
│   ├── incident.py     # Incident model with validation
│   ├── category.py     # Category model with validation
│   └── audit.py        # Audit log model
├── services/            # Service layer (business logic)
│   ├── incident_service.py
│   └── category_service.py
└── utils/               # Utility modules
    ├── error_handler.py # Centralized error handling
    ├── audit.py         # Centralized audit logging
    ├── validators.py    # Custom form validators
    └── sanitizer.py     # HTML sanitization
```

## Design Patterns

### 1. Repository Pattern (via SQLAlchemy)

Models act as repositories, providing a clean interface to database operations:
- `User.query.filter_by(...)`
- `Incident.query.get_or_404(...)`

### 2. Decorator Pattern

Used extensively for:
- **Authentication**: `@login_required`
- **Error Handling**: `@handle_db_errors`
- **Rate Limiting**: `@limiter.limit()`

### 3. Factory Pattern

- Application factory: `create_app()`
- Extension initialization: `init_extensions()`

### 4. Strategy Pattern

- Different validation strategies (form, model, custom validators)
- Different error handling strategies based on error type

## Error Handling Strategy

### Centralized Error Logging

All errors are logged through a centralized system:

**Location**: `app/utils/error_handler.py`

**Features**:
- Custom exception classes (`ValidationError`, `DatabaseError`, `NotFoundError`)
- Structured logging with context
- Automatic error logging with stack traces
- User-friendly error messages

**Usage**:
```python
from app.utils.error_handler import log_error, ValidationError

try:
    # Operation
except Exception as e:
    log_error(e, "Context information")
    flash('User-friendly message', 'danger')
```

### Error Handling Decorators

- `@handle_db_errors`: Automatically handles database errors with rollback
- `@handle_validation_errors`: Handles validation errors gracefully

### Error Flow

1. **Exception occurs** in service or route
2. **Caught by handler** or decorator
3. **Logged** with context via `log_error()`
4. **User notified** with flash message
5. **Transaction rolled back** if database error
6. **User redirected** to safe page

## Validation Approach

### Three-Layer Validation

1. **Form Validation** (Client-side + Server-side)
   - WTForms validators
   - Custom validators (`StrongPassword`, `NoHTML`, `SafeText`)
   - Location: `app/*/forms.py`

2. **Model Validation** (Data Integrity)
   - SQLAlchemy `@validates` decorator
   - Business rule enforcement
   - Location: `app/models/*.py`

3. **Service Validation** (Business Logic)
   - Additional business rules
   - Cross-model validation
   - Location: `app/services/*.py`

### Custom Validators

**Location**: `app/utils/validators.py`

- `StrongPassword`: Password strength validation
- `NoHTML`: Prevents HTML in text fields
- `SafeText`: Checks for dangerous content

**Benefits**:
- Reusable across forms
- Consistent validation logic
- Easy to maintain

## Database Design

### Models

All models include:
- Type hints for better IDE support
- Model-level validation
- Proper indexes for performance
- Relationships with appropriate lazy loading

### Indexes

Performance indexes on frequently queried columns:
- `incidents.user_id`
- `incidents.category_id`
- `incidents.status`
- `incidents.timestamp`
- `users.username`
- `users.email`
- `audit_logs.user_id`
- `audit_logs.timestamp`

**Migration**: `migrations/versions/add_performance_indexes.py`

### Query Optimization

- **Eager Loading**: `joinedload()` to prevent N+1 queries
- **Pagination**: Efficient pagination for large datasets
- **Indexed Queries**: All foreign keys and frequently filtered columns are indexed

## Security Considerations

### Input Sanitization

- **HTML Sanitization**: All user input is sanitized using `bleach`
- **XSS Prevention**: Content Security Policy (CSP) headers
- **SQL Injection**: Prevented by SQLAlchemy ORM

### Authentication & Authorization

- **Password Hashing**: Bcrypt with salt
- **2FA**: TOTP-based two-factor authentication
- **Account Lockout**: After failed login attempts
- **Session Security**: Secure, HTTP-only cookies

### Audit Logging

All critical actions are logged:
- Create, update, delete operations
- User authentication events
- Centralized via `app/utils/audit.py`

### CSRF Protection

- Flask-WTF CSRF protection on all forms
- Token validation on POST requests

## Data Flow

### Creating an Incident

1. **User submits form** → Route handler
2. **Form validation** → WTForms validators
3. **Route calls service** → `IncidentService.create_incident()`
4. **Service validates** → Business rules, model validation
5. **Service creates model** → Database operation
6. **Service creates audit log** → Centralized audit utility
7. **Service returns result** → Route handler
8. **Route sends notification** → Email to admins
9. **Route redirects** → User feedback

### Error Handling Flow

1. **Exception occurs** → Service or route
2. **Caught by handler** → Try/except or decorator
3. **Logged** → `log_error()` with context
4. **User notified** → Flash message
5. **Transaction rolled back** → If database error
6. **Safe redirect** → User-friendly page

## Testing Strategy

### Test Organization

- **Unit Tests**: Services, utilities, models
- **Integration Tests**: Routes with test client
- **Security Tests**: XSS, SQL injection, CSRF

### Test Coverage

- Target: 85%+ code coverage
- Tools: `pytest`, `pytest-cov`
- CI/CD: Automated testing on every commit

## Performance Considerations

### Database

- Indexes on frequently queried columns
- Eager loading to prevent N+1 queries
- Pagination for large result sets

### Caching (Future)

- Session caching with Redis
- Query result caching
- Static asset caching

## Deployment

### Configuration

- Environment-based configuration (`DevConfig`, `ProdConfig`)
- Environment variables for secrets
- Database URL handling (SQLite/PostgreSQL)

### Logging

- Structured logging to files
- Log rotation (daily, 7-day retention)
- Separate error log (30-day retention)
- Production logging configured in `app/__init__.py`

## Future Enhancements

1. **API Layer**: RESTful API with Flask-RESTful
2. **Caching**: Redis integration for sessions and queries
3. **Background Tasks**: Celery for async operations
4. **Monitoring**: Application performance monitoring
5. **Documentation**: API documentation with Swagger

## Conclusion

This architecture provides:
- ✅ **Modularity**: Clear separation of concerns
- ✅ **Maintainability**: Easy to understand and modify
- ✅ **Testability**: Services and utilities are easily testable
- ✅ **Scalability**: Can grow with additional features
- ✅ **Security**: Multiple layers of protection
- ✅ **Performance**: Optimized queries and indexes

