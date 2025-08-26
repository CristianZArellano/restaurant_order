# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django-based restaurant ordering system called `restaurant_orderV2`. The application manages restaurants, user accounts, and food orders with a complete order lifecycle management system.

## Commands

### Development Commands
```bash
# Navigate to Django project root
cd restaurant_management/

# Run development server
python manage.py runserver

# Make migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser

# Open Django shell
python manage.py shell

# Run tests
python manage.py test

# Collect static files (if needed)
python manage.py collectstatic
```

## Architecture

### Project Structure
```
restaurant_management/          # Main Django project directory
├── manage.py                  # Django management script
├── restaurant_management/     # Django settings package
│   ├── settings.py           # Main settings (Spanish locale, Bogotá timezone)
│   ├── urls.py              # Root URL configuration
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
├── users/                    # User management app
├── restaurants/              # Restaurant management app
├── orders/                   # Order management app
└── db.sqlite3               # SQLite database file
```

### Applications Architecture

#### Users App
- **Model**: `CustomUser` extends Django's `AbstractUser`
- **Features**: Phone validation, verification status, timestamps
- **Custom user model**: `AUTH_USER_MODEL = "users.CustomUser"`

#### Restaurants App  
- **Model**: `Restaurant`
- **Features**: Auto-generated slugs, owner relationship with users, location/contact info
- **Signals**: Welcome emails on creation, pre-deletion cleanup

#### Orders App
- **Models**: `MenuItem`, `Order`, `OrderItem`, `OrderStatusHistory`, `Review`
- **Features**: 
  - Complete order lifecycle (PENDING → DELIVERED)
  - Automatic order number generation with UUID
  - Tax calculation (8% default)
  - Delivery fee management
  - Order total auto-calculation
- **Signals**: Status change tracking, email notifications, automatic total recalculation

### Key Model Relationships
- `Restaurant.owner` → `CustomUser` (ForeignKey)
- `MenuItem.restaurant` → `Restaurant` (ForeignKey)  
- `Order.user` → `CustomUser` (ForeignKey)
- `Order.restaurant` → `Restaurant` (ForeignKey)
- `OrderItem.order` → `Order` (ForeignKey)
- `OrderItem.menu_item` → `MenuItem` (ForeignKey)
- `Review.order` → `Order` (OneToOneField)

### Signal System
The application uses Django signals extensively:
- **Order signals**: Status change tracking, email notifications, delivery time estimation
- **OrderItem signals**: Automatic total recalculation on item changes
- **Restaurant signals**: Welcome emails, cleanup on deletion
- **User signals**: Welcome emails on account creation

### Settings Configuration
- **Database**: SQLite (`db.sqlite3`)
- **Language**: Spanish (`es`)
- **Timezone**: `America/Bogota`
- **Installed Apps**: DRF ready with `rest_framework` included
- **Security**: Development secret key (needs change for production)

### Email Integration
Email notifications are configured throughout the system:
- Order confirmations
- Status updates  
- Welcome messages
- Restaurant notifications

Set `DEFAULT_FROM_EMAIL` in settings for email functionality.

### Important Implementation Details
- Order numbers use UUID format: `ORD-{8-char-hex}`
- Automatic slug generation for restaurants with collision handling
- Phone number validation with international format support
- Order total calculation includes subtotal + tax (8%) + delivery fee
- Menu items are categorized (APPETIZER, MAIN, DESSERT, DRINK, SIDE)
- Order status workflow: PENDING → CONFIRMED → PREPARING → READY → OUT_FOR_DELIVERY → DELIVERED