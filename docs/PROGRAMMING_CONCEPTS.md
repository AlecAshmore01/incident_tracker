# Programming Concepts and Syntax

This document describes the key programming concepts, syntax, and patterns used in the Incident Tracker application. It provides a detailed explanation of Python and Flask-specific features to help understand the codebase.

## Table of Contents

- [Python Syntax and Features](#python-syntax-and-features)
- [Flask Framework Concepts](#flask-framework-concepts)
- [SQLAlchemy ORM Concepts](#sqlalchemy-orm-concepts)
- [Design Patterns](#design-patterns)
- [Type Hints and Annotations](#type-hints-and-annotations)
- [Context Managers](#context-managers)
- [Error Handling Patterns](#error-handling-patterns)

---

## Python Syntax and Features

### 1. Decorators

**Concept**: Decorators are a powerful Python feature that allows functions to be modified or extended without changing their source code. They use the `@` syntax and are essentially functions that wrap other functions.

**Syntax**:
```python
@decorator_name
def my_function():
    pass
```

**Example from codebase** (`app/auth/routes.py`):
```python
@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login() -> ResponseReturnValue:
    # Function implementation
```

**Explanation**: 
- `@auth_bp.route()` registers the function as a URL route handler
- `@limiter.limit()` applies rate limiting to the function
- Multiple decorators are applied from bottom to top

**Custom Decorator Example** (`app/utils/error_handler.py`):
```python
def handle_db_errors(f: Callable) -> Callable:
    """Decorator to handle database errors automatically."""
    @wraps(f)  # Preserves function metadata
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        try:
            return f(*args, **kwargs)
        except Exception as e:
            db.session.rollback()  # Rollback on error
            log_error(e, f"Database error in {f.__name__}")
            raise DatabaseError(str(e))
    return decorated_function
```

**Usage**:
```python
@handle_db_errors
def create_incident(...):
    # Database operations automatically wrapped in error handling
```

### 2. Type Hints

**Concept**: Type hints allow developers to specify the expected types of function parameters and return values, improving code readability and enabling static type checking.

**Syntax**:
```python
def function_name(param: Type) -> ReturnType:
    pass
```

**Example from codebase** (`app/services/incident_service.py`):
```python
@staticmethod
def create_incident(
    title: str,
    description: str,
    status: str,
    category_id: int,
    user_id: int
) -> Incident:
    """Create a new incident."""
    # Implementation
```

**Benefits**:
- IDE autocomplete and error detection
- Self-documenting code
- Static type checking with `mypy`

**Optional Types**:
```python
from typing import Optional

def get_user(user_id: Optional[int] = None) -> Optional[User]:
    # Can accept None or int, returns None or User
```

### 3. Class Methods and Static Methods

**Static Methods** (`@staticmethod`):
- Don't require access to instance or class
- Can be called on the class directly
- Used for utility functions related to the class

**Example**:
```python
class IncidentService:
    @staticmethod
    def create_incident(...) -> Incident:
        # No 'self' parameter needed
        # Called as: IncidentService.create_incident(...)
```

**Class Methods** (`@classmethod`):
- Receive the class as first parameter (`cls`)
- Can access class-level attributes
- Used for alternative constructors

### 4. Context Managers

**Concept**: Context managers ensure proper resource management using the `with` statement. They automatically handle setup and teardown operations.

**Syntax**:
```python
with context_manager() as resource:
    # Use resource
# Resource automatically cleaned up
```

**Example from codebase** (`app/__init__.py`):
```python
with app.app_context():
    ensure_db_is_up_to_date(db.engine, migrations_path)
```

**Explanation**: 
- `app.app_context()` creates a Flask application context
- Required for accessing Flask features like `current_app`, `g`, etc.
- Automatically cleaned up when exiting the `with` block

**Database Session Context**:
```python
with app.app_context():
    user = User.query.filter_by(username='test').first()
    # Database session automatically managed
```

### 5. List Comprehensions and Generator Expressions

**List Comprehension**:
```python
# Traditional approach
categories = []
for i in range(1, 11):
    categories.append(IncidentCategory(name=f"Category {i}"))

# List comprehension (more Pythonic)
categories = [
    IncidentCategory(name=f"Category {i}", description=f"Description {i}")
    for i in range(1, 11)
]
```

**Generator Expression** (memory efficient):
```python
# Generator doesn't create full list in memory
category_names = (cat.name for cat in categories)
```

### 6. String Formatting

**f-strings** (Python 3.6+):
```python
name = "John"
message = f"Hello, {name}"  # "Hello, John"
```

**Example from codebase**:
```python
raise ValidationError(f"Status must be one of: {', '.join(allowed_statuses)}")
```

---

## Flask Framework Concepts

### 1. Application Factory Pattern

**Concept**: Instead of creating the Flask app instance globally, we use a factory function that creates and configures the app. This allows multiple app instances and easier testing.

**Syntax**:
```python
def create_app(config_name: str = 'dev') -> Flask:
    app = Flask(__name__)
    # Configure app
    return app
```

**Example from codebase** (`app/__init__.py`):
```python
def create_app(config_name: str = 'dev') -> Flask:
    app = Flask(__name__)
    config = DevConfig if config_name == 'dev' else ProdConfig
    app.config.from_object(config)
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    return app
```

**Benefits**:
- Multiple app instances (testing, development, production)
- Delayed configuration
- Easier testing with different configs

### 2. Blueprints

**Concept**: Blueprints organize related routes, templates, and static files into reusable components. They allow modular application structure.

**Syntax**:
```python
from flask import Blueprint

bp = Blueprint('name', __name__)

@bp.route('/path')
def view_function():
    pass
```

**Example from codebase** (`app/auth/routes.py`):
```python
from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register() -> ResponseReturnValue:
    # Registration logic
```

**Registration**:
```python
app.register_blueprint(auth_bp, url_prefix='/auth')
# Routes become: /auth/register, /auth/login, etc.
```

**Benefits**:
- Modular organization
- Reusable components
- Clear separation of concerns

### 3. Route Decorators

**Concept**: Flask uses decorators to map URLs to Python functions. The decorator defines the HTTP methods and URL pattern.

**Syntax**:
```python
@blueprint.route('/path', methods=['GET', 'POST'])
def view_function():
    pass
```

**Example**:
```python
@incident_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_incident(id: int) -> ResponseReturnValue:
    # id is automatically converted to integer
    # Handles both GET (display form) and POST (process form)
```

**URL Variables**:
- `<int:id>` - Integer parameter
- `<string:name>` - String parameter (default)
- `<path:filepath>` - Path parameter

### 4. Request Context

**Concept**: Flask uses context locals to provide request-specific data without passing it as parameters.

**Available Context Variables**:
- `request` - Current request object
- `session` - Session data
- `g` - Application context global
- `current_app` - Current application instance
- `current_user` - Current logged-in user (Flask-Login)

**Example**:
```python
from flask import request, current_app
from flask_login import current_user

@incident_bp.route('/create', methods=['POST'])
def create_incident():
    title = request.form.get('title')  # Access form data
    user_id = current_user.id  # Access current user
    app_name = current_app.config['APP_NAME']  # Access config
```

### 5. Template Rendering

**Concept**: Flask uses Jinja2 templating engine to render HTML templates with dynamic data.

**Syntax**:
```python
return render_template('template.html', variable=value)
```

**Example**:
```python
@incident_bp.route('/list')
def list_incidents():
    incidents = Incident.query.all()
    return render_template('incidents/list.html', incidents=incidents)
```

**Template Syntax** (Jinja2):
```jinja2
{% for incident in incidents %}
    <div>{{ incident.title }}</div>
{% endfor %}
```

### 6. Flash Messages

**Concept**: Flash messages store messages in the session that are displayed on the next request, typically for user feedback.

**Syntax**:
```python
flash('Message text', 'category')
```

**Example**:
```python
flash('Incident created successfully.', 'success')
flash('Error occurred.', 'danger')
```

**Display in Template**:
```jinja2
{% with messages = get_flashed_messages(with_categories=true) %}
    {% for category, message in messages %}
        <div class="alert alert-{{ category }}">{{ message }}</div>
    {% endfor %}
{% endwith %}
```

---

## SQLAlchemy ORM Concepts

### 1. Model Definition

**Concept**: SQLAlchemy models are Python classes that represent database tables. They use class attributes to define columns.

**Syntax**:
```python
class ModelName(db.Model):
    __tablename__ = 'table_name'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
```

**Example from codebase** (`app/models/incident.py`):
```python
class Incident(db.Model):
    __tablename__ = 'incidents'
    
    id: int = db.Column(db.Integer, primary_key=True)
    title: str = db.Column(db.String(200), nullable=False)
    description: str = db.Column(db.Text, nullable=False)
    status: str = db.Column(db.String(20), nullable=False, index=True)
    timestamp: datetime = db.Column(db.DateTime, default=datetime.utcnow)
    user_id: int = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id: int = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
```

**Column Types**:
- `db.Integer` - Integer
- `db.String(n)` - String with max length
- `db.Text` - Unlimited text
- `db.DateTime` - Date and time
- `db.Boolean` - Boolean

**Column Options**:
- `primary_key=True` - Primary key
- `nullable=False` - Not null constraint
- `unique=True` - Unique constraint
- `index=True` - Create index
- `default=value` - Default value

### 2. Relationships

**Concept**: SQLAlchemy relationships define how models relate to each other, similar to foreign keys in SQL.

**Syntax**:
```python
# One-to-Many
incidents = db.relationship('Incident', backref='creator', lazy='dynamic')

# Many-to-One (via ForeignKey)
user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
```

**Example**:
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    incidents = db.relationship('Incident', backref='creator', lazy='dynamic')

class Incident(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # Can access creator via: incident.creator
    # Can access incidents via: user.incidents
```

**Lazy Loading Options**:
- `lazy='select'` - Load on access (default)
- `lazy='dynamic'` - Returns query object (for filtering)
- `lazy='joined'` - Eager load with JOIN
- `lazy='subquery'` - Eager load with subquery

### 3. Query API

**Concept**: SQLAlchemy provides a Pythonic query interface instead of writing raw SQL.

**Basic Queries**:
```python
# Get all
users = User.query.all()

# Get by ID
user = User.query.get(1)

# Filter
users = User.query.filter_by(role='admin').all()
users = User.query.filter(User.role == 'admin').all()

# First result
user = User.query.filter_by(username='john').first()

# Count
count = User.query.count()
```

**Example from codebase**:
```python
incident = Incident.query.get(incident_id)
if not incident:
    raise NotFoundError(f"Incident with ID {incident_id} not found")
```

**Advanced Queries**:
```python
# Join
incidents = db.session.query(Incident).join(User).filter(User.role == 'admin').all()

# Order by
incidents = Incident.query.order_by(Incident.timestamp.desc()).all()

# Limit
incidents = Incident.query.limit(10).all()

# Pagination
incidents = Incident.query.paginate(page=1, per_page=20)
```

### 4. Model Validation

**Concept**: SQLAlchemy's `@validates` decorator allows model-level validation before data is saved.

**Syntax**:
```python
from sqlalchemy.orm import validates

@validates('field_name')
def validate_field(self, key, value):
    # Validation logic
    return value
```

**Example from codebase** (`app/models/incident.py`):
```python
@validates('title')
def validate_title(self, key: str, value: str) -> str:
    """Validate incident title."""
    if not value or not value.strip():
        raise ValidationError("Title cannot be empty")
    if len(value.strip()) > 200:
        raise ValidationError("Title must be 200 characters or less")
    return value.strip()
```

**Benefits**:
- Data integrity at model level
- Consistent validation across all code paths
- Automatic validation on save

### 5. Database Sessions

**Concept**: SQLAlchemy uses sessions to manage database transactions. Changes are staged in the session and committed together.

**Syntax**:
```python
# Add
db.session.add(object)
db.session.commit()

# Update
object.field = new_value
db.session.commit()

# Delete
db.session.delete(object)
db.session.commit()

# Rollback
db.session.rollback()
```

**Example from codebase**:
```python
incident = Incident(title="New Incident", ...)
db.session.add(incident)
db.session.commit()  # Saves to database
```

**Transaction Management**:
```python
try:
    db.session.add(incident)
    db.session.commit()
except Exception as e:
    db.session.rollback()  # Undo changes
    raise
```

---

## Design Patterns

### 1. Service Layer Pattern

**Concept**: Business logic is separated from route handlers into service classes. Routes become thin controllers that delegate to services.

**Structure**:
```
Route Handler (thin) → Service Layer (business logic) → Model (data)
```

**Example**:
```python
# Route (app/incidents/routes.py)
@incident_bp.route('/create', methods=['POST'])
def create_incident():
    form = IncidentForm()
    if form.validate_on_submit():
        incident = IncidentService.create_incident(
            title=form.title.data,
            description=form.description.data,
            ...
        )
        flash('Success!', 'success')
        return redirect(url_for('incident.list_incidents'))

# Service (app/services/incident_service.py)
class IncidentService:
    @staticmethod
    def create_incident(...) -> Incident:
        # Validation
        # Business rules
        # Database operations
        # Audit logging
        return incident
```

**Benefits**:
- Reusable business logic
- Easier testing
- Clear separation of concerns

### 2. Repository Pattern

**Concept**: Models act as repositories, providing a clean interface to database operations.

**Example**:
```python
# Instead of raw SQL
incident = Incident.query.get(id)
incidents = Incident.query.filter_by(status='Open').all()
```

### 3. Decorator Pattern

**Concept**: Decorators add functionality to functions without modifying them.

**Examples**:
- `@login_required` - Authentication check
- `@handle_db_errors` - Error handling
- `@validates` - Model validation

---

## Type Hints and Annotations

### Basic Types

```python
def function(param: str) -> int:
    return len(param)
```

### Optional Types

```python
from typing import Optional

def get_user(id: Optional[int] = None) -> Optional[User]:
    if id is None:
        return None
    return User.query.get(id)
```

### Union Types

```python
from typing import Union

def process(value: Union[str, int]) -> str:
    return str(value)
```

### Callable Types

```python
from typing import Callable

def decorator(f: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper
```

### Generic Types

```python
from typing import List, Dict

def get_all() -> List[User]:
    return User.query.all()

def get_dict() -> Dict[str, int]:
    return {'count': 10}
```

---

## Context Managers

### Flask Application Context

```python
with app.app_context():
    # Can access current_app, g, etc.
    user = User.query.get(1)
```

### Database Session Context

```python
with app.app_context():
    db.session.begin()
    try:
        # Database operations
        db.session.commit()
    except:
        db.session.rollback()
```

### Custom Context Manager

```python
from contextlib import contextmanager

@contextmanager
def transaction():
    db.session.begin()
    try:
        yield
        db.session.commit()
    except:
        db.session.rollback()
        raise

# Usage
with transaction():
    # Database operations
```

---

## Error Handling Patterns

### Try-Except Blocks

```python
try:
    # Risky operation
    result = operation()
except SpecificError as e:
    # Handle specific error
    log_error(e)
    flash('Error message', 'danger')
except Exception as e:
    # Handle any other error
    log_error(e)
    flash('Unexpected error', 'danger')
```

### Custom Exceptions

```python
class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

# Usage
if not valid:
    raise ValidationError("Invalid input")
```

### Error Handling Decorators

```python
@handle_db_errors
def database_operation():
    # Automatically handles database errors
    db.session.add(object)
    db.session.commit()
```

---

## Summary

This application demonstrates:

1. **Python Features**: Decorators, type hints, context managers, comprehensions
2. **Flask Patterns**: Application factory, blueprints, route decorators, context locals
3. **SQLAlchemy ORM**: Models, relationships, queries, validation, sessions
4. **Design Patterns**: Service layer, repository, decorator patterns
5. **Error Handling**: Custom exceptions, decorators, try-except blocks

These concepts work together to create a maintainable, testable, and secure web application following Python and Flask best practices.

