# ShopSwift India - Product Requirements Document

## Problem Statement
Build a production-ready multi-tenant SaaS platform that allows small Indian retailers to create personalized online stores with one click.

## Target Users
Non-technical small retailers in India (tier-2/3 cities, rural areas)

## Core Architecture
- **Backend:** FastAPI (Python) with modular routers
- **Frontend:** React + Tailwind CSS + Shadcn UI
- **Database:** MongoDB (motor async driver)
- **Real-time:** Socket.io (with REST fallback)
- **Auth:** Emergent Google Auth + Demo login (retailer + admin roles)

## Backend Structure
```
backend/
├── server.py          # Slim entry point (~60 lines)
├── database.py        # MongoDB connection
├── deps.py            # Auth deps (get_current_user, get_admin_user)
├── models/
│   └── schemas.py     # All Pydantic models
├── routers/
│   ├── auth.py        # Auth + demo login + seed (retailer + admin)
│   ├── store.py       # Store CRUD
│   ├── products.py    # Product CRUD
│   ├── orders.py      # Order management
│   ├── templates.py   # Template library
│   ├── analytics.py   # Analytics overview
│   ├── mobile_app.py  # Flutter app generation
│   ├── ondc.py        # ONDC integration + webhooks
│   ├── chat.py        # Chat REST + Socket.io
│   ├── public.py      # Public storefront APIs
│   └── admin.py       # Admin dashboard APIs (metrics, retailers, subscriptions)
└── utils/
    ├── flutter_generator.py
    └── ondc_integration.py
```

## Completed Features
- [x] User authentication (Google Auth + Demo login with role support)
- [x] One-click store creation with AI descriptions (GPT-5.2)
- [x] Retailer dashboard with analytics
- [x] Product catalog CRUD
- [x] Order management
- [x] Template library (free + premium)
- [x] PWA support (offline, installable)
- [x] Mobile app generation (Flutter codebase)
- [x] ONDC integration (KYC, catalog sync, webhooks)
- [x] Real-time customer chat (Socket.io + REST API)
- [x] Backend refactored to modular routers
- [x] Admin Dashboard — platform metrics, retailer management, subscription management
- [x] Role-based access control (admin guard at /api/admin/*)
- [x] Demo seed data (5 sample retailers with varied subscription states)

## In Progress
- [ ] Pricing & Monetization (Razorpay mock → live later)
- [ ] GST invoicing (user requested after monetization)

## Upcoming (P1-P2)
- [ ] Premium template purchase flow
- [ ] Add-on marketing services

## Backlog (P3 - Skipped per user request)
- [ ] Logistics integration
- [ ] Regional language expansion

## Key Admin Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/admin/metrics | GET | Platform-wide metrics |
| /api/admin/retailers | GET | List retailers (search, status, tier filters) |
| /api/admin/retailers/{id} | GET | Retailer detail (products, orders, revenue, KYC) |
| /api/admin/retailers/{id}/subscription | PATCH | Update subscription status/tier |

## Test Reports
- `/app/test_reports/iteration_1.json` - Chat + basic APIs (17/17 pass)
- `/app/test_reports/iteration_2.json` - Admin dashboard (15/15 backend, all frontend pass)
- `/app/backend/tests/test_api.py` - Base API tests
- `/app/backend/tests/test_admin_api.py` - Admin API tests

## Demo Credentials
- **Retailer:** Token `demo_session_retailer_12345678901234567890`, route `/demo-login` → click "Login as Retailer" → `/dashboard`
- **Admin:** Token `demo_session_admin_12345678901234567890`, route `/demo-login` → click "Login as Admin" → `/admin`
- Seeded retailers: Priya Fashions (pro), Ravi Electronics (premium), Anita Fresh Mart (trial), Suresh Kirana (active/pro), Meena Jewellers (premium)

## Mocked APIs
- Demo login: hardcoded accounts
- ONDC: staging environment
- Razorpay: test keys (awaiting live keys)
- Mobile app: generates Flutter code, doesn't compile
