// Global state
let currentUser = null;
let currentCategory = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Check locally stored user info
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        updateUIAfterLogin();
    }
    
    loadCategories();
    loadProducts();
});

// ============= Authentication =============

function showLogin() {
    closeModal('registerModal');
    document.getElementById('loginModal').classList.remove('hidden');
}

function showRegister() {
    closeModal('loginModal');
    document.getElementById('registerModal').classList.remove('hidden');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

async function handleLogin(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    
    try {
        const response = await axios.post('/api/auth/login', {
            email: formData.get('email'),
            password: formData.get('password')
        });
        
        if (response.data.success) {
            currentUser = response.data.user;
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            updateUIAfterLogin();
            closeModal('loginModal');
            form.reset();
            alert('Login successful!');
            loadCart();
        }
    } catch (error) {
        alert(error.response?.data?.message || 'Login failed, please try again');
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    
    try {
        const response = await axios.post('/api/auth/register', {
            email: formData.get('email'),
            password: formData.get('password'),
            username: formData.get('username'),
            phone: formData.get('phone'),
            address: formData.get('address')
        });
        
        if (response.data.success) {
            alert('Registration successful! Please login');
            closeModal('registerModal');
            form.reset();
            showLogin();
        }
    } catch (error) {
        alert(error.response?.data?.message || 'Registration failed, please try again');
    }
}

function logout() {
    currentUser = null;
    localStorage.removeItem('currentUser');
    document.getElementById('authButtons').classList.remove('hidden');
    document.getElementById('userMenu').classList.add('hidden');
    alert('Logged out');
    loadProducts();
}

function updateUIAfterLogin() {
    document.getElementById('authButtons').classList.add('hidden');
    document.getElementById('userMenu').classList.remove('hidden');
    document.getElementById('welcomeText').textContent = `Welcome, ${currentUser.username}`;
    loadCart();
}

// ============= Product Management =============

async function loadCategories() {
    try {
        const response = await axios.get('/api/categories');
        if (response.data.success) {
            const container = document.getElementById('categoryFilter');
            container.innerHTML = `
                <button onclick="filterByCategory(null)" 
                        class="px-4 py-2 rounded-lg ${!currentCategory ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100'}">
                    All
                </button>
            `;
            
            response.data.categories.forEach(cat => {
                const button = document.createElement('button');
                button.onclick = () => filterByCategory(cat.category);
                button.className = `px-4 py-2 rounded-lg ${currentCategory === cat.category ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100'}`;
                button.textContent = cat.category;
                container.appendChild(button);
            });
        }
    } catch (error) {
        console.error('Failed to load categories:', error);
    }
}

async function loadProducts(category = null) {
    try {
        const url = category ? `/api/products?category=${encodeURIComponent(category)}` : '/api/products';
        const response = await axios.get(url);
        
        if (response.data.success) {
            displayProducts(response.data.products);
        }
    } catch (error) {
        console.error('Failed to load products:', error);
    }
}

function filterByCategory(category) {
    currentCategory = category;
    loadCategories();
    loadProducts(category);
}

function displayProducts(products) {
    const container = document.getElementById('productList');
    
    if (products.length === 0) {
        container.innerHTML = '<div class="col-span-full text-center text-gray-500 py-12">No products available</div>';
        return;
    }
    
    container.innerHTML = products.map(product => `
        <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow">
            <img src="${product.image_url}" alt="${product.name}" class="w-full h-48 object-cover">
            <div class="p-4">
                <h3 class="text-lg font-semibold text-gray-900 mb-2">${product.name}</h3>
                <p class="text-gray-600 text-sm mb-2 line-clamp-2">${product.description || ''}</p>
                <div class="flex justify-between items-center mb-3">
                    <span class="text-2xl font-bold text-red-600">¥${parseFloat(product.price).toFixed(2)}</span>
                    <span class="text-sm text-gray-500">Stock: ${product.stock}</span>
                </div>
                <button onclick="addToCart(${product.id})" 
                        class="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors ${!currentUser ? 'opacity-50 cursor-not-allowed' : ''}"
                        ${!currentUser ? 'disabled title="Please login first"' : ''}>
                    <i class="fas fa-cart-plus mr-2"></i>Add to Cart
                </button>
            </div>
        </div>
    `).join('');
}

// ============= Cart Management =============

async function addToCart(productId) {
    if (!currentUser) {
        alert('Please login first');
        showLogin();
        return;
    }
    
    try {
        const response = await axios.post('/api/cart', {
            userId: currentUser.id,
            productId: productId,
            quantity: 1
        });
        
        if (response.data.success) {
            alert('Added to cart');
            loadCart();
        }
    } catch (error) {
        alert(error.response?.data?.message || 'Failed to add');
    }
}

async function loadCart() {
    if (!currentUser) return;
    
    try {
        const response = await axios.get(`/api/cart/${currentUser.id}`);
        if (response.data.success) {
            const cartItems = response.data.cartItems;
            document.getElementById('cartBadge').textContent = cartItems.length;
        }
    } catch (error) {
        console.error('Failed to load cart:', error);
    }
}

async function showCart() {
    if (!currentUser) {
        alert('Please login first');
        showLogin();
        return;
    }
    
    try {
        const response = await axios.get(`/api/cart/${currentUser.id}`);
        if (response.data.success) {
            const cartItems = response.data.cartItems;
            displayCart(cartItems);
            document.getElementById('cartModal').classList.remove('hidden');
        }
    } catch (error) {
        alert('Failed to load cart');
    }
}

function displayCart(items) {
    const container = document.getElementById('cartContent');
    
    if (items.length === 0) {
        container.innerHTML = '<p class="text-center text-gray-500 py-8">Your cart is empty</p>';
        return;
    }
    
    const totalAmount = items.reduce((sum, item) => sum + parseFloat(item.price) * item.quantity, 0);
    
    container.innerHTML = `
        <div class="space-y-4">
            ${items.map(item => `
                <div class="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
                    <img src="${item.image_url}" alt="${item.name}" class="w-20 h-20 object-cover rounded">
                    <div class="flex-1">
                        <h4 class="font-semibold">${item.name}</h4>
                        <p class="text-red-600 font-bold">¥${parseFloat(item.price).toFixed(2)}</p>
                    </div>
                    <div class="flex items-center gap-2">
                        <button onclick="updateCartQuantity(${item.id}, ${item.quantity - 1})" 
                                class="px-3 py-1 bg-gray-300 rounded hover:bg-gray-400">-</button>
                        <span class="w-12 text-center">${item.quantity}</span>
                        <button onclick="updateCartQuantity(${item.id}, ${item.quantity + 1})" 
                                class="px-3 py-1 bg-gray-300 rounded hover:bg-gray-400"
                                ${item.quantity >= item.stock ? 'disabled class="opacity-50"' : ''}>+</button>
                    </div>
                    <div class="font-bold text-lg">¥${(parseFloat(item.price) * item.quantity).toFixed(2)}</div>
                    <button onclick="removeFromCart(${item.id})" 
                            class="text-red-600 hover:text-red-700">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `).join('')}
        </div>
        <div class="mt-6 pt-6 border-t">
            <div class="flex justify-between items-center mb-4">
                <span class="text-xl font-bold">Total:</span>
                <span class="text-2xl font-bold text-red-600">¥${totalAmount.toFixed(2)}</span>
            </div>
            <button onclick="proceedToCheckout()" 
                    class="w-full bg-red-600 text-white py-3 rounded-lg hover:bg-red-700 text-lg font-semibold">
                Checkout
            </button>
        </div>
    `;
}

async function updateCartQuantity(cartId, newQuantity) {
    if (newQuantity < 1) {
        await removeFromCart(cartId);
        return;
    }
    
    try {
        const response = await axios.put(`/api/cart/${cartId}`, { quantity: newQuantity });
        if (response.data.success) {
            showCart();
        }
    } catch (error) {
        alert(error.response?.data?.message || 'Update failed');
    }
}

async function removeFromCart(cartId) {
    if (!confirm('Are you sure you want to remove this item?')) return;
    
    try {
        const response = await axios.delete(`/api/cart/${cartId}`);
        if (response.data.success) {
            showCart();
            loadCart();
        }
    } catch (error) {
        alert('Delete failed');
    }
}

async function proceedToCheckout() {
    const address = currentUser.address || prompt('Please enter shipping address:');
    if (!address) return;
    
    const phone = currentUser.phone || prompt('Please enter phone number:');
    if (!phone) return;
    
    try {
        const response = await axios.post('/api/orders', {
            userId: currentUser.id,
            shippingAddress: address,
            phone: phone
        });
        
        if (response.data.success) {
            alert(`Order created! Order #: ${response.data.orderId}\nTotal: ¥${parseFloat(response.data.totalAmount).toFixed(2)}`);
            closeModal('cartModal');
            loadCart();
            showOrders();
        }
    } catch (error) {
        alert(error.response?.data?.message || 'Failed to create order');
    }
}

// ============= Order Management =============

async function showOrders() {
    if (!currentUser) {
        alert('Please login first');
        showLogin();
        return;
    }
    
    try {
        const response = await axios.get(`/api/orders/user/${currentUser.id}`);
        if (response.data.success) {
            displayOrders(response.data.orders);
            document.getElementById('ordersModal').classList.remove('hidden');
        }
    } catch (error) {
        alert('Failed to load orders');
    }
}

function displayOrders(orders) {
    const container = document.getElementById('ordersContent');
    
    if (orders.length === 0) {
        container.innerHTML = '<p class="text-center text-gray-500 py-8">No orders yet</p>';
        return;
    }
    
    const statusMap = {
        'pending': { text: 'Pending', color: 'orange' },
        'paid': { text: 'Paid', color: 'green' },
        'shipped': { text: 'Shipped', color: 'blue' },
        'completed': { text: 'Completed', color: 'gray' },
        'cancelled': { text: 'Cancelled', color: 'red' }
    };
    
    container.innerHTML = orders.map(order => {
        const status = statusMap[order.status] || { text: order.status, color: 'gray' };
        return `
            <div class="bg-white border rounded-lg p-6 mb-4">
                <div class="flex justify-between items-start mb-4">
                    <div>
                        <h3 class="text-lg font-semibold">Order #: ${order.id}</h3>
                        <p class="text-gray-600 text-sm">${new Date(order.created_at).toLocaleString('en-US')}</p>
                    </div>
                    <span class="px-3 py-1 bg-${status.color}-100 text-${status.color}-800 rounded-full text-sm font-semibold">
                        ${status.text}
                    </span>
                </div>
                <div class="border-t pt-4">
                    <p class="text-gray-700 mb-2">
                        <i class="fas fa-map-marker-alt mr-2 text-gray-500"></i>
                        Shipping Address: ${order.shipping_address}
                    </p>
                    <p class="text-gray-700 mb-2">
                        <i class="fas fa-phone mr-2 text-gray-500"></i>
                        Phone: ${order.phone}
                    </p>
                    <div class="flex justify-between items-center mt-4">
                        <span class="text-xl font-bold text-red-600">Total: ¥${parseFloat(order.total_amount).toFixed(2)}</span>
                        <button onclick="viewOrderDetail(${order.id})" 
                                class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                            View Details
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

async function viewOrderDetail(orderId) {
    try {
        const response = await axios.get(`/api/orders/${orderId}`);
        if (response.data.success) {
            const order = response.data.order;
            alert(`Order Details:\n\n${order.items.map(item => 
                `${item.product_name} x ${item.quantity} = ¥${parseFloat(item.subtotal).toFixed(2)}`
            ).join('\n')}\n\nTotal: ¥${parseFloat(order.total_amount).toFixed(2)}`);
        }
    } catch (error) {
        alert('Failed to get order details');
    }
}

// Search functionality
document.getElementById('searchInput')?.addEventListener('input', (e) => {
    const searchTerm = e.target.value.toLowerCase();
    if (!searchTerm) {
        loadProducts(currentCategory);
        return;
    }
    
    const productCards = document.querySelectorAll('#productList > div');
    productCards.forEach(card => {
        const text = card.textContent.toLowerCase();
        card.style.display = text.includes(searchTerm) ? 'block' : 'none';
    });
});
