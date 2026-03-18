import { serve } from '@hono/node-server'
import { serveStatic } from '@hono/node-server/serve-static'
import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { pool, query } from './db.js'
import 'dotenv/config'

const app = new Hono()

// Enable CORS
app.use('/api/*', cors())

// Serve static files
app.use('/static/*', serveStatic({ root: './public' }))

// ============= Auth API =============

// User registration
app.post('/api/auth/register', async (c) => {
  try {
    const { email, password, username, phone, address } = await c.req.json()
    
    if (!email || !password || !username) {
      return c.json({ success: false, message: 'Email, password and username are required' }, 400)
    }
    
    // Simple password hash (use bcrypt in production)
    const passwordHash = Buffer.from(password).toString('base64')
    
    const result = await query(
      `INSERT INTO users (email, password_hash, username, phone, address) 
       VALUES ($1, $2, $3, $4, $5) RETURNING id`,
      [email, passwordHash, username, phone || '', address || '']
    )
    
    return c.json({ 
      success: true, 
      message: 'Registration successful',
      userId: result.rows[0].id 
    })
  } catch (error: unknown) {
    const err = error as Error & { code?: string }
    if (err.code === '23505') { // PostgreSQL unique violation
      return c.json({ success: false, message: 'This email is already registered' }, 400)
    }
    return c.json({ success: false, message: 'Registration failed: ' + err.message }, 500)
  }
})

// User login
app.post('/api/auth/login', async (c) => {
  try {
    const { email, password } = await c.req.json()
    
    if (!email || !password) {
      return c.json({ success: false, message: 'Email and password are required' }, 400)
    }
    
    const passwordHash = Buffer.from(password).toString('base64')
    
    const result = await query(
      `SELECT id, email, username, phone, address FROM users 
       WHERE email = $1 AND password_hash = $2`,
      [email, passwordHash]
    )
    
    if (result.rows.length === 0) {
      return c.json({ success: false, message: 'Invalid email or password' }, 401)
    }
    
    return c.json({ 
      success: true, 
      message: 'Login successful',
      user: result.rows[0]
    })
  } catch (error: unknown) {
    const err = error as Error
    return c.json({ success: false, message: 'Login failed: ' + err.message }, 500)
  }
})

// Get user info
app.get('/api/auth/user/:id', async (c) => {
  try {
    const userId = c.req.param('id')
    
    const result = await query(
      `SELECT id, email, username, phone, address, created_at FROM users WHERE id = $1`,
      [userId]
    )
    
    if (result.rows.length === 0) {
      return c.json({ success: false, message: 'User not found' }, 404)
    }
    
    return c.json({ success: true, user: result.rows[0] })
  } catch (error: unknown) {
    const err = error as Error
    return c.json({ success: false, message: 'Failed to get user info: ' + err.message }, 500)
  }
})

// ============= Products API =============

// Get product list
app.get('/api/products', async (c) => {
  try {
    const category = c.req.query('category')
    
    let queryText = 'SELECT * FROM products WHERE stock > 0'
    const params: string[] = []
    
    if (category) {
      queryText += ' AND category = $1'
      params.push(category)
    }
    
    queryText += ' ORDER BY created_at DESC'
    
    const result = await query(queryText, params)
    
    return c.json({ success: true, products: result.rows })
  } catch (error: unknown) {
    const err = error as Error
    return c.json({ success: false, message: 'Failed to get product list: ' + err.message }, 500)
  }
})

// Get product details
app.get('/api/products/:id', async (c) => {
  try {
    const productId = c.req.param('id')
    
    const result = await query(
      `SELECT * FROM products WHERE id = $1`,
      [productId]
    )
    
    if (result.rows.length === 0) {
      return c.json({ success: false, message: 'Product not found' }, 404)
    }
    
    return c.json({ success: true, product: result.rows[0] })
  } catch (error: unknown) {
    const err = error as Error
    return c.json({ success: false, message: 'Failed to get product details: ' + err.message }, 500)
  }
})

// Get product categories
app.get('/api/categories', async (c) => {
  try {
    const result = await query(
      `SELECT DISTINCT category FROM products WHERE category IS NOT NULL`
    )
    
    return c.json({ success: true, categories: result.rows })
  } catch (error: unknown) {
    const err = error as Error
    return c.json({ success: false, message: 'Failed to get categories: ' + err.message }, 500)
  }
})

// ============= Cart API =============

