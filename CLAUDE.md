# CLAUDE.md -- ecommerce-capstone

This file is the authoritative instruction set for Claude Code when working on this project.
Read it in full before taking any action. Follow every constraint exactly as written.
When in doubt, ask rather than assume.

---

## 1. Project Overview

**ecommerce-capstone** is a simple e-commerce platform backend built with Django.
It is the capstone project for the Backend I module. Each student independently builds
a functional Python backend application within the group's chosen topic domain
(Simple E-Commerce Platform). The goal is not just to write code that runs; it is to
demonstrate sound architectural thinking, intentional tool selection, and
professional-grade project hygiene. Think of this as your first portfolio piece.

There are **three team members** working on this project:

| Member | Domain | Responsibilities |
|---|---|---|
| **Sabrina** | Orders / Cart | Shopping cart (add, remove, update quantities), order lifecycle (cart to confirmed order) |
| **Cleber** | Products | Products with name, description, price, stock, and category |
| **Diogo** | Users / Infrastructure | User roles (seller vs buyer), inventory management (stock decrements on order, restock endpoint), Docker, project setup |

Payment processing is mocked. There is no frontend. This is a pure backend project
exposing Django views that return JSON responses. The Django admin panel serves as the
visual interface for data inspection.

---

## 2. Technology Stack

| Layer | Technology | Notes |
|---|---|---|
| Web framework | Django 5.1+ | No async views. Use standard Django views returning JsonResponse. |
| Language | Python 3.12+ | Type hints encouraged but not mandatory |
| Database | SQLite 3 | Default Django SQLite backend. No PostgreSQL. |
| Sessions | Django sessions (DB-backed) | `django.contrib.sessions.backends.db` |
| Auth | Django built-in auth | `django.contrib.auth`. No JWT, no django-allauth, no third-party auth. |
| Package manager | uv (astral.sh) | All dependency management via `uv`. No pip, no poetry, no pipenv. |
| Containerisation | Docker (Dev Container, Docker-in-Docker) | Single Dockerfile. No docker-compose for multiple services. |
| Testing | pytest + pytest-django + factory_boy | Coverage target >80% per app |
| Server | uvicorn OR Django runserver | `python manage.py runserver` for dev |
| CLI utilities | Typer (optional) | Management commands only. Not required for core functionality. |
| Media storage | Local filesystem | `MEDIA_ROOT` = `media/` in project root |

### Explicitly Forbidden

Do NOT install or use any of the following:

- Redis, django-redis, or any external cache backend
- Celery or any task queue
- JWT (djangorestframework-simplejwt, PyJWT, etc.)
- Django REST Framework (djangorestframework)
- django-allauth, social-auth, or any third-party auth
- django-oscar, django-shop, saleor, or any pre-built e-commerce framework
- PostgreSQL, psycopg2, or any non-SQLite database in development
- Nginx, gunicorn in Docker (use runserver for dev)
- Any frontend framework (React, Vue, HTMX, etc.)

---

## 3. Repository Structure

Create exactly this layout. Do not add extra top-level directories without instruction.

```
ecommerce-capstone/
+-- CLAUDE.md
+-- README.md
+-- .env.example
+-- .gitignore
+-- Dockerfile
+-- .devcontainer/
|   +-- devcontainer.json
+-- pyproject.toml
+-- manage.py
+-- config/                        # Django project package
|   +-- __init__.py
|   +-- settings/
|   |   +-- __init__.py
|   |   +-- base.py
|   |   +-- dev.py
|   |   +-- prod.py               # Stubbed, not wired up
|   +-- urls.py
|   +-- wsgi.py
+-- apps/
|   +-- __init__.py
|   +-- users/                     # Diogo: User model, auth, roles
|   |   +-- __init__.py
|   |   +-- models.py
|   |   +-- views.py
|   |   +-- urls.py
|   |   +-- admin.py
|   |   +-- apps.py
|   |   +-- decorators.py          # @seller_required, @buyer_required
|   |   +-- services.py            # Business logic
|   |   +-- factories.py           # factory_boy factories
|   |   +-- tests/
|   |       +-- __init__.py
|   |       +-- test_models.py
|   |       +-- test_views.py
|   |       +-- test_decorators.py
|   +-- products/                  # Cleber: Product, Category, stock
|   |   +-- __init__.py
|   |   +-- models.py
|   |   +-- views.py
|   |   +-- urls.py
|   |   +-- admin.py
|   |   +-- apps.py
|   |   +-- services.py            # decrement_stock, restock logic
|   |   +-- signals.py             # post_save audit log
|   |   +-- factories.py           # factory_boy factories
|   |   +-- management/
|   |   |   +-- __init__.py
|   |   |   +-- commands/
|   |   |       +-- __init__.py
|   |   |       +-- seed_categories.py
|   |   |       +-- load_products.py
|   |   +-- tests/
|   |       +-- __init__.py
|   |       +-- test_models.py
|   |       +-- test_views.py
|   |       +-- test_services.py
|   +-- cart/                      # Sabrina: Cart and CartItem
|   |   +-- __init__.py
|   |   +-- models.py
|   |   +-- views.py
|   |   +-- urls.py
|   |   +-- admin.py
|   |   +-- apps.py
|   |   +-- services.py
|   |   +-- factories.py
|   |   +-- tests/
|   |       +-- __init__.py
|   |       +-- test_models.py
|   |       +-- test_views.py
|   +-- orders/                    # Sabrina: Order and OrderItem
|   |   +-- __init__.py
|   |   +-- models.py
|   |   +-- views.py
|   |   +-- urls.py
|   |   +-- admin.py
|   |   +-- apps.py
|   |   +-- services.py            # checkout, cancel, status transitions
|   |   +-- factories.py
|   |   +-- tests/
|   |       +-- __init__.py
|   |       +-- test_models.py
|   |       +-- test_views.py
|   |       +-- test_checkout.py
+-- docs/
|   +-- architecture.md
+-- media/                         # Gitignored, created at runtime
+-- tests/                         # Cross-app integration tests
|   +-- __init__.py
|   +-- test_purchase_flow.py
|   +-- test_cancel_restock.py
|   +-- test_full_lifecycle.py
+-- conftest.py                    # Shared pytest fixtures
+-- pytest.ini
```

