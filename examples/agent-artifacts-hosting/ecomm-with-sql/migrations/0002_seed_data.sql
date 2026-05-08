-- PostgreSQL Seed Data for E-commerce Platform

-- Insert sample products
INSERT INTO products (id, name, description, price, stock, category, image_url) VALUES 
  (1, 'iPhone 15 Pro', 'Latest Apple flagship phone, A17 Pro chip, titanium frame', 999.00, 50, 'Phones & Electronics', 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400'),
  (2, 'MacBook Pro 16"', 'M3 Max chip, professional-grade laptop', 2499.00, 30, 'Computers & Office', 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400'),
  (3, 'AirPods Pro 2', 'Active noise cancellation wireless earbuds, spatial audio', 249.00, 100, 'Audio & Entertainment', 'https://images.unsplash.com/photo-1606841837239-c5a1a4a07af7?w=400'),
  (4, 'Sony A7R5', 'Full-frame mirrorless camera, 61MP', 3899.00, 20, 'Cameras & Photography', 'https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=400'),
  (5, 'Nike Air Max', 'Stylish sports shoes, comfortable and breathable', 129.00, 200, 'Sports & Outdoors', 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400'),
  (6, 'Kindle Oasis', 'E-book reader, 7-inch screen', 249.00, 80, 'Books & Media', 'https://images.unsplash.com/photo-1589998059171-988d887df646?w=400'),
  (7, 'PlayStation 5', 'Next-gen gaming console, 4K gaming experience', 499.00, 40, 'Gaming', 'https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=400'),
  (8, 'Dyson Hair Dryer', 'High-speed digital motor, intelligent heat control', 429.00, 60, 'Home Appliances', 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=400'),
  (9, 'Switch OLED', 'Nintendo game console, 7-inch OLED screen', 349.00, 70, 'Gaming', 'https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=400'),
  (10, 'Apple Watch Ultra 2', 'Outdoor sports smartwatch, titanium case', 799.00, 45, 'Wearables', 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=400')
ON CONFLICT (id) DO NOTHING;

-- Reset sequence to avoid conflict with future inserts
SELECT setval('products_id_seq', (SELECT MAX(id) FROM products));

-- Insert test user
-- Password: demo123 (base64 encoded)
INSERT INTO users (id, email, password_hash, username, phone, address) VALUES 
  (1, 'demo@example.com', 'ZGVtbzEyMw==', 'DemoUser', '13800138000', 'Beijing, Chaoyang District')
ON CONFLICT (id) DO NOTHING;

-- Reset sequence to avoid conflict with future inserts
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
