-- Tohum Verisi: Ürünler, 8 Haftalık Satışlar ve Müşteri Yorumları

-- Ürünler
INSERT INTO products (product_id, product_name, category, launch_date, unit_price) VALUES
(1, 'USB-C Hub', 'Accessories', '2024-01-01', 39.99),
(2, 'Laptop Stand', 'Accessories', '2024-01-01', 49.99),
(3, 'Wireless Earbuds', 'Audio', '2024-01-01', 79.99);

-- 8 Haftalık Satışlar (Product 3 için 5. haftadan sonra düşüş deseni)
INSERT INTO sales (product_id, week_start_date, units_sold, revenue) VALUES
(1, '2024-01-01', 72, 2879.28), (2, '2024-01-01', 30, 1499.70), (3, '2024-01-01', 120, 9598.80),
(1, '2024-01-08', 75, 2999.25), (2, '2024-01-08', 32, 1599.68), (3, '2024-01-08', 125, 9998.75),
(1, '2024-01-15', 70, 2799.30), (2, '2024-01-15', 35, 1749.65), (3, '2024-01-15', 118, 9438.82),
(1, '2024-01-22', 74, 2959.26), (2, '2024-01-22', 37, 1849.63), (3, '2024-01-22', 122, 9758.78),
(1, '2024-01-29', 78, 3119.22), (2, '2024-01-29', 39, 1949.61), (3, '2024-01-29', 95, 7599.05),
(1, '2024-02-05', 76, 3039.24), (2, '2024-02-05', 42, 2099.58), (3, '2024-02-05', 75, 5999.25),
(1, '2024-02-12', 73, 2919.27), (2, '2024-02-12', 44, 2199.56), (3, '2024-02-12', 60, 4799.40),
(1, '2024-02-19', 75, 2999.25), (2, '2024-02-19', 46, 2299.54), (3, '2024-02-19', 48, 3839.52);

-- Örnek Yorumlar (Başlangıçta sentiment ve issue_type alanları NULL)
INSERT INTO reviews (product_id, customer_name, review_text, review_date) VALUES
(1, 'Alice M.', 'Works like a charm. All ports function as expected.', '2024-01-10'),
(2, 'Ian W.', 'Decent stand, sturdy enough for a 15-inch laptop.', '2024-01-12'),
(3, 'Paul Q.', 'Sound quality is impressive for the price, pairing was instant.', '2024-01-05'),
(3, 'Victor E.', 'Battery drops from 100% to zero in less than 30 minutes! Unacceptable.', '2024-02-01'),
(3, 'Wendy Y.', 'Sound is fine but the right earbud stopped holding charge after two weeks.', '2024-02-03');