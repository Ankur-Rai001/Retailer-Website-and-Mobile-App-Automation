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
- **Auth:** Emergent Google Auth + Demo login flow

## Backend Structure (Refactored Feb 2026)
```
backend/
├── server.py          # Slim entry point (~50 lines)
├── database.py        # MongoDB connection
├── deps.py            # Auth dependencies
├── models/
│   └── schemas.py     # All Pydantic models
├── routers/
│   ├── auth.py        # Auth + demo login + seed
│   ├── store.py       # Store CRUD
│   ├── products.py    # Product CRUD
│   ├── orders.py      # Order management
│   ├── templates.py   # Template library
│   ├── analytics.py   # Analytics overview
│   ├── mobile_app.py  # Flutter app generation
│   ├── ondc.py        # ONDC integration + webhooks
│   ├── chat.py        # Chat REST + Socket.io
│   └── public.py      # Public storefront APIs
└── utils/
    ├── flutter_generator.py
    └── ondc_integration.py
```

## Completed Features
- [x] User authentication (Google Auth + Demo login)
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
- [x] Demo login with seeded test data

## In Progress
- [ ] Admin Dashboard (manage retailers, subscriptions)
- [ ] Pricing & Monetization (Razorpay mock → live later)
- [ ] GST invoicing (user requested after monetization)

## Upcoming (P1-P2)
- [ ] Premium template purchase flow
- [ ] Add-on marketing services
- [ ] Zero transaction fees messaging in UI (done in chat)

## Backlog (P3 - Skipped per user request)
- [ ] Logistics integration
- [ ] Regional language expansion
- [ ] Full GST-compliant invoicing

## Key Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/auth/demo-login | POST | Demo login with cookie |
| /api/auth/session | POST | Google Auth session |
| /api/auth/me | GET | Current user |
| /api/stores | POST | Create store |
| /api/stores/my-store | GET | Get retailer's store |
| /api/products | GET/POST | Product CRUD |
| /api/orders | GET | Order list |
| /api/chat/send | POST | Send chat message |
| /api/chat/messages/{id} | GET | Get messages |
| /api/chat/conversations/{id} | GET | Get conversations |
| /api/templates | GET | Template library |
| /api/analytics/overview | GET | Dashboard analytics |

## Test Reports
- `/app/test_reports/iteration_1.json` - 100% pass (17/17 backend, all frontend flows)
- `/app/backend/tests/test_api.py` - Pytest test suite

## Mocked APIs
- Demo login: hardcoded accounts (no real Google auth needed for testing)
- ONDC: staging environment
- Razorpay: test keys (awaiting live keys from user)
- Mobile app: generates Flutter code but doesn't compile

## Demo Credentials
- Token: `demo_session_retailer_12345678901234567890`
- Store ID: `store_demo_001`
- Login: `/demo-login` page → "Login as Retailer"
