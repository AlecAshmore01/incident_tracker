# DevOps Systems Development Processes

This document describes the DevOps processes, practices, and methodologies used in the development of the Incident Tracker application. It covers the complete software development lifecycle from development to deployment.

## Table of Contents

- [Overview](#overview)
- [Development Workflow](#development-workflow)
- [Version Control Strategy](#version-control-strategy)
- [CI/CD Pipeline](#cicd-pipeline)
- [Testing Strategy](#testing-strategy)
- [Code Quality Assurance](#code-quality-assurance)
- [Database Migration Process](#database-migration-process)
- [Deployment Process](#deployment-process)
- [Monitoring and Logging](#monitoring-and-logging)
- [Security Practices](#security-practices)

---

## Overview

The Incident Tracker application follows a **DevOps approach** that emphasizes:
- **Continuous Integration (CI)**: Automated testing and quality checks on every commit
- **Continuous Deployment (CD)**: Automated deployment to production environments
- **Infrastructure as Code**: Configuration managed through version control
- **Automated Testing**: Comprehensive test suite with high coverage
- **Code Quality**: Automated linting, type checking, and security scanning

---

## Development Workflow

### 1. Branching Strategy

**Main Branches**:
- `main` / `master` - Production-ready code
- `develop` - Integration branch for features

**Feature Branches**:
- `feature/feature-name` - New features
- `bugfix/bug-name` - Bug fixes
- `hotfix/issue-name` - Critical production fixes

**Workflow**:
```
1. Create feature branch from develop
2. Develop and commit changes
3. Push to remote repository
4. Create Pull Request (PR)
5. CI/CD pipeline runs automatically
6. Code review and approval
7. Merge to develop/main
8. Automatic deployment (if configured)
```

### 2. Commit Strategy

**Commit Message Format**:
```
type(scope): brief description

Detailed explanation if needed
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

**Examples**:
```
feat(auth): add two-factor authentication
fix(incidents): resolve SQL injection vulnerability
docs(readme): update installation instructions
```

### 3. Pull Request Process

**PR Requirements**:
1. All CI/CD checks must pass
2. Code review approval required
3. Tests must pass with coverage maintained
4. Documentation updated if needed
5. No merge conflicts

**PR Template**:
- Description of changes
- Related issues
- Testing performed
- Screenshots (if UI changes)

---

## Version Control Strategy

### Git Workflow

**Repository Structure**:
```
incident_tracker/
├── .github/
│   └── workflows/
│       └── ci.yml          # CI/CD pipeline
├── app/                    # Application code
├── tests/                  # Test suite
├── migrations/             # Database migrations
├── docs/                   # Documentation
└── requirements.txt         # Dependencies
```

### Git Configuration

**.gitignore**:
- Python cache files (`__pycache__/`, `*.pyc`)
- Virtual environment (`venv/`, `env/`)
- IDE files (`.vscode/`, `.idea/`)
- Environment variables (`.env`)
- Database files (`*.db`, `*.sqlite`)
- Log files (`logs/`)
- Coverage reports (`htmlcov/`, `.coverage`)

### Version Tagging

**Semantic Versioning**:
- `v1.0.0` - Major release
- `v1.1.0` - Minor release (new features)
- `v1.1.1` - Patch release (bug fixes)

**Tagging Process**:
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

---

## CI/CD Pipeline

### Pipeline Overview

The CI/CD pipeline is defined in `.github/workflows/ci.yml` and runs automatically on:
- Push to `main`, `develop`, or `master` branches
- Pull requests to these branches

### Pipeline Stages

#### 1. Test Stage

**Purpose**: Run automated tests across multiple Python versions

**Configuration**:
```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12', '3.13']
```

**Steps**:
1. Checkout code
2. Set up Python environment
3. Install dependencies
4. Run tests with coverage
5. Upload coverage reports

**Tools**:
- `pytest` - Test framework
- `pytest-cov` - Coverage reporting
- `pytest-html` - HTML coverage reports

**Coverage Target**: 85%+

#### 2. Type Checking Stage

**Purpose**: Static type analysis using mypy

**Steps**:
1. Checkout code
2. Set up Python
3. Install dependencies
4. Run mypy type checking

**Configuration**: `mypy.ini`
```ini
[mypy]
python_version = 3.13
warn_return_any = True
warn_unused_configs = True
```

#### 3. Linting Stage

**Purpose**: Code style and quality checks

**Steps**:
1. Checkout code
2. Set up Python
3. Install dependencies
4. Run flake8 linting

**Rules**:
- Maximum line length: 127 characters
- Maximum complexity: 10
- Error codes: E9, F63, F7, F82 (critical errors)

#### 4. Security Testing Stage

**Purpose**: Automated security vulnerability testing

**Tests**:
- XSS (Cross-Site Scripting) prevention
- SQL Injection prevention
- CSRF protection
- Input sanitization

**Location**: `tests/test_basic.py`
```python
def test_xss_sanitization_on_incident_description(...)
def test_sql_injection_in_category_name(...)
def test_csrf_protection(...)
```

#### 5. Build Verification Stage

**Purpose**: Verify application builds successfully

**Steps**:
1. Checkout code
2. Set up Python
3. Install dependencies
4. Verify build: `python -c "from app import create_app; app = create_app('dev')"`
5. Check database migrations

**Dependencies**: All previous stages must pass

### Pipeline Artifacts

**Coverage Reports**:
- HTML reports uploaded as artifacts
- Available for 30 days
- Optional Codecov integration

**Build Logs**:
- Available in GitHub Actions
- Retained for debugging

### Pipeline Failure Handling

**On Failure**:
1. Notification sent (if configured)
2. PR marked as failed
3. Detailed error logs available
4. Developer fixes and re-pushes

---

## Testing Strategy

### Test Types

#### 1. Unit Tests

**Purpose**: Test individual components in isolation

**Examples**:
- Model validation
- Service layer logic
- Utility functions

**Location**: `tests/test_basic.py`

**Example**:
```python
def test_user_model(app):
    with app.app_context():
        user = User(username="testuser", email="test@example.com")
        db.session.add(user)
        db.session.commit()
        assert User.query.filter_by(username="testuser").first() is not None
```

#### 2. Integration Tests

**Purpose**: Test component interactions

**Examples**:
- Route handlers with database
- Form submission flows
- Authentication workflows

**Example**:
```python
def test_create_incident_flow(client, app):
    login_user(client, "testuser")
    response = client.post('/incidents/create', data={
        'title': 'Test Incident',
        'description': 'Long enough description',
        'status': 'Open',
        'category': 1
    })
    assert response.status_code == 302  # Redirect on success
```

#### 3. Security Tests

**Purpose**: Verify security measures

**Tests**:
- XSS prevention
- SQL injection protection
- CSRF token validation
- Authentication bypass attempts

**Example**:
```python
def test_xss_sanitization_on_incident_description(client, app):
    xss_payload = "<script>alert('xss')</script>"
    # Submit form with XSS payload
    # Verify it's sanitized in database
```

### Test Organization

**Structure**:
```
tests/
└── test_basic.py          # All test cases
```

**Test Fixtures**:
```python
@pytest.fixture
def app():
    # Create test application
    app = create_app('dev')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app

@pytest.fixture
def client(app):
    return app.test_client()
```

### Test Coverage

**Target**: 85%+ code coverage

**Measurement**:
```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

**Coverage Reports**:
- Terminal output (missing lines)
- HTML report (`htmlcov/index.html`)
- XML report (for CI/CD)

### Test Execution

**Local Execution**:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test
pytest tests/test_basic.py::test_user_model

# Run with verbose output
pytest -v
```

**CI/CD Execution**:
- Automatic on every push/PR
- Runs on multiple Python versions
- Fails build if tests fail

---

## Code Quality Assurance

### 1. Type Checking (mypy)

**Purpose**: Static type analysis to catch type errors

**Configuration**: `mypy.ini`
```ini
[mypy]
python_version = 3.13
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False
```

**Execution**:
```bash
mypy app
```

**Benefits**:
- Catch type errors before runtime
- Improve code documentation
- Better IDE support

### 2. Linting (flake8)

**Purpose**: Enforce code style and catch errors

**Rules**:
- PEP 8 style guide compliance
- Maximum line length: 127
- Maximum complexity: 10
- Critical error detection

**Execution**:
```bash
flake8 app tests --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 app tests --count --exit-zero --max-complexity=10 --max-line-length=127
```

### 3. Code Formatting

**Tools** (optional):
- `black` - Automatic code formatting
- `isort` - Import sorting

### 4. Documentation

**Requirements**:
- Docstrings for all functions/classes
- README with setup instructions
- Architecture documentation
- API documentation (if applicable)

---

## Database Migration Process

### Migration Tool: Flask-Migrate (Alembic)

**Purpose**: Version control for database schema

### Migration Workflow

#### 1. Create Migration

```bash
flask db migrate -m "Description of changes"
```

**Creates**: `migrations/versions/XXXXXX_description.py`

#### 2. Review Migration

**Check generated SQL**:
```python
def upgrade():
    # Upgrade operations
    op.add_column('incidents', sa.Column('closed_at', sa.DateTime(), nullable=True))

def downgrade():
    # Downgrade operations
    op.drop_column('incidents', 'closed_at')
```

#### 3. Apply Migration

**Development**:
```bash
flask db upgrade
```

**Production**:
- Automatic on deployment (via CI/CD)
- Manual: `flask db upgrade` in production environment

### Migration Best Practices

1. **Always review** generated migrations
2. **Test migrations** on development database first
3. **Backup database** before production migrations
4. **Test downgrade** path (downgrade/upgrade)
5. **Document breaking changes**

### Migration Files

**Location**: `migrations/versions/`

**Examples**:
- `0c547c870a1b_initial_schema.py` - Initial database schema
- `7b9a350afb10_create_audit_logs_table.py` - Add audit logs
- `99342c40e3b4_add_otp_secret_to_user.py` - Add 2FA support

### Migration Check on Startup

**Automatic Verification**:
```python
# app/__init__.py
if not app.debug:
    with app.app_context():
        ensure_db_is_up_to_date(db.engine, migrations_path)
```

**Purpose**: Ensure production database is up-to-date

---

## Deployment Process

### Deployment Environments

#### 1. Development

**Location**: Local machine
**Database**: SQLite (`app.db`)
**Configuration**: `DevConfig`

**Setup**:
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
flask db upgrade
python seed.py
python run.py
```

#### 2. Production

**Platform**: Render.com
**Database**: PostgreSQL
**Configuration**: `ProdConfig`

### Deployment Steps

#### 1. Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Database migrations tested
- [ ] Environment variables configured
- [ ] Dependencies updated in `requirements.txt`

#### 2. Deployment Configuration

**Platform**: Render.com

**Configuration File**: `render.yaml`
```yaml
services:
  - type: web
    name: incident-tracker
    env: python
    buildCommand: pip install -r requirements.txt && flask db upgrade
    startCommand: gunicorn wsgi:app
    envVars:
      - key: FLASK_ENV
        value: production
```

#### 3. Environment Variables

**Required**:
- `SECRET_KEY` - Flask secret key
- `DATABASE_URL` - PostgreSQL connection string
- `FLASK_ENV` - Environment (production)

**Optional**:
- `MAIL_SERVER` - SMTP server
- `MAIL_PORT` - SMTP port
- `MAIL_USERNAME` - Email username
- `MAIL_PASSWORD` - Email password

#### 4. Deployment Process

**Automatic** (on push to main):
1. Render detects code changes
2. Runs build command
3. Applies database migrations
4. Starts application
5. Health check verification

**Manual**:
1. Push code to repository
2. Trigger deployment in Render dashboard
3. Monitor build logs
4. Verify deployment

#### 5. Post-Deployment

**Verification**:
- [ ] Application accessible
- [ ] Database migrations applied
- [ ] Authentication working
- [ ] CRUD operations functional
- [ ] Error handling working

**Rollback** (if needed):
1. Revert to previous deployment in Render
2. Or: `git revert` and redeploy

### Deployment Documentation

**Location**: `DEPLOYMENT.md`

**Contents**:
- Step-by-step deployment guide
- Environment variable configuration
- Troubleshooting common issues
- Security considerations

---

## Monitoring and Logging

### Logging Strategy

#### 1. Log Levels

- **INFO**: General application events
- **WARNING**: Potential issues
- **ERROR**: Error conditions
- **CRITICAL**: Critical failures

#### 2. Log Configuration

**Location**: `app/__init__.py`

**Features**:
- File-based logging
- Log rotation (daily)
- Separate error log
- Structured format

**Configuration**:
```python
def setup_logging(app: Flask) -> None:
    if not app.debug:
        # File handler with rotation
        file_handler = TimedRotatingFileHandler(
            'logs/app.log',
            when='midnight',
            interval=1,
            backupCount=7
        )
        # Error handler
        error_handler = TimedRotatingFileHandler(
            'logs/errors.log',
            when='midnight',
            interval=1,
            backupCount=30
        )
```

#### 3. Log Locations

- **Application Log**: `app/logs/app.log`
- **Error Log**: `app/logs/errors.log`
- **Retention**: 7 days (app), 30 days (errors)

#### 4. Logging Usage

**Example**:
```python
from flask import current_app

current_app.logger.info('User logged in')
current_app.logger.error('Database connection failed', exc_info=True)
```

### Monitoring

**Production Monitoring**:
- Render dashboard (uptime, logs)
- Application logs
- Error tracking (via logs)

**Metrics to Monitor**:
- Application uptime
- Error rates
- Response times
- Database connection status

---

## Security Practices

### 1. Secret Management

**Never commit**:
- Passwords
- API keys
- Database URLs
- Secret keys

**Use environment variables**:
```python
SECRET_KEY = os.environ.get('SECRET_KEY')
DATABASE_URL = os.environ.get('DATABASE_URL')
```

### 2. Dependency Management

**Regular Updates**:
- Review `requirements.txt`
- Update dependencies regularly
- Check for security vulnerabilities

**Tools**:
- `pip list --outdated`
- `safety check` (security scanning)

### 3. Security Scanning

**In CI/CD Pipeline**:
- Automated security tests
- XSS/SQL injection tests
- CSRF protection verification

### 4. Code Review

**Security Focus**:
- Input validation
- Authentication/authorization
- SQL injection prevention
- XSS prevention

---

## Summary

The DevOps processes implemented in this application include:

1. **Version Control**: Git with feature branch workflow
2. **CI/CD**: Automated testing, linting, type checking, security testing
3. **Testing**: Unit, integration, and security tests with 85%+ coverage
4. **Code Quality**: Type checking, linting, documentation
5. **Database Migrations**: Version-controlled schema changes
6. **Deployment**: Automated deployment to production
7. **Monitoring**: Structured logging and error tracking
8. **Security**: Automated security testing and best practices

These processes ensure:
- **Quality**: High code quality through automated checks
- **Reliability**: Comprehensive testing prevents bugs
- **Security**: Automated security testing and best practices
- **Maintainability**: Clear processes and documentation
- **Speed**: Automated processes reduce manual work

