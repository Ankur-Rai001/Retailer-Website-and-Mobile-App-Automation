# ShopSwift India - Live Preview & Demo Guide

## 🔗 Live Preview URL
**https://retail-connect-40.preview.emergentagent.com**

---

## 🎯 Quick Access Demo Accounts

### Method 1: Easy Demo Login (Recommended)
Visit: **https://retail-connect-40.preview.emergentagent.com/demo-login**

Click on either:
- **"Login as Retailer"** - Full store management experience
- **"Login as Admin"** - Platform admin features (dashboard coming soon)

### Method 2: Direct Credentials

#### 🏪 Demo Retailer Account
```
Email: demo.retailer@shopswift.in
Name: Demo Retailer
Session Token: demo_session_retailer_12345678901234567890
Role: Store Owner/Retailer
```

**What you can test:**
- ✅ AI-powered store creation with GPT-5.2
- ✅ Product management (add, edit, delete)
- ✅ Order management
- ✅ Analytics dashboard
- ✅ Store settings & customization
- ✅ Template selection
- ✅ ONDC integration toggle

#### 🛡️ Demo Admin Account
```
Email: demo.admin@shopswift.in
Name: Demo Admin
Session Token: demo_session_admin_12345678901234567890
Role: Platform Administrator
```

**What you can test:**
- ⏳ Admin dashboard (coming in Phase 2)
- ⏳ Platform-wide analytics
- ⏳ Manage all retailers
- ⏳ Subscription management

---

## 📋 Testing Checklist

