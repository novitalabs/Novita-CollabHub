# E-Commerce Platform

A fully-featured online shopping platform built with Hono + Cloudflare Pages + D1 Database.

## Project Overview

- **Name**: CloudShop (E-commerce Platform)
- **Goal**: Provide a complete online shopping experience, including user registration, product browsing, cart management, and order processing
- **Tech Stack**: Hono, Cloudflare Pages, D1 Database, Tailwind CSS, Axios

## Live Access

- **Production**: https://webapp-ekl.pages.dev
- **Deployment URL**: https://3b40209c.webapp-ekl.pages.dev
- **Development**: https://3000-ii3o62k5yqp3wileofp91-82b888ba.sandbox.novita.ai

## Core Features

### Completed

1. **User Authentication**
   - User registration (email, password, username, phone, address)
   - User login (email/password verification)
   - User profile management
   - Session persistence (LocalStorage)

2. **Product Management**
   - Product listing
   - Category filtering
   - Product search
   - Product detail view
   - Real-time stock display

3. **Shopping Cart**
   - Add products to cart
   - Real-time cart count update
   - Adjust item quantities
   - Remove cart items
   - Cart total calculation

4. **Order System**
   - Create orders (from cart)
   - Order list view
   - Order detail display
   - Order status tracking
   - Automatic stock deduction

### Planned

1. **Payment Integration**
   - Third-party payment APIs (WeChat Pay, Alipay)
   - Payment status callback handling

2. **Order Management Enhancements**
   - Order cancellation
   - Refund processing
   - Shipping tracking

3. **Admin Dashboard**
   - Admin login
   - Product CRUD operations
   - Order management interface

4. **UX Improvements**
   - Product review system
   - Wishlist functionality
   - Coupon system
   - User address management

## API Documentation

### Auth API

#### 1. User Registration
- **Path**: `POST /api/auth/register`
- **Parameters**: 
  ```json
  {
    "email": "user@example.com",
    "password": "password123",
    "username": "username",
    "phone": "13800138000",
    "address": "Beijing, Chaoyang District"
  }
  ```
- **Response**: 
  ```json
  {
    "success": true,
    "message": "Registration successful",
    "userId": 1
  }
  ```

#### 2. User Login
- **Path**: `POST /api/auth/login`
- **Parameters**: 
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Response**: 
  ```json
  {
    "success": true,
    "message": "Login successful",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "username": "username",
      "phone": "13800138000",
      "address": "Beijing, Chaoyang District"
    }
  }
  ```

#### 3. Get User Info
- **Path**: `GET /api/auth/user/:id`
- **Response**: 
  ```json
  {
    "success": true,
    "user": { ... }
  }
  ```

### Products API

#### 4. Get Product List
- **Path**: `GET /api/products`
- **Query Parameters**: `category` (optional)
- **Example**: `GET /api/products?category=Phones%20%26%20Electronics`
- **Response**: 
  ```json
  {
    "success": true,
    "products": [
      {
        "id": 1,
        "name": "iPhone 15 Pro",
        "description": "Latest Apple flagship phone...",
        "price": 999.00,
        "stock": 50,
        "category": "Phones & Electronics",
        "image_url": "https://..."
      }
    ]
  }
  ```

#### 5. Get Product Detail
- **Path**: `GET /api/products/:id`
- **Response**: 
  ```json
  {
    "success": true,
    "product": { ... }
  }
  ```

#### 6. Get Product Categories
- **Path**: `GET /api/categories`
- **Response**: 
  ```json
  {
    "success": true,
    "categories": [
      {"category": "Phones & Electronics"},
      {"category": "Computers & Office"}
    ]
  }
  ```

### Cart API

#### 7. Get Cart
- **Path**: `GET /api/cart/:userId`
- **Response**: 
  ```json
  {
    "success": true,
    "cartItems": [
      {
        "id": 1,
        "product_id": 1,
        "quantity": 2,
        "name": "iPhone 15 Pro",
        "price": 999.00,
        "image_url": "https://...",
        "stock": 50
      }
    ]
  }
  ```

#### 8. Add to Cart
- **Path**: `POST /api/cart`
- **Parameters**: 
  ```json
  {
    "userId": 1,
    "productId": 1,
    "quantity": 1
  }
  ```
- **Response**: 
  ```json
  {
    "success": true,
    "message": "Added to cart"
  }
  ```

#### 9. Update Cart Item Quantity
- **Path**: `PUT /api/cart/:id`
- **Parameters**: 
  ```json
  {
    "quantity": 3
  }
  ```