// Get cart
app.get('/api/cart/:userId', async (c) => {
  try {
    const userId = c.req.param('userId')
    
    const result = await query(
      `SELECT 
        c.id, c.product_id, c.quantity,
        p.name, p.price, p.image_url, p.stock
      FROM cart_items c
      JOIN products p ON c.product_id = p.id
      WHERE c.user_id = $1`,
      [userId]
    )
    
    return c.json({ success: true, cartItems: result.rows })
  } catch (error: unknown) {
    const err = error as Error
    return c.json({ success: false, message: 'Failed to get cart: ' + err.message }, 500)
  }
})

// Add to cart
app.post('/api/cart', async (c) => {
  try {
    const { userId, productId, quantity } = await c.req.json()
    
    if (!userId || !productId || !quantity) {
      return c.json({ success: false, message: 'Missing required parameters' }, 400)
    }
    
    // Check product stock
    const productResult = await query(
      `SELECT stock FROM products WHERE id = $1`,
      [productId]
    )
    
    if (productResult.rows.length === 0 || productResult.rows[0].stock < quantity) {
      return c.json({ success: false, message: 'Insufficient stock' }, 400)
    }
    
    // Check if product already in cart
    const existingResult = await query(
      `SELECT id, quantity FROM cart_items WHERE user_id = $1 AND product_id = $2`,
      [userId, productId]
    )
    
    if (existingResult.rows.length > 0) {
      // Update quantity
      await query(
        `UPDATE cart_items SET quantity = quantity + $1, updated_at = CURRENT_TIMESTAMP 
         WHERE id = $2`,
        [quantity, existingResult.rows[0].id]
      )
    } else {
      // Insert new
      await query(
        `INSERT INTO cart_items (user_id, product_id, quantity) VALUES ($1, $2, $3)`,
        [userId, productId, quantity]
      )
    }
    
    return c.json({ success: true, message: 'Added to cart' })
  } catch (error: unknown) {
    const err = error as Error
    return c.json({ success: false, message: 'Failed to add: ' + err.message }, 500)
  }
})

// Update cart item quantity
app.put('/api/cart/:id', async (c) => {
  try {
    const cartId = c.req.param('id')
    const { quantity } = await c.req.json()
    
    if (quantity < 1) {
      return c.json({ success: false, message: 'Quantity must be greater than 0' }, 400)
    }
    
    await query(
      `UPDATE cart_items SET quantity = $1, updated_at = CURRENT_TIMESTAMP WHERE id = $2`,
      [quantity, cartId]
    )
    
    return c.json({ success: true, message: 'Updated successfully' })
  } catch (error: unknown) {
    const err = error as Error
    return c.json({ success: false, message: 'Update failed: ' + err.message }, 500)
  }
})

// Remove cart item
app.delete('/api/cart/:id', async (c) => {
  try {
    const cartId = c.req.param('id')
    
    await query(
      `DELETE FROM cart_items WHERE id = $1`,
      [cartId]
    )
    
    return c.json({ success: true, message: 'Deleted successfully' })
  } catch (error: unknown) {
    const err = error as Error
    return c.json({ success: false, message: 'Delete failed: ' + err.message }, 500)
  }
})

// ============= Orders API =============