### 1. Landing Page
- [x] Visit homepage: https://retail-connect-40.preview.emergentagent.com
- [x] Click "Try Demo" button (top right)
- [x] Verify design: Eczar font headings, Digital Saffron (#F97316) color
- [x] Check "Zero Transaction Fees" messaging is prominent

### 2. Demo Login
- [x] Click "Login as Retailer"
- [x] Should redirect to Dashboard or Store Setup

### 3. Store Creation (If no store exists)
- [x] Fill store name: "Demo Kirana Store"
- [x] Select category: "Grocery & Kirana Store"
- [x] Add phone, address, GST number (optional)
- [x] Click "Create My Store"
- [x] **AI Feature**: Watch for auto-generated store description using GPT-5.2
- [x] Verify subdomain created: `demokiranastore.shopswift.in`

### 4. Dashboard
- [x] View analytics cards (Products, Orders, Revenue, Pending)
- [x] Check Quick Actions section
- [x] Verify store info card shows subdomain

### 5. Products Page
- [x] Click "Add Product" button
- [x] Add product:
  - Name: "Tata Salt 1kg"
  - Price: 22.50
  - Stock: 150
  - Category: "groceries"
- [x] Verify product appears in list
- [x] Test Edit product
- [x] Test Delete product (with confirmation)
- [x] Check stock status colors (green > 10, orange ≤ 10, red = 0)

### 6. Orders Page
- [x] View orders list (empty initially)
- [x] Test order status updates (pending → processing → completed)

### 7. Analytics Page
- [x] View business overview metrics
- [x] Check growth tips section

### 8. Settings Page
- [x] Update store name
- [x] Change store description
- [x] View subdomain (read-only)
- [x] Add custom domain
- [x] Switch template
- [x] Toggle ONDC integration
- [x] Change language (English/Hindi)
- [x] Save settings

### 9. Logout
- [x] Click logout button (top right)
- [x] Should redirect to demo login or home

---

## 🧪 API Testing (For Developers)

### Base URL
```
https://retail-connect-40.preview.emergentagent.com/api
```

### Test Endpoints

#### 1. Health Check
```bash
curl https://retail-connect-40.preview.emergentagent.com/api/
```
Expected: `{"message": "ShopSwift India API", "status": "running"}`

#### 2. Get Templates
```bash
curl https://retail-connect-40.preview.emergentagent.com/api/templates
```
Expected: Array of 4 templates

#### 3. Authenticated Requests (Use Demo Token)
```bash
# Get current user
curl -H "Authorization: Bearer demo_session_retailer_12345678901234567890" \
  https://retail-connect-40.preview.emergentagent.com/api/auth/me

# Get store
curl -H "Authorization: Bearer demo_session_retailer_12345678901234567890" \
  https://retail-connect-40.preview.emergentagent.com/api/stores/my-store

# Get products
curl -H "Authorization: Bearer demo_session_retailer_12345678901234567890" \
  https://retail-connect-40.preview.emergentagent.com/api/products

# Get analytics
curl -H "Authorization: Bearer demo_session_retailer_12345678901234567890" \
  https://retail-connect-40.preview.emergentagent.com/api/analytics/overview
```

#### 4. Create Product
```bash
curl -X POST https://retail-connect-40.preview.emergentagent.com/api/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer demo_session_retailer_12345678901234567890" \
  -d '{
    "name": "Amul Milk 1L",
    "description": "Fresh full cream milk",
    "price": 66.00,
    "stock": 50,
    "category": "dairy"
  }'
```

---

## 🎨 Design Verification

### Colors
- Primary (Digital Saffron): #F97316 ✅
- Secondary (Ledger Ink): #0F172A ✅
- Accent (Growth Green): #10B981 ✅
- Background: #F8FAFC ✅

### Typography
- Headings: Eczar (serif) ✅
- Body: Manrope (sans-serif) ✅
- Mono: JetBrains Mono ✅

### Components
- Buttons: Rounded-full, shadow-lg ✅
- Cards: Rounded-xl, border-slate-200 ✅
- Inputs: Rounded-lg, h-12 ✅

---

## 🐛 Known Issues / Limitations

### Current Limitations
1. **Payment Simulation**: Razorpay is in test mode
   - Live keys pending from user
   - Test cards work in sandbox
   
2. **Phone OTP**: Twilio integration ready
   - Credentials pending from user
   - Can be tested once keys provided

3. **Image Upload**: URL input only
   - Cloud storage (S3/Cloudinary) integration in Phase 2
   
4. **Mobile App**: PWA ready
   - Flutter export coming in Phase 2
   
5. **ONDC**: Toggle available
   - Full Beckn protocol implementation in Phase 2

6. **Regional Languages**: UI supports Hindi selection
   - Full translation in Phase 2

### Fixed Issues
✅ Subdomain generation works correctly
✅ AI description generation using GPT-5.2 works
✅ Multi-tenant data isolation verified
✅ Session management secure (httpOnly cookies)
✅ All CRUD operations functional

---

## 🚀 Real Account Testing

### Create Your Own Store
1. Visit: https://retail-connect-40.preview.emergentagent.com
2. Click "Get Started Free"
3. Sign in with Google (Emergent OAuth)
4. Complete store creation wizard
5. Start adding products!

**Note**: Real accounts create actual stores with unique subdomains and full data isolation.

---

## 💡 Testing Tips

1. **Clear Demo Data**: 
   - Logout and login again for fresh session
   - Each demo session is isolated

2. **Test AI Features**:
   - Create stores with different names/categories
   - Watch AI generate unique descriptions

3. **Test Multi-tenancy**:
   - Use both demo accounts
   - Verify data isolation (retailer can't see admin data)

4. **Mobile Testing**:
   - Open on mobile device
   - Responsive design works on all screen sizes

5. **Browser Testing**:
   - Chrome, Firefox, Safari, Edge all supported
   - Best experience on Chrome

---

## 📞 Support & Issues

For bugs or feature requests:
- Check browser console for errors (F12)
- Note the URL and steps to reproduce
- Provide screenshots if possible

---

## 🎉 What Makes ShopSwift India Special

1. **Zero Transaction Fees** - Keep 100% of profits
2. **AI-Powered** - GPT-5.2 generates store content
3. **One-Click Setup** - Store ready in under 2 minutes
4. **India-First** - GST, UPI, regional languages, ONDC
5. **Multi-tenant** - Secure data isolation
6. **Beautiful Design** - Professional, trust-building UI
7. **Affordable** - ₹99-299/month (vs competitors at ₹2000+)

**Target**: 10-15 million small Indian retailers going digital!

---

Last Updated: January 22, 2025
Platform Status: ✅ MVP Complete & Functional