#### 10. Remove Cart Item
- **Path**: `DELETE /api/cart/:id`

### Orders API

#### 11. Create Order
- **Path**: `POST /api/orders`
- **Parameters**: 
  ```json
  {
    "userId": 1,
    "shippingAddress": "123 Main St, Beijing",
    "phone": "13800138000"
  }
  ```
- **Response**: 
  ```json
  {
    "success": true,
    "message": "Order created successfully",
    "orderId": 1,
    "totalAmount": 1998.00
  }
  ```

#### 12. Get User Orders
- **Path**: `GET /api/orders/user/:userId`
- **Response**: 
  ```json
  {
    "success": true,
    "orders": [
      {
        "id": 1,
        "user_id": 1,
        "total_amount": 1998.00,
        "status": "pending",
        "shipping_address": "123 Main St, Beijing",
        "phone": "13800138000",
        "created_at": "2024-01-15 10:30:00"
      }
    ]
  }
  ```

#### 13. Get Order Detail
- **Path**: `GET /api/orders/:orderId`
- **Response**: 
  ```json
  {
    "success": true,
    "order": {
      "id": 1,
      "user_id": 1,
      "total_amount": 1998.00,
      "status": "pending",
      "items": [
        {
          "id": 1,
          "product_id": 1,
          "product_name": "iPhone 15 Pro",
          "price": 999.00,
          "quantity": 2,
          "subtotal": 1998.00
        }
      ]
    }
  }
  ```

## Data Architecture

### Data Models

1. **users**
   - id: Primary key
   - email: Email (unique)
   - password_hash: Password hash
   - username: Username
   - phone: Phone number
   - address: Address
   - created_at: Created timestamp

2. **products**
   - id: Primary key
   - name: Product name
   - description: Product description
   - price: Price
   - stock: Stock quantity
   - category: Category
   - image_url: Image URL
   - created_at: Created timestamp

3. **cart_items**
   - id: Primary key
   - user_id: User ID (foreign key)
   - product_id: Product ID (foreign key)
   - quantity: Quantity
   - created_at: Created timestamp

4. **orders**
   - id: Primary key
   - user_id: User ID (foreign key)
   - total_amount: Total amount
   - status: Order status (pending/paid/shipped/completed/cancelled)
   - shipping_address: Shipping address
   - phone: Contact phone
   - created_at: Created timestamp

5. **order_items**
   - id: Primary key
   - order_id: Order ID (foreign key)
   - product_id: Product ID (foreign key)
   - product_name: Product name
   - price: Unit price
   - quantity: Quantity
   - subtotal: Subtotal

### Storage

- **Database**: Cloudflare D1 (SQLite)
- **Development**: Local SQLite (`.wrangler/state/v3/d1`)
- **Production**: Cloudflare D1 globally distributed database

### Data Flow

1. **User Registration/Login**: User info stored in users table, passwords encoded with base64 (production should use bcrypt)
2. **Product Browsing**: Data read from products table, supports category filtering
3. **Shopping Cart**: cart_items table links users and products, supports quantity modification
4. **Order Creation**: 
   - Create orders record
   - Create multiple order_items records
   - Update products stock
   - Clear cart

## User Guide

### Accessing the Website

1. Open browser and navigate to: https://3000-ii3o62k5yqp3wileofp91-82b888ba.sandbox.novita.ai

### User Workflow

1. **Register an Account**
   - Click the "Register" button in the top-right corner
   - Fill in email, password, username, and other info
   - Submit registration

2. **Login**
   - Click the "Login" button
   - Enter your registered email and password
   - After successful login, username and cart icon will be displayed

3. **Browse Products**
   - Homepage shows all products
   - Use category buttons to filter by category
   - Use the search box to find specific products

4. **Add to Cart**
   - Click the "Add to Cart" button on a product card
   - Cart icon shows the item count

5. **Manage Cart**
   - Click the cart icon to view your cart
   - Adjust item quantities (+/- buttons)
   - Remove unwanted items
   - View total amount

6. **Create an Order**
   - Click "Checkout" on the cart page
   - Confirm or enter shipping address and phone number
   - Submit order
   - View order number and total

7. **View Orders**
   - Click the "Orders" button to view all orders
   - Check order status and details
   - Click "View Details" to see item breakdown

### Test Account

- **Email**: demo@example.com
- **Password**: demo123
- **Username**: DemoUser

## Local Development

### Requirements

- Node.js 18+
- npm or pnpm

### Install Dependencies

```bash
cd /home/user/webapp
npm install
```

### Initialize Database

