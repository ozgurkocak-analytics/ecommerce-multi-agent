-- Tablo Şemaları: products, sales, reviews

DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS products;

-- 1. Ürün Kataloğu
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    launch_date TEXT NOT NULL,
    unit_price REAL NOT NULL
);

-- 2. Haftalık Satış Kayıtları
CREATE TABLE sales (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    week_start_date TEXT NOT NULL,
    units_sold INTEGER NOT NULL,
    revenue REAL NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products (product_id)
);

-- 3. Müşteri Yorumları
-- Not: sentiment, issue_type ve flagged_for_ops alanları
-- başlangıçta NULL olup LLM/Ajan tarafından güncellenir.
CREATE TABLE reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    customer_name TEXT NOT NULL,
    review_text TEXT NOT NULL,
    review_date TEXT NOT NULL,
    sentiment TEXT DEFAULT NULL,       -- 'positive', 'neutral', 'negative'
    issue_type TEXT DEFAULT NULL,      -- örn: 'battery', 'hardware', 'none'
    flagged_for_ops BOOLEAN DEFAULT NULL, -- Kritik operasyon alarmı (TRUE/FALSE)
    FOREIGN KEY (product_id) REFERENCES products (product_id)
);