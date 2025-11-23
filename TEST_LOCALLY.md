# Testing Locally - Step by Step Guide

Follow these steps to test the application locally before pushing to Git.

## Step 1: Activate Virtual Environment

```powershell
# Navigate to project directory (if not already there)
cd "C:\Users\Alec Ashmore\incident_tracker"

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

You should see `(venv)` in your prompt.

## Step 2: Install/Update Dependencies

```powershell
# Make sure all dependencies are installed
pip install -r requirements.txt
```

## Step 3: Set Environment Variables

Create a `.env` file in the project root (if you don't have one):

```powershell
# .env file
FLASK_ENV=dev
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///app.db
```

Or set them in PowerShell:
```powershell
$env:FLASK_ENV="dev"
$env:SECRET_KEY="dev-secret-key-change-in-production"
```

## Step 4: Run Database Migrations

```powershell
# Check current migration status
flask db current

# Upgrade to latest migration (includes new indexes)
flask db upgrade

# If you get errors, you might need to stamp the database first:
# flask db stamp head
```

## Step 5: Test the Application Starts

```powershell
# Test that the app can be imported and initialized
python -c "from app import create_app; app = create_app('dev'); print('✓ App created successfully')"
```

## Step 6: Run Tests

```powershell
# Run all tests with coverage
$env:PYTHONPATH="."; pytest --cov=app --cov-report=term-missing -v

# Or just run tests without coverage
pytest -v
```

## Step 7: Start the Development Server

```powershell
# Run the application
python run.py

# Or using Flask CLI
flask run
```

The app should be available at `http://localhost:5000`

## Step 8: Test Key Features

1. **Register a new user** - Test password validation (should require 8+ chars, uppercase, lowercase, digit)
2. **Create an incident** - Test form validation and HTML sanitization
3. **Create a category** (as admin) - Test model validation
4. **Check audit logs** - Verify centralized audit logging works
5. **Check application logs** - Look in `app/logs/app.log` for structured logging

## Troubleshooting

### Import Errors
If you get `ModuleNotFoundError`, make sure:
- Virtual environment is activated
- All dependencies are installed: `pip install -r requirements.txt`

### Migration Errors
If migrations fail:
```powershell
# Check migration status
flask db current

# If needed, stamp to latest
flask db stamp head

# Then upgrade
flask db upgrade
```

### Database Errors
If database issues occur:
```powershell
# Check if database exists
# SQLite database should be at: app/app.db or instance/app.db

# If needed, recreate (WARNING: This deletes data)
flask db downgrade base
flask db upgrade
```

### Type Checking Errors
```powershell
# Run mypy to check for type errors
mypy app
```

### Linting Errors
```powershell
# Run flake8 to check code style
flake8 app tests
```

## Quick Verification Checklist

- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] Migrations run successfully
- [ ] App starts without errors
- [ ] Tests pass
- [ ] Can register a user
- [ ] Can create an incident
- [ ] Can create a category (as admin)
- [ ] Audit logs are created
- [ ] Application logs are written to `app/logs/app.log`

## Next Steps After Testing

Once everything works locally:
1. Commit your changes
2. Push to Git
3. GitHub Actions will run CI/CD pipeline automatically