```bash
# Apply database migrations
npm run db:migrate:local

# Insert sample data
npm run db:seed
```

### Start Development Server

```bash
# Build the project
npm run build

# Start with PM2
pm2 start ecosystem.config.cjs

# Or use wrangler directly
npm run dev:sandbox
```

### Access Local Service

- Local URL: http://localhost:3000

### Database Management

```bash
# Reset database
npm run db:reset

# Execute SQL commands
npm run db:console:local
```

## Deployment

### Deployment Platform

- **Cloudflare Pages** - Static assets and edge functions
- **Cloudflare D1** - Globally distributed database

### Deployment Status

- Local development environment running normally
- Deployed to Cloudflare Pages
- Production environment requires manual D1 database configuration (due to API token permission limitations)

### Current Deployment Info

- **Project Name**: webapp
- **Main Domain**: https://webapp-ekl.pages.dev
- **Deployment ID**: https://3b40209c.webapp-ekl.pages.dev
- **Status**: Frontend pages working, backend API pending database configuration

### Full Deployment Steps (requires Cloudflare Dashboard)

#### Step 1: Create D1 Database

Since the API token lacks D1 database permissions, manual creation in Cloudflare Dashboard is required:

1. Visit [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Navigate to **Workers & Pages** > **D1 SQL Database** in the left menu
3. Click the **Create database** button
4. Enter database name: `webapp-production`
5. Click **Create** to create the database
6. After creation, copy the database ID (format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

#### Step 2: Bind D1 Database to Pages Project

1. In Cloudflare Dashboard, go to **Workers & Pages**
2. Find and click the **webapp** project
3. Go to the **Settings** tab
4. Find the **Functions** section, click **D1 database bindings**
5. Click **Add binding**:
   - Variable name: `DB`
   - D1 database: Select `webapp-production`
6. Click **Save**

#### Step 3: Apply Database Migrations

Run in local terminal (requires API token with D1 permissions):

```bash
# Method 1: Using wrangler CLI (recommended)
npx wrangler d1 migrations apply webapp-production --remote

# Method 2: Manual SQL execution
# In the Cloudflare Dashboard D1 database page, use the Console to execute the SQL in migrations/0001_initial_schema.sql
# Then execute seed.sql to insert sample data
```

#### Step 4: Update wrangler.jsonc Configuration

Add the database ID to the config file:

```jsonc
{
  "$schema": "node_modules/wrangler/config-schema.json",
  "name": "webapp",
  "compatibility_date": "2025-12-02",
  "pages_build_output_dir": "./dist",
  "compatibility_flags": [
    "nodejs_compat"
  ],
  "d1_databases": [
    {
      "binding": "DB",
      "database_name": "webapp-production",
      "database_id": "your-database-id"
    }
  ]
}
```

#### Step 5: Redeploy

```bash
# Rebuild and deploy
npm run build
npx wrangler pages deploy dist --project-name webapp
```

### Quick Deploy (with full local permissions)

```bash
# One-click deploy (requires full Cloudflare API permissions)
npm run deploy:prod
```

## Project Structure

```
webapp/
├── src/
│   ├── index.tsx          # Main app entry, contains all API routes and HTML
│   └── renderer.tsx       # Renderer configuration
├── public/
│   └── static/
│       ├── app.js         # Frontend JavaScript logic
│       └── style.css      # Custom styles
├── migrations/
│   └── 0001_initial_schema.sql  # Database schema
├── seed.sql               # Sample data
├── ecosystem.config.cjs   # PM2 configuration
├── wrangler.jsonc         # Cloudflare configuration
├── package.json           # Project dependencies and scripts
└── README.md              # Project documentation
```

## Technical Highlights

1. **Edge Computing**: Runs on Cloudflare Workers at global edge nodes
2. **Lightweight Framework**: Hono provides fast routing and middleware support
3. **Serverless Database**: D1 provides globally distributed SQLite database
4. **Responsive Design**: Tailwind CSS for mobile-friendly interface
5. **Frontend-Backend Separation**: RESTful API architecture, easy to extend

## Development Recommendations

### Next Steps

1. **Security Enhancements**
   - Use bcrypt for password hashing
   - Implement JWT token authentication
   - Add CSRF protection

2. **Performance Optimization**
   - Add lazy loading for product images
   - Implement API response caching
   - Optimize database queries

3. **Feature Expansion**
   - Integrate payment APIs
   - Add product review system
   - Build admin dashboard

4. **User Experience**
   - Add loading animations
   - Improve error messages
   - Implement form validation

## License

MIT License

## Last Updated

2024-12-02