// Create order
app.post('/api/orders', async (c) => {
  const client = await pool.connect()
  
  try {
    const { userId, shippingAddress, phone } = await c.req.json()
    
    if (!userId || !shippingAddress || !phone) {
      return c.json({ success: false, message: 'Shipping info is incomplete' }, 400)
    }
    
    // Begin transaction
    await client.query('BEGIN')
    
    // Get cart items
    const cartResult = await client.query(
      `SELECT c.*, p.name, p.price, p.stock 
       FROM cart_items c
       JOIN products p ON c.product_id = p.id
       WHERE c.user_id = $1`,
      [userId]
    )
    
    if (cartResult.rows.length === 0) {
      await client.query('ROLLBACK')
      return c.json({ success: false, message: 'Cart is empty' }, 400)
    }
    
    // Calculate total and check stock
    let totalAmount = 0
    for (const item of cartResult.rows) {
      if (item.stock < item.quantity) {
        await client.query('ROLLBACK')
        return c.json({ success: false, message: `${item.name} is out of stock` }, 400)
      }
      totalAmount += item.price * item.quantity
    }
    
    // Create order
    const orderResult = await client.query(
      `INSERT INTO orders (user_id, total_amount, shipping_address, phone)
       VALUES ($1, $2, $3, $4) RETURNING id`,
      [userId, totalAmount, shippingAddress, phone]
    )
    
    const orderId = orderResult.rows[0].id
    
    // Insert order items and update stock
    for (const item of cartResult.rows) {
      await client.query(
        `INSERT INTO order_items (order_id, product_id, product_name, price, quantity, subtotal)
         VALUES ($1, $2, $3, $4, $5, $6)`,
        [orderId, item.product_id, item.name, item.price, item.quantity, item.price * item.quantity]
      )
      
      // Update stock
      await client.query(
        `UPDATE products SET stock = stock - $1 WHERE id = $2`,
        [item.quantity, item.product_id]
      )
    }
    
    // Clear cart
    await client.query(
      `DELETE FROM cart_items WHERE user_id = $1`,
      [userId]
    )
    
    // Commit transaction
    await client.query('COMMIT')
    
    return c.json({ 
      success: true, 
      message: 'Order created successfully',
      orderId,
      totalAmount
    })
  } catch (error: unknown) {
    await client.query('ROLLBACK')
    const err = error as Error
    return c.json({ success: false, message: 'Failed to create order: ' + err.message }, 500)
  } finally {
    client.release()
  }
})

// Get user order list
app.get('/api/orders/user/:userId', async (c) => {
  try {
    const userId = c.req.param('userId')
    
    const result = await query(
      `SELECT * FROM orders WHERE user_id = $1 ORDER BY created_at DESC`,
      [userId]
    )
    
    return c.json({ success: true, orders: result.rows })
  } catch (error: unknown) {
    const err = error as Error
    return c.json({ success: false, message: 'Failed to get order list: ' + err.message }, 500)
  }
})

// Get order details
app.get('/api/orders/:orderId', async (c) => {
  try {
    const orderId = c.req.param('orderId')
    
    const orderResult = await query(
      `SELECT * FROM orders WHERE id = $1`,
      [orderId]
    )
    
    if (orderResult.rows.length === 0) {
      return c.json({ success: false, message: 'Order not found' }, 404)
    }
    
    const itemsResult = await query(
      `SELECT * FROM order_items WHERE order_id = $1`,
      [orderId]
    )
    
    return c.json({ 
      success: true, 
      order: {
        ...orderResult.rows[0],
        items: itemsResult.rows
      }
    })
  } catch (error: unknown) {
    const err = error as Error
    return c.json({ success: false, message: 'Failed to get order details: ' + err.message }, 500)
  }
})

// ============= Home Page HTML =============