---

## 4. Django Apps

Each app lives under `apps/`. Register them in `INSTALLED_APPS` as `apps.users`,
`apps.products`, `apps.cart`, `apps.orders`. Each app must have its own `urls.py`,
`models.py`, `views.py`, `admin.py`, `apps.py`, and `services.py`.

### 4.1 apps.users (Owner: Diogo)

**Purpose:** Custom user model, authentication, and role-based access control.

**URLs (under `/api/users/`):**

| Name | Path | View | Method | Notes |
|---|---|---|---|---|
| `users:register` | `register/` | `register_view` | POST | Creates new user with role |
| `users:login` | `login/` | `login_view` | POST | Django authenticate() + login() |
| `users:logout` | `logout/` | `logout_view` | POST | Django logout() |
| `users:profile` | `profile/` | `profile_view` | GET, PUT | Login required |
| `users:change-password` | `change-password/` | `change_password_view` | POST | Login required |
| `users:seller-detail` | `sellers/<int:pk>/` | `seller_detail_view` | GET | Public |
| `users:seller-list` | `sellers/` | `seller_list_view` | GET | Public, paginated |

**Models:**

#### User (extends AbstractUser)

```
id              -- AutoField PK (inherited)
username        -- CharField (inherited from AbstractUser)
email           -- EmailField(unique=True)
role            -- CharField(max_length=10, choices=[('buyer','Buyer'),('seller','Seller')], default='buyer')
phone           -- CharField(max_length=20, blank=True)
bio             -- TextField(blank=True)
```

Rules:
- Set `AUTH_USER_MODEL = 'users.User'` in settings BEFORE the first migration.
- `__str__` returns username.
- Default ordering by `-date_joined`.
- Email must be unique at the model level.

### 4.2 apps.products (Owner: Cleber)

**Purpose:** Product catalogue, categories, stock management.

**URLs (under `/api/products/` and `/api/categories/`):**

| Name | Path | View | Method | Notes |
|---|---|---|---|---|
| `products:list` | `products/` | `product_list_view` | GET | Public, paginated, filterable |
| `products:detail` | `products/<int:pk>/` | `product_detail_view` | GET | Public |
| `products:create` | `products/create/` | `product_create_view` | POST | Seller only |
| `products:update` | `products/<int:pk>/update/` | `product_update_view` | PUT | Seller + owner only |
| `products:delete` | `products/<int:pk>/delete/` | `product_delete_view` | DELETE | Seller + owner only (soft delete) |
| `products:restock` | `products/<int:pk>/restock/` | `restock_view` | POST | Seller + owner only |
| `products:low-stock` | `products/low-stock/` | `low_stock_view` | GET | Seller only |
| `products:seller-dashboard` | `products/dashboard/` | `seller_dashboard_view` | GET | Seller only |
| `categories:list` | `categories/` | `category_list_view` | GET | Public |
| `categories:create` | `categories/create/` | `category_create_view` | POST | Admin/staff only |

**Models:**

#### Category

```
id              -- AutoField PK
name            -- CharField(max_length=200, unique=True)
slug            -- SlugField(unique=True)
description     -- TextField(blank=True)
```

Rules:
- Slug auto-generated from name in `save()` using `django.utils.text.slugify`.
- `__str__` returns name.

#### Product

```
id              -- AutoField PK
name            -- CharField(max_length=200)
slug            -- SlugField(unique=True)
description     -- TextField(max_length=2000)
price           -- DecimalField(max_digits=10, decimal_places=2)
stock           -- PositiveIntegerField(default=0)
category        -- FK(Category, on_delete=PROTECT, related_name='products')
seller          -- FK(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='products')
image           -- ImageField(upload_to='products/', blank=True, null=True)
is_active       -- BooleanField(default=True)
created_at      -- DateTimeField(auto_now_add=True)
updated_at      -- DateTimeField(auto_now=True)
```

Rules:
- Slug auto-generated from name in `save()`. Handle duplicates by appending a numeric suffix.
- Price must be > 0. Enforce in `clean()` method with `ValidationError`.
- `is_available` property: returns `True` if `is_active` and `stock > 0`.
- `__str__` returns product name.
- Default ordering by `-created_at`.
- Add `help_text` to all fields.
- All money values use `DecimalField`, never `FloatField`.

#### StockChange

```
id              -- AutoField PK
product         -- FK(Product, on_delete=CASCADE, related_name='stock_changes')
change_qty      -- IntegerField()  # positive for restock, negative for orders
reason          -- CharField(max_length=20, choices=[('order','Order'),('restock','Restock'),('manual','Manual')])
user            -- FK(settings.AUTH_USER_MODEL, null=True, on_delete=SET_NULL)
created_at      -- DateTimeField(auto_now_add=True)
```

Rules:
- Every stock change (from orders, restocks, manual adjustments) must be logged here.
- Created automatically by the `decrement_stock()` and restock functions in `services.py`.

### 4.3 apps.cart (Owner: Sabrina)

**Purpose:** Shopping cart management.

**URLs (under `/api/cart/`):**

| Name | Path | View | Method | Notes |
|---|---|---|---|---|
| `cart:view` | `` | `cart_view` | GET | Buyer only, shows active cart |
| `cart:add` | `add/` | `cart_add_view` | POST | Buyer only |
| `cart:remove` | `remove/<int:item_id>/` | `cart_remove_view` | DELETE | Buyer only |
| `cart:update` | `update/<int:item_id>/` | `cart_update_view` | PUT | Buyer only |
| `cart:clear` | `clear/` | `cart_clear_view` | POST | Buyer only |

**Models:**

#### Cart

```
id              -- AutoField PK
buyer           -- FK(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='carts')
status          -- CharField(max_length=10, choices=[('open','Open'),('closed','Closed')], default='open')
created_at      -- DateTimeField(auto_now_add=True)
updated_at      -- DateTimeField(auto_now=True)
```

Rules:
- Only ONE open cart per buyer at any time. Use `get_or_create(buyer=user, status='open')`.
- `subtotal` property: aggregates all CartItem subtotals. Returns `Decimal('0.00')` if empty.
- `__str__` returns `"Cart #{id} ({status}) - {buyer.username}"`.

#### CartItem

```
id              -- AutoField PK
cart            -- FK(Cart, on_delete=CASCADE, related_name='items')
product         -- FK('products.Product', on_delete=CASCADE)
quantity        -- PositiveIntegerField(default=1)
added_at        -- DateTimeField(auto_now_add=True)
```

Rules:
- `unique_together = [('cart', 'product')]`. A product appears once per cart; adding again increments quantity.
- `subtotal` property: `return self.quantity * self.product.price`.

### 4.4 apps.orders (Owner: Sabrina)

**Purpose:** Order lifecycle management.

**URLs (under `/api/orders/`):**

| Name | Path | View | Method | Notes |
|---|---|---|---|---|
| `orders:checkout` | `checkout/` | `checkout_view` | POST | Buyer only, creates order from cart |
| `orders:detail` | `<int:pk>/` | `order_detail_view` | GET | Buyer sees own order |
| `orders:list` | `` | `order_list_view` | GET | Buyer sees own orders |
| `orders:confirm` | `<int:pk>/confirm/` | `confirm_order_view` | POST | Buyer only |
| `orders:cancel` | `<int:pk>/cancel/` | `cancel_order_view` | POST | Buyer only, within 30min window |
| `orders:seller-orders` | `seller/` | `seller_orders_view` | GET | Seller sees orders with their products |
| `orders:seller-fulfil` | `<int:pk>/items/<int:item_id>/fulfil/` | `seller_fulfil_view` | POST | Seller only |
| `orders:summary` | `summary/` | `order_summary_view` | GET | Seller/admin, date range aggregation |

**Models:**

#### Order

```
id              -- AutoField PK
buyer           -- FK(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='orders')
status          -- CharField(max_length=20, choices=OrderStatus.choices, default='pending')
total_amount    -- DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
created_at      -- DateTimeField(auto_now_add=True, db_index=True)
updated_at      -- DateTimeField(auto_now=True)
```

#### OrderStatus (TextChoices)

```python
class OrderStatus(models.TextChoices):
    PENDING    = 'pending',    'Pending'
    CONFIRMED  = 'confirmed',  'Confirmed'
    CANCELLED  = 'cancelled',  'Cancelled'
```

Valid transitions (enforce in a `transition_status()` model method):
- `pending` -> `confirmed`
- `pending` -> `cancelled`
- All other transitions must raise `ValueError`.

Rules:
- `total` property: aggregates all OrderItem (qty * unit_price). Use aggregate or Python sum.
- Cancellation is only allowed within 30 minutes of `created_at`.
- `__str__` returns `"Order #{id} ({status}) - {buyer.username}"`.

#### OrderItem

```
id                  -- AutoField PK
order               -- FK(Order, on_delete=CASCADE, related_name='items')
product             -- FK('products.Product', on_delete=PROTECT)
quantity            -- PositiveIntegerField()
unit_price          -- DecimalField(max_digits=10, decimal_places=2)  # snapshot at order time
fulfilment_status   -- CharField(max_length=20, choices=[('unfulfilled','Unfulfilled'),('fulfilled','Fulfilled')], default='unfulfilled')
```

Rules:
- `unit_price` is a snapshot of `product.price` at checkout time. Never update it.
- `subtotal` property: `return self.unit_price * self.quantity`.
- `fulfilment_status` is updated by the seller, not the buyer.

---

## 5. View Conventions

All views are **function-based views** (FBV) returning `JsonResponse`.
Do NOT use Django REST Framework. Do NOT use class-based views.

### Request Parsing

```python
import json
from django.http import JsonResponse

def my_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    # ... process data ...
    return JsonResponse({'success': True, 'data': result})
```

### Authentication

Use Django's built-in `@login_required` decorator. For role checks, use the custom
decorators in `apps/users/decorators.py`:

```python
from django.contrib.auth.decorators import login_required
from apps.users.decorators import seller_required, buyer_required

@login_required
@buyer_required
def cart_add_view(request):
    ...
```

### Error Responses

Always return JSON. Standard error shape:

```python
JsonResponse({'error': 'Description of what went wrong'}, status=4XX)
```

### Success Responses

```python
JsonResponse({'success': True, 'data': {...}})
# or for lists:
JsonResponse({'success': True, 'data': [...], 'page': 1, 'total_pages': 5})
```

### Pagination

Use Django's built-in `Paginator`:

```python
from django.core.paginator import Paginator

paginator = Paginator(queryset, 20)  # 20 items per page
page_number = request.GET.get('page', 1)
page_obj = paginator.get_page(page_number)
```

Default page size: 20. Accept `?page_size` param, max 100.

---

## 6. Service Layer

Business logic lives in `services.py` in each app, NOT in views or models.
Views are thin: they parse input, call a service function, and return the result as JSON.

### Example pattern:

```python
# apps/products/services.py
from django.db.models import F
from apps.products.models import Product, StockChange

def decrement_stock(product_id, quantity, user=None):
    """Atomically decrement stock. Raises ValueError if insufficient."""
    updated = Product.objects.filter(
        pk=product_id, stock__gte=quantity
    ).update(stock=F('stock') - quantity)
    if updated == 0:
        raise ValueError(f"Insufficient stock for product {product_id}")
    StockChange.objects.create(
        product_id=product_id,
        change_qty=-quantity,
        reason='order',
        user=user,
    )

def restock(product_id, quantity, user):
    """Add stock to a product. Only the product owner can restock."""
    Product.objects.filter(pk=product_id).update(stock=F('stock') + quantity)
    StockChange.objects.create(
        product_id=product_id,
        change_qty=quantity,
        reason='restock',
        user=user,
    )
```

---

## 7. Checkout Flow

The checkout process (in `apps/orders/services.py`) must follow this exact sequence:

1. Get the buyer's open cart. If cart has zero items, raise `ValueError`.
2. Wrap everything in `transaction.atomic()`.
3. Create an `Order` with status `pending` and buyer = request.user.
4. For each `CartItem` in the cart:
   a. Call `decrement_stock(product.id, cartitem.quantity, user=buyer)`.
   b. Create an `OrderItem` with `unit_price = cartitem.product.price` (snapshot).
5. Use `OrderItem.objects.bulk_create()` for all order items.
6. Compute `order.total_amount` from the created items and save.
7. Mark the cart as `closed` (status='closed').
8. If ANY step fails (e.g., insufficient stock), the entire transaction rolls back.

---

## 8. Authentication and Sessions

- Use Django's built-in `django.contrib.auth` entirely.
- Sessions are stored in the database (`django.contrib.sessions.backends.db`).
- `SESSION_COOKIE_AGE = 60 * 60 * 24 * 14` (14 days).
- Login view uses `django.contrib.auth.authenticate()` and `login()`.
- Logout view uses `django.contrib.auth.logout()`.
- Registration creates a User with `User.objects.create_user()`.
- `@login_required` returns `JsonResponse({'error': 'Authentication required'}, status=401)`.
  Override `LOGIN_URL` or handle in a custom decorator that returns JSON instead of redirecting.

### Custom login_required for JSON APIs

Since all views return JSON, the default `@login_required` redirect behaviour is wrong.
Create a custom version in `apps/users/decorators.py`:

```python
from functools import wraps
from django.http import JsonResponse

def login_required_json(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper

def seller_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        if request.user.role != 'seller':
            return JsonResponse({'error': 'Seller access required'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper

def buyer_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        if request.user.role != 'buyer':
            return JsonResponse({'error': 'Buyer access required'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper
```

---

## 9. Docker Setup

Single Dockerfile using a Dev Container pattern with Docker-in-Docker support.
No docker-compose. No PostgreSQL container. No Redis container.
The database is SQLite (file-based, inside the container).

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml .

# Install dependencies
RUN uv sync --frozen --no-dev || uv sync

# Copy project
COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### .devcontainer/devcontainer.json

```json
{
  "name": "ecommerce-capstone",
  "build": {
    "dockerfile": "../Dockerfile"
  },
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {}
  },
  "forwardPorts": [8000],
  "postCreateCommand": "uv sync && python manage.py migrate",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.debugpy"
      ]
    }
  }
}
```

---

## 10. Settings Architecture

Use split settings: `config/settings/base.py`, `config/settings/dev.py`.
The `DJANGO_SETTINGS_MODULE` env var selects the active settings file.
Default: `config.settings.dev`.

### config/settings/base.py

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-in-production')
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Project apps
    'apps.users',
    'apps.products',
    'apps.cart',
    'apps.orders',
]

AUTH_USER_MODEL = 'users.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14  # 14 days

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Pagination defaults
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
```

### config/settings/dev.py

```python
from .base import *  # noqa: F401,F403

DEBUG = True
```

### config/settings/prod.py

```python
from .base import *  # noqa: F401,F403