app.get('/', (c) => {
  return c.html(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>E-Commerce - Online Shopping Platform</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/css/all.min.css" rel="stylesheet">
    </head>
    <body class="bg-gray-50">
        <!-- Navigation -->
        <nav class="bg-white shadow-lg sticky top-0 z-50">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between h-16">
                    <div class="flex items-center">
                        <i class="fas fa-store text-blue-600 text-2xl mr-3"></i>
                        <span class="text-xl font-bold text-gray-900">CloudShop</span>
                    </div>
                    <div class="flex items-center space-x-4">
                        <div class="relative">
                            <input type="text" id="searchInput" placeholder="Search products..." 
                                   class="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                            <i class="fas fa-search absolute left-3 top-3 text-gray-400"></i>
                        </div>
                        <div id="authButtons" class="flex items-center space-x-3">
                            <button onclick="showLogin()" class="px-4 py-2 text-blue-600 hover:text-blue-700">
                                <i class="fas fa-sign-in-alt mr-1"></i>Login
                            </button>
                            <button onclick="showRegister()" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                                <i class="fas fa-user-plus mr-1"></i>Sign Up
                            </button>
                        </div>
                        <div id="userMenu" class="hidden flex items-center space-x-4">
                            <span id="welcomeText" class="text-gray-700"></span>
                            <button onclick="showCart()" class="relative px-4 py-2 text-gray-700 hover:text-blue-600">
                                <i class="fas fa-shopping-cart text-xl"></i>
                                <span id="cartBadge" class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">0</span>
                            </button>
                            <button onclick="showOrders()" class="px-4 py-2 text-gray-700 hover:text-blue-600">
                                <i class="fas fa-list-alt mr-1"></i>Orders
                            </button>
                            <button onclick="logout()" class="px-4 py-2 text-gray-700 hover:text-red-600">
                                <i class="fas fa-sign-out-alt mr-1"></i>Logout
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </nav>

        <!-- Main Content -->
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <!-- Category Filter -->
            <div id="categoryFilter" class="mb-6 flex flex-wrap gap-2"></div>
            
            <!-- Product List -->
            <div id="productList" class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6"></div>
        </div>

        <!-- Login Modal -->
        <div id="loginModal" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div class="bg-white rounded-lg p-8 max-w-md w-full mx-4">
                <div class="flex justify-between items-center mb-6">
                    <h2 class="text-2xl font-bold">Login</h2>
                    <button onclick="closeModal('loginModal')" class="text-gray-500 hover:text-gray-700">
                        <i class="fas fa-times text-xl"></i>
                    </button>
                </div>
                <form id="loginForm" onsubmit="handleLogin(event)">
                    <div class="mb-4">
                        <label class="block text-gray-700 mb-2">Email</label>
                        <input type="email" name="email" required 
                               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                    </div>
                    <div class="mb-6">
                        <label class="block text-gray-700 mb-2">Password</label>
                        <input type="password" name="password" required 
                               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                    </div>
                    <button type="submit" class="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">
                        Login
                    </button>
                    <p class="mt-4 text-center text-gray-600">
                        Don't have an account? <a href="#" onclick="showRegister(); return false;" class="text-blue-600 hover:underline">Sign up now</a>
                    </p>
                </form>
            </div>
        </div>

        <!-- Register Modal -->
        <div id="registerModal" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div class="bg-white rounded-lg p-8 max-w-md w-full mx-4">
                <div class="flex justify-between items-center mb-6">
                    <h2 class="text-2xl font-bold">Sign Up</h2>
                    <button onclick="closeModal('registerModal')" class="text-gray-500 hover:text-gray-700">
                        <i class="fas fa-times text-xl"></i>
                    </button>
                </div>
                <form id="registerForm" onsubmit="handleRegister(event)">
                    <div class="mb-4">
                        <label class="block text-gray-700 mb-2">Username</label>
                        <input type="text" name="username" required 
                               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                    </div>
                    <div class="mb-4">
                        <label class="block text-gray-700 mb-2">Email</label>
                        <input type="email" name="email" required 
                               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                    </div>
                    <div class="mb-4">
                        <label class="block text-gray-700 mb-2">Password</label>
                        <input type="password" name="password" required minlength="6"
                               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                    </div>
                    <div class="mb-4">
                        <label class="block text-gray-700 mb-2">Phone (optional)</label>
                        <input type="tel" name="phone" 
                               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                    </div>
                    <div class="mb-6">
                        <label class="block text-gray-700 mb-2">Shipping Address (optional)</label>
                        <textarea name="address" rows="2"
                                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"></textarea>
                    </div>
                    <button type="submit" class="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">
                        Sign Up
                    </button>
                    <p class="mt-4 text-center text-gray-600">
                        Already have an account? <a href="#" onclick="showLogin(); return false;" class="text-blue-600 hover:underline">Login now</a>
                    </p>
                </form>
            </div>
        </div>

        <!-- Cart Modal -->
        <div id="cartModal" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div class="bg-white rounded-lg p-8 max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto">
                <div class="flex justify-between items-center mb-6">
                    <h2 class="text-2xl font-bold">Shopping Cart</h2>
                    <button onclick="closeModal('cartModal')" class="text-gray-500 hover:text-gray-700">
                        <i class="fas fa-times text-xl"></i>
                    </button>
                </div>
                <div id="cartContent"></div>
            </div>
        </div>

        <!-- Orders Modal -->
        <div id="ordersModal" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div class="bg-white rounded-lg p-8 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
                <div class="flex justify-between items-center mb-6">
                    <h2 class="text-2xl font-bold">My Orders</h2>
                    <button onclick="closeModal('ordersModal')" class="text-gray-500 hover:text-gray-700">
                        <i class="fas fa-times text-xl"></i>
                    </button>
                </div>
                <div id="ordersContent"></div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/axios@1.6.0/dist/axios.min.js"></script>
        <script src="/static/app.js"></script>
    </body>
    </html>
  `)
})

// Start server
const port = parseInt(process.env.PORT || '3000')

serve({
  fetch: app.fetch,
  port
}, (info) => {
  console.log(`🚀 Server running at http://localhost:${info.port}`)
})