DEBUG = False
# Stubbed for future use
```

---

## 11. URL Configuration

### config/urls.py

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('apps.users.urls')),
    path('api/products/', include('apps.products.urls', namespace='products')),
    path('api/categories/', include('apps.products.category_urls', namespace='categories')),
    path('api/cart/', include('apps.cart.urls', namespace='cart')),
    path('api/orders/', include('apps.orders.urls', namespace='orders')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

Note: `apps.products` has two URL files: `urls.py` for product endpoints and
`category_urls.py` for category endpoints.

---

## 12. Dependencies (pyproject.toml)

```toml
[project]
name = "ecommerce-capstone"
version = "0.1.0"
description = "Simple E-Commerce Platform - Backend I Capstone"
requires-python = ">=3.12"
dependencies = [
    "django>=5.1,<6.0",
    "Pillow>=10.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-django>=4.8",
    "pytest-cov>=5.0",
    "factory-boy>=3.3",
]

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.dev"
python_files = ["tests.py", "test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--tb=short -q"
```

---

## 13. Admin Registration

Every model must be registered in its app's `admin.py`. Use `@admin.register` decorator.
Apply the following as a minimum:

- **User**: Use `UserAdmin` as base. `list_display = ['username', 'email', 'role', 'is_active']`,
  `list_filter = ['role', 'is_active']`, `search_fields = ['username', 'email']`
- **Category**: `list_display = ['name', 'slug']`, `prepopulated_fields = {'slug': ('name',)}`
- **Product**: `list_display = ['name', 'price', 'stock', 'category', 'seller', 'is_active']`,
  `list_filter = ['category', 'is_active']`, `search_fields = ['name']`,
  `prepopulated_fields = {'slug': ('name',)}`
- **StockChange**: `list_display = ['product', 'change_qty', 'reason', 'user', 'created_at']`,
  `list_filter = ['reason']`, `readonly_fields = ['product', 'change_qty', 'reason', 'user', 'created_at']`
- **Cart**: `list_display = ['id', 'buyer', 'status', 'created_at']`, `list_filter = ['status']`
- **CartItem**: inline on Cart admin using `TabularInline`
- **Order**: `list_display = ['id', 'buyer', 'status', 'total_amount', 'created_at']`,
  `list_filter = ['status']`, `readonly_fields = ['total_amount', 'created_at']`
- **OrderItem**: inline on Order admin using `TabularInline`, all fields `readonly`

---

## 14. Testing

### pytest.ini

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.dev
python_files = tests.py test_*.py
python_classes = Test*
python_functions = test_*
addopts = --tb=short -q
```

### conftest.py (project root)

```python
import pytest
from apps.users.factories import UserFactory, BuyerFactory, SellerFactory

@pytest.fixture
def buyer(db):
    return BuyerFactory()

@pytest.fixture
def seller(db):
    return SellerFactory()

@pytest.fixture
def admin_user(db):
    return UserFactory(is_staff=True, is_superuser=True)
```

### Factory conventions

Each app has a `factories.py` using `factory_boy`:

```python
# apps/users/factories.py
import factory
from apps.users.models import User

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    role = 'buyer'
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')

class BuyerFactory(UserFactory):
    role = 'buyer'

class SellerFactory(UserFactory):
    role = 'seller'
```

### Running tests

```bash
uv run pytest                          # run all tests
uv run pytest apps/users/              # run user tests only
uv run pytest --cov=apps --cov-report=term-missing   # with coverage
```

---

## 15. .env.example

```
DJANGO_SETTINGS_MODULE=config.settings.dev
SECRET_KEY=change-me-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## 16. .gitignore

```
__pycache__/
*.py[cod]
*.sqlite3
db.sqlite3
.env
media/
*.egg-info/
dist/
.venv/
.uv/
.pytest_cache/
htmlcov/
.coverage
```

---

## 17. CSRF Handling for JSON API Views

Since all views accept JSON POST/PUT/DELETE requests (not HTML forms), you must handle
Django's CSRF protection. Two options:

**Option A (Recommended for this project):** Use `@csrf_exempt` on API views and rely on
session authentication. This is acceptable because this is a demo/capstone project, not
production.

```python
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@buyer_required
def cart_add_view(request):
    ...
```

**Option B:** Send the CSRF token in a cookie and include it in the `X-CSRFToken` header.
This is more correct but adds complexity to testing.

Choose Option A for simplicity. Apply `@csrf_exempt` to all POST/PUT/DELETE views.

---

## 18. Constraints and Non-Goals

- Do NOT use Django REST Framework. Use plain Django views + JsonResponse.
- Do NOT use JWT or token-based auth. Use Django sessions.
- Do NOT use Redis, Celery, or any external service beyond SQLite.
- Do NOT use PostgreSQL. SQLite only.
- Do NOT implement a frontend. JSON API only + Django admin for data inspection.
- Do NOT implement real payment processing.
- Do NOT implement email sending or notifications.
- Do NOT use class-based views. Function-based views only.
- All money values use `DecimalField`, never `FloatField`.
- All PKs are standard auto-increment integers.
- Never commit `.env` or `db.sqlite3`.

---

---

# PHASE EXECUTION GUIDE

This section defines the exact order in which each team member should build their part.
Phases are designed so that after certain checkpoints, the project can be started up and
tested. Each phase lists the sprint backlog task IDs it covers.

**IMPORTANT:** Phases must be executed in order. Phase 1 must be complete for all members
before anyone starts Phase 2. After Phase 3, the project should be runnable and testable.

---

## DIOGO -- Users and Infrastructure

### Phase 1: Project Foundation (Tasks: D24, D25, D27, D28, D29)

This phase MUST be completed first before Sabrina or Cleber can start.

**Step-by-step:**

1. Create the root directory `ecommerce-capstone/` and initialize git.
2. Create `pyproject.toml` with all dependencies as specified in Section 12.
3. Run `uv sync` to create the virtual environment and install dependencies.
4. Run `uv run django-admin startproject config .` to create the Django project.
5. Delete the auto-generated `config/settings.py` file.
6. Create `config/settings/` package with `__init__.py`, `base.py`, `dev.py`, `prod.py`
   as specified in Section 10.
7. Create `.env.example` as specified in Section 15.
8. Create `.gitignore` as specified in Section 16.
9. Create the four Django apps:
   ```bash
   mkdir -p apps
   touch apps/__init__.py
   uv run python manage.py startapp users apps/users
   uv run python manage.py startapp products apps/products
   uv run python manage.py startapp cart apps/cart
   uv run python manage.py startapp orders apps/orders
   ```
10. Update each app's `apps.py` to use the correct name (e.g., `name = 'apps.users'`).
11. Create `config/urls.py` as specified in Section 11 (use placeholder `urlpatterns = []`
    in each app's `urls.py` for now).
12. Create `pytest.ini` and `conftest.py` at project root as specified in Section 14.
13. Create the `tests/` directory with `__init__.py`.
14. Create the `docs/` directory.
15. Verify: `uv run python manage.py check` passes with no errors.
16. Verify: `DJANGO_SETTINGS_MODULE=config.settings.dev uv run python manage.py check` passes.

**Checkpoint:** The project skeleton exists. `manage.py check` passes. No models yet.

### Phase 2: User Model and Auth (Tasks: D1, D2, D3, D4, D5, D17, D18, D19)

**Step-by-step:**

1. In `apps/users/models.py`, create the custom `User` model extending `AbstractUser`:
   - Add `role` field with `TextChoices` for 'buyer' and 'seller', default 'buyer'.
   - Add `phone` CharField (max_length=20, blank=True).
   - Add `bio` TextField (blank=True).
   - Set `email` field to `unique=True`.
   - Implement `__str__` returning username.
   - Add `Meta` class with `ordering = ['-date_joined']` and verbose names.
2. Confirm `AUTH_USER_MODEL = 'users.User'` is in `base.py` settings.
3. Run `uv run python manage.py makemigrations users`.
4. Run `uv run python manage.py migrate`.
5. Create `apps/users/decorators.py` with `login_required_json`, `seller_required`,
   and `buyer_required` as specified in Section 8.
6. Create `apps/users/views.py` with:
   - `register_view`: POST, accepts JSON `{username, email, password, role}`.
     Uses `User.objects.create_user()`. Returns `JsonResponse` with user data.
   - `login_view`: POST, accepts `{username, password}`.
     Uses `authenticate()` + `login()`. Returns success/error JSON.
   - `logout_view`: POST, uses `logout()`. Returns success JSON.
   - `profile_view`: GET returns profile data, PUT updates email/phone/bio (not role).
   - `change_password_view`: POST, accepts `{old_password, new_password}`.
     Uses `check_password()` + `set_password()`.
7. Create `apps/users/urls.py` with all URL patterns as specified in Section 4.1.
   Include `app_name = 'users'`.
8. Configure `AUTH_PASSWORD_VALIDATORS` in `base.py` as specified in Section 10.
9. Run `uv run python manage.py check` to verify.

**Checkpoint:** Users can register, login, logout, view/update profile. Role decorators exist.

### Phase 3: User Admin, Public Views, Fixtures (Tasks: D6, D7, D8, D9, D10, D11, D16, D19, D22)

**Step-by-step:**

1. Create `apps/users/admin.py`: register User model with full admin config as specified
   in Section 13.
2. Create `seller_detail_view` in views.py: GET, public, returns seller info with
   annotated product_count (annotation can be a placeholder returning 0 until products
   app exists).
3. Create `seller_list_view` in views.py: GET, public, paginated list of sellers.
4. Add the seller URLs to `apps/users/urls.py`.
5. Create `apps/users/factories.py` with `UserFactory`, `BuyerFactory`, `SellerFactory`
   as specified in Section 14.
6. Create `apps/users/tests/` directory with `__init__.py`, `test_models.py`,
   `test_views.py`, `test_decorators.py`.
7. Write tests for: user creation, login, logout, profile view/update, role decorators,
   password change, email uniqueness.
8. Run `uv run pytest apps/users/ -v` and verify all pass.
9. Run `uv run python manage.py createsuperuser` and verify admin panel works.

**Checkpoint:** Full user system working. Admin panel shows users. Tests pass. Sabrina and
Cleber can now start their Phase 2 work (they depend on D1 and D5).

### Phase 4: Docker and Documentation (Tasks: D26, D30, D31)

**Step-by-step:**

1. Create `Dockerfile` as specified in Section 9.
2. Create `.devcontainer/devcontainer.json` as specified in Section 9.
3. Build and test the Docker image:
   ```bash
   docker build -t ecommerce-capstone .
   docker run -p 8000:8000 ecommerce-capstone
   ```
4. Verify the server starts and responds on http://localhost:8000/admin/.
5. Create `README.md` with: project overview, prerequisites (Python 3.12+, uv),
   local setup steps, Docker setup steps, env vars, how to run tests, project structure,
   team members and responsibilities.
6. Create `docs/architecture.md` with Mermaid diagrams: system overview, data model
   relationships, request flow, app boundaries and inter-app dependencies.

**Checkpoint:** Docker works. Documentation exists. New developer can onboard in <15 minutes.

### Phase 5: Integration and Service Layer (Tasks: D12, D13, D14, D15, D20, D21, D23, D32, D33)

**Step-by-step:**

1. Verify `@login_required` (JSON version) is applied to all protected views across
   all apps. Test anonymous access returns 401.
2. Create `apps/users/services.py` and extract any business logic from views.
3. Create `seller_can_view_orders` integration: ensure D14 view (reusing S21) works
   for sellers.
4. Create `buyer_can_view_orders` integration: ensure D15 view (reusing S19) works
   for buyers.
5. Write integration test `tests/test_full_lifecycle.py`: register seller, create product,
   register buyer, add to cart, checkout, confirm, verify stock.
6. Write remaining user unit tests to reach >80% coverage.
7. Run `uv run pytest --cov=apps.users --cov-report=term-missing`.

**Checkpoint:** All user functionality complete. Integration tests pass end-to-end.

---

## CLEBER -- Products

### Phase 1: Wait for Diogo's Phase 2

Cleber cannot start until Diogo has completed Phase 2 (User model and AUTH_USER_MODEL
exist, migrations applied). Pull Diogo's code and verify `uv run python manage.py check` passes.

### Phase 2: Core Models (Tasks: C1, C2, C13, C14, C17, C21, C33)

**Step-by-step:**

1. In `apps/products/models.py`, create the `Category` model:
   - `name` CharField(max_length=200, unique=True)
   - `slug` SlugField(unique=True)
   - `description` TextField(blank=True)
   - Override `save()` to auto-generate slug from name using `slugify`.
   - Implement `__str__` returning name.
2. Create the `Product` model with all fields as specified in Section 4.2:
   - All fields with proper constraints, help_text, and validators.
   - Override `save()` to auto-generate slug from name. Handle duplicates with suffix.
   - Override `clean()` to validate price > 0.
   - Add `is_available` property.
   - Add `image` ImageField (optional).
   - Set `Meta` ordering `['-created_at']` and verbose names.
   - Implement `__str__`.
   - Enforce `max_length` on name (200) and description (2000).
3. Create the `StockChange` model as specified in Section 4.2.
4. Run `uv run python manage.py makemigrations products`.
5. Run `uv run python manage.py migrate`.
6. Verify: `uv run python manage.py check` passes.

**Checkpoint:** Product and Category tables exist in database. Models are complete.

### Phase 3: CRUD Views and URLs (Tasks: C3, C4, C5, C6, C7, C8, C9, C15, C16, C25)

**Step-by-step:**

1. Create `apps/products/services.py` with `decrement_stock()` and `restock()` as
   specified in Section 6 (service layer). These are utility functions, not views.
2. Create `apps/products/views.py` with all views as function-based views returning
   JsonResponse:
   - `product_list_view`: GET, public, paginated. Supports `?category=<slug>`,
     `?search=<term>`, `?ordering=<field>` (name, price, -created_at, popular).
     Only returns active products. Uses `select_related('category', 'seller')`.
   - `product_detail_view`: GET, public. Returns full product info. 404 if inactive.
   - `product_create_view`: POST, `@seller_required`. Auto-assigns seller = request.user.
   - `product_update_view`: PUT, `@seller_required`. Only product owner can update.
   - `product_delete_view`: DELETE, `@seller_required`. Soft-delete (set is_active=False).
     Reject if product has pending/confirmed orders.
   - `restock_view`: POST, `@seller_required`. Only product owner. Uses `restock()` service.
   - `low_stock_view`: GET, `@seller_required`. Lists seller's products with stock < threshold.
   - `seller_dashboard_view`: GET, `@seller_required`. Lists seller's products with
     aggregated order revenue.
   - `category_list_view`: GET, public. Returns categories with product count annotation.
   - `category_create_view`: POST, admin/staff only.
3. Create `apps/products/urls.py` with `app_name = 'products'` and all product URL patterns.
4. Create `apps/products/category_urls.py` with `app_name = 'categories'` and category patterns.
5. Verify all URLs resolve: `uv run python manage.py show_urls` (or test manually).

**Checkpoint:** All product endpoints respond. Seller can create, update, soft-delete, restock.
Public can browse and search products.

### Phase 4: Admin, Signals, Commands, Factories (Tasks: C20, C23, C24, C26, C30, C31)

**Step-by-step:**

1. Create `apps/products/admin.py` with full admin config as specified in Section 13.
2. Create `apps/products/signals.py`: connect `post_save` on Product to log creation
   and update events using Python's `logging` module.
3. Register the signal in `apps/products/apps.py` `ready()` method.
4. Create `apps/products/management/commands/seed_categories.py`: management command
   that creates default categories (Electronics, Clothing, Books, Home, Sports) using
   `get_or_create`. Must be idempotent.
5. Create `apps/products/management/commands/load_products.py`: management command
   that loads products from a JSON file argument. Uses `get_or_create`. Idempotent.
6. Create `apps/products/factories.py` with `CategoryFactory` and `ProductFactory`
   using `factory_boy`.
7. Run `uv run python manage.py seed_categories` and verify categories exist in admin.

**Checkpoint:** Admin panel shows products/categories. Management commands work.
Factories ready for tests.

### Phase 5: Testing and Integration (Tasks: C22, C27, C28, C29, C32)

**Step-by-step:**

1. Create `apps/products/tests/` directory with `__init__.py`, `test_models.py`,
   `test_views.py`, `test_services.py`.
2. Write model tests: creation, slug generation, price validation, is_available property,
   field constraints, __str__.
3. Write view tests: product list (pagination, filtering by category, search, ordering),
   product detail, create (seller only), update (owner only), delete (soft-delete,
   rejection with active orders), restock, low stock, seller dashboard, category CRUD.
4. Write service tests: decrement_stock (success, insufficient stock, atomicity),
   restock (success).
5. Configure pagination: test page boundaries and max page size.
6. Implement product ordering by popularity (annotate from OrderItems, requires orders
   app to exist).
7. Write integration test in `apps/products/tests/`: seller creates product, buyer
   views it, buyer adds to cart, seller restocks.
8. Run `uv run pytest apps/products/ --cov=apps.products --cov-report=term-missing`.
   Target >80%.

**Checkpoint:** All product functionality complete and tested.

---

## SABRINA -- Cart and Orders

### Phase 1: Wait for Diogo's Phase 2 and Cleber's Phase 2

Sabrina cannot start until the User model (D1, D5) and Product model (C1, C2) exist
and migrations are applied. Pull their code and verify `uv run python manage.py check` passes.

### Phase 2: Cart Models and Views (Tasks: S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S30)

**Step-by-step:**

1. In `apps/cart/models.py`, create the `Cart` model:
   - All fields as specified in Section 4.3.
   - Add `subtotal` property using
     `self.items.aggregate(total=Sum(F('quantity') * F('product__price')))`.
   - Implement `__str__`.
2. Create the `CartItem` model:
   - All fields as specified in Section 4.3.
   - Add `unique_together = [('cart', 'product')]`.
   - Add `subtotal` property.
3. Run `uv run python manage.py makemigrations cart`.
4. Run `uv run python manage.py migrate`.
5. Create `apps/cart/services.py` with helper functions:
   - `get_or_create_cart(user)`: returns the user's open cart.
   - `add_to_cart(user, product_id, quantity)`: adds or increments. Validates stock.
   - `remove_from_cart(user, item_id)`: removes a CartItem.
   - `update_cart_item(user, item_id, quantity)`: updates quantity. Validates stock.
   - `clear_cart(user)`: removes all items from open cart.
   - `get_cart_contents(user)`: returns cart with items, product details, subtotals,
     and stock availability flags.
6. Create `apps/cart/views.py` with all views as FBVs:
   - `cart_view`: GET, `@buyer_required`. Returns cart contents via service.
   - `cart_add_view`: POST, `@buyer_required`, `@csrf_exempt`. Accepts `{product_id, quantity}`.
   - `cart_remove_view`: DELETE, `@buyer_required`, `@csrf_exempt`.
   - `cart_update_view`: PUT, `@buyer_required`, `@csrf_exempt`. Accepts `{quantity}`.
   - `cart_clear_view`: POST, `@buyer_required`, `@csrf_exempt`.
7. Create `apps/cart/urls.py` with `app_name = 'cart'` and all cart URL patterns.
8. Verify: all cart endpoints respond correctly using Django shell or curl.

**Checkpoint:** Cart system works. Buyer can add, remove, update items and view cart.

### Phase 3: Order Models and Checkout (Tasks: S12, S13, S14, S15, S16, S17, S20, S22, S23, S24, S25, S31)

**Step-by-step:**

1. In `apps/orders/models.py`, create `OrderStatus` TextChoices and the `Order` model:
   - All fields as specified in Section 4.4.
   - Implement `transition_status()` method enforcing valid transitions.
   - Add `total` property aggregating OrderItems.
   - Add `db_index=True` on `created_at`.
   - Implement `__str__`.
2. Create the `OrderItem` model:
   - All fields as specified in Section 4.4.
   - `subtotal` property.
3. Run `uv run python manage.py makemigrations orders`.
4. Run `uv run python manage.py migrate`.
5. Create `apps/orders/services.py` with:
   - `checkout(user)`: full checkout flow as specified in Section 7.
     Uses `transaction.atomic()`, calls `decrement_stock()` from products.services,
     creates OrderItems with `bulk_create()`, computes total, closes cart.
   - `confirm_order(user, order_id)`: transitions pending -> confirmed.
   - `cancel_order(user, order_id)`: transitions pending -> cancelled, restores stock.
     Enforces 30-minute cancellation window.
6. Create `apps/orders/views.py` with all views:
   - `checkout_view`: POST, `@buyer_required`, `@csrf_exempt`. Calls checkout service.
   - `order_detail_view`: GET, `@buyer_required`. Returns order with items.
     Only order owner can view.
   - `order_list_view`: GET, `@buyer_required`. Returns buyer's orders, paginated.
   - `confirm_order_view`: POST, `@buyer_required`, `@csrf_exempt`.
   - `cancel_order_view`: POST, `@buyer_required`, `@csrf_exempt`.
   - `seller_orders_view`: GET, `@seller_required`. Orders containing seller's products.
   - `seller_fulfil_view`: POST, `@seller_required`, `@csrf_exempt`. Marks OrderItem fulfilled.
   - `order_summary_view`: GET, `@seller_required`. Aggregation by date range
     using `TruncDate` and `annotate`.
7. Create `apps/orders/urls.py` with `app_name = 'orders'` and all order URL patterns.
8. Verify: checkout flow works end-to-end using Django shell.

**Checkpoint:** Full order lifecycle works. Buyer can checkout, confirm, cancel. Seller can
view orders and mark items fulfilled. **This is the critical milestone: the project should
be fully functional at this point.**

### Phase 4: Admin, Factories, Edge Cases (Tasks: S18, S19, S21, S26, S27, S28, S34)

**Step-by-step:**

1. Create `apps/cart/admin.py` and `apps/orders/admin.py` with full admin config as
   specified in Section 13. CartItem as inline on Cart, OrderItem as inline on Order.
2. Create `apps/cart/factories.py` with `CartFactory`, `CartItemFactory`.
3. Create `apps/orders/factories.py` with `OrderFactory`, `OrderItemFactory`.
4. Implement the 30-minute cancellation window in `cancel_order` service (S26).
5. Implement fulfilment_status update in `seller_fulfil_view` (S27).
6. Implement order summary aggregation view (S28).
7. Verify all admin inlines and list views work in the Django admin panel.

**Checkpoint:** All edge cases handled. Admin panel fully configured. Factories ready.

### Phase 5: Testing and Integration (Tasks: S8, S11, S29, S32, S33)

**Step-by-step:**

1. Create `apps/cart/tests/` with `test_models.py`, `test_views.py`.
2. Create `apps/orders/tests/` with `test_models.py`, `test_views.py`, `test_checkout.py`.
3. Write cart tests: add item, add duplicate (increments), remove, update quantity,
   clear, view contents, stock validation flag, prevent duplicate carts, subtotal.
4. Write order tests: checkout (success, empty cart, insufficient stock), confirm,
   cancel (within window, after window, already confirmed), status transitions,
   order detail (owner vs non-owner), buyer order list, seller orders, fulfilment,
   order summary aggregation.
5. Write integration tests in `tests/`:
   - `test_purchase_flow.py` (S32): create cart, add items, checkout, confirm, verify stock.
   - `test_cancel_restock.py` (S33): create order, cancel, verify stock restored.
6. Run `uv run pytest --cov=apps --cov-report=term-missing`. Target >80% per app.

**Checkpoint:** All tests pass. Coverage target met. Project is complete.

---

## PHASE DEPENDENCY SUMMARY

```
Diogo Phase 1  (Project skeleton)
    |
    v
Diogo Phase 2  (User model + auth)
    |
    +-----------------------------+
    |                             |
    v                             v
Cleber Phase 2                 Sabrina waits...
(Product models)                  |
    |                             |
    v                             |
Cleber Phase 3                    |
(Product CRUD views)              |
    |                             |
    +-----------------------------+
    |
    v
Sabrina Phase 2  (Cart models + views)
    |
    v
Sabrina Phase 3  (Order models + checkout)
    |
    v
ALL: Phase 4+5 in parallel (admin, tests, docs, integration)
```

### Runnable Checkpoints

| After | What you can test |
|---|---|
| Diogo Phase 2 | `manage.py createsuperuser`, login/register via curl, admin panel |
| Cleber Phase 3 | Create products via curl, browse product list, search, filter by category |
| Sabrina Phase 3 | **Full purchase flow**: register buyer, add to cart, checkout, confirm order |
| All Phase 5 | Run `uv run pytest --cov=apps` and see >80% coverage across all apps |

### Quick Test Commands at Each Checkpoint

```bash
# After Diogo Phase 2:
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
# Open http://localhost:8000/admin/ and verify User model appears
# Test registration:
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testbuyer","email":"buyer@test.com","password":"securepass123","role":"buyer"}'

# After Cleber Phase 3:
# Login as seller first, then:
curl -X POST http://localhost:8000/api/products/create/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=<your_session_id>" \
  -d '{"name":"Test Product","description":"A test","price":"19.99","stock":50,"category_id":1}'
# Browse products:
curl http://localhost:8000/api/products/

# After Sabrina Phase 3:
# Login as buyer, then full flow:
curl -X POST http://localhost:8000/api/cart/add/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=<your_session_id>" \
  -d '{"product_id":1,"quantity":2}'
curl -X POST http://localhost:8000/api/orders/checkout/ \
  -H "Cookie: sessionid=<your_session_id>"
```

---

## 19. Common Mistakes to Avoid

1. **Do NOT run makemigrations before AUTH_USER_MODEL is set.** Diogo must set
   `AUTH_USER_MODEL = 'users.User'` in settings BEFORE the first migration.
2. **Do NOT use `FloatField` for money.** Always `DecimalField`.
3. **Do NOT put business logic in views.** Views parse input and call services.
4. **Do NOT forget `@csrf_exempt`** on POST/PUT/DELETE views.
5. **Do NOT use `get()` without handling `DoesNotExist`.** Use `get_object_or_404` or
   try/except.
6. **Do NOT forget `select_related` / `prefetch_related`** on querysets that cross
   foreign keys. Avoid N+1 queries.
7. **Do NOT hardcode config values.** Use `os.environ.get()` or settings constants.
8. **Do NOT skip `transaction.atomic()`** in the checkout flow. Stock decrements and
   order creation must be atomic.
9. **Do NOT allow negative stock.** The `decrement_stock()` function must check
   `stock__gte=quantity` in the filter.
10. **Do NOT forget the `app_name`** in each app's `urls.py` for namespace resolution.
