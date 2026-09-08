import sqlite3
from pathlib import Path

# Veritabanı dosya yolunu belirle
DB_PATH = Path(__file__).resolve().parent / "sales.db"

def seed_database():
    # Varsa önceki veritabanını temiz başlatmak adına bağlantıyı aç
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabloları oluştur
    cursor.executescript("""
    DROP TABLE IF EXISTS reviews;
    DROP TABLE IF EXISTS sales;
    DROP TABLE IF EXISTS products;

    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        launch_date TEXT NOT NULL,
        unit_price REAL NOT NULL
    );

    CREATE TABLE sales (
        sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        week_start_date TEXT NOT NULL,
        units_sold INTEGER NOT NULL,
        revenue REAL NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products (product_id)
    );

    CREATE TABLE reviews (
        review_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        customer_name TEXT NOT NULL,
        review_text TEXT NOT NULL,
        review_date TEXT NOT NULL,
        sentiment TEXT DEFAULT NULL,
        issue_type TEXT DEFAULT NULL,
        flagged_for_ops BOOLEAN DEFAULT NULL,
        FOREIGN KEY (product_id) REFERENCES products (product_id)
    );
    """)

    # 1. Ürünler
    products_data = [
        (1, "USB-C Hub", "Accessories", "2024-01-01", 39.99),
        (2, "Laptop Stand", "Accessories", "2024-01-01", 49.99),
        (3, "Wireless Earbuds", "Audio", "2024-01-01", 79.99),
    ]
    cursor.executemany(
        "INSERT INTO products VALUES (?, ?, ?, ?, ?)", products_data
    )

    # 2. Satış Verisi (8 Hafta)
    weeks = [
        "2024-01-01", "2024-01-08", "2024-01-15", "2024-01-22",
        "2024-01-29", "2024-02-05", "2024-02-12", "2024-02-19"
    ]
    
    # Product 1 (Hub): Dengeli (~70-80 adet)
    # Product 2 (Stand): Yavaş yükseliş (~30 -> ~45 adet)
    # Product 3 (Earbuds): İlk 4 hafta güçlü (~120), sonra düşüş (~75 -> 50)
    sales_data = []
    
    hub_sales = [72, 75, 70, 74, 78, 76, 73, 75]
    stand_sales = [30, 32, 35, 37, 39, 42, 44, 46]
    earbuds_sales = [120, 125, 118, 122, 95, 75, 60, 48]

    for i, week in enumerate(weeks):
        sales_data.append((1, week, hub_sales[i], round(hub_sales[i] * 39.99, 2)))
        sales_data.append((2, week, stand_sales[i], round(stand_sales[i] * 49.99, 2)))
        sales_data.append((3, week, earbuds_sales[i], round(earbuds_sales[i] * 79.99, 2)))

    cursor.executemany(
        "INSERT INTO sales (product_id, week_start_date, units_sold, revenue) VALUES (?, ?, ?, ?)",
        sales_data
    )

    # 3. Yorumlar (30 adet: Product 1 pozitif, Product 2 nötr/iyi, Product 3 batarya şikayetli)
    reviews_data = [
        # Product 1: USB-C Hub (Dengeli, pozitif)
        (1, "Alice M.", "Works like a charm. All ports function as expected.", "2024-01-10"),
        (1, "Bob K.", "Very solid build quality and compact enough for travel.", "2024-01-18"),
        (1, "Charlie D.", "Good value for money, connects easily to my MacBook.", "2024-01-25"),
        (1, "Diana P.", "Does not overheat even when multiple devices are plugged in.", "2024-02-02"),
        (1, "Edward S.", "Reliable connection and fast data transfer speeds.", "2024-02-08"),
        (1, "Fiona G.", "Clean design, exactly what I needed for my workstation.", "2024-02-14"),
        (1, "George H.", "Great customer service and high performance hub.", "2024-02-18"),
        (1, "Hannah L.", "No complaints at all, seamless plug and play.", "2024-02-21"),

        # Product 2: Laptop Stand (Nötr / Pozitif)
        (2, "Ian W.", "Decent stand, sturdy enough for a 15-inch laptop.", "2024-01-12"),
        (2, "Julia R.", "Helps my posture, though adjustment mechanism is a bit stiff.", "2024-01-19"),
        (2, "Kevin T.", "Simple design, minimal desk footprint. Good product.", "2024-01-28"),
        (2, "Laura B.", "Looks clean on desk, does its job properly.", "2024-02-04"),
        (2, "Michael C.", "A bit heavy to carry around, but very solid on the table.", "2024-02-11"),
        (2, "Nina V.", "Satisfied with the purchase, improves airflow noticeably.", "2024-02-17"),
        (2, "Oscar N.", "Pretty basic but well engineered aluminum stand.", "2024-02-22"),

        # Product 3: Wireless Earbuds (Hafta 1-4 iyi, Hafta 5-8 kronik batarya şikayeti)
        (3, "Paul Q.", "Sound quality is impressive for the price, pairing was instant.", "2024-01-05"),
        (3, "Rachel O.", "Comfortable fit and bass response is great.", "2024-01-14"),
        (3, "Sam T.", "Loving these earbuds so far. Case feels premium.", "2024-01-20"),
        (3, "Tina U.", "Good battery life initially and microphone works well on calls.", "2024-01-27"),
        (3, "Victor E.", "Battery drops from 100% to zero in less than 30 minutes! Unacceptable.", "2024-02-01"),
        (3, "Wendy Y.", "Sound is fine but the right earbud stopped holding charge after two weeks.", "2024-02-03"),
        (3, "Xavier J.", "Terrible battery draining issue. Case won't charge properly.", "2024-02-07"),
        (3, "Yara K.", "Charging case gets excessively hot while charging. Major battery flaw.", "2024-02-10"),
        (3, "Zack M.", "Battery dies after just one conference call. Requesting a refund.", "2024-02-12"),
        (3, "Aria F.", "Left earbud battery indicator is completely broken.", "2024-02-15"),
        (3, "Brian R.", "Severely defective battery batch, lasts barely an hour now.", "2024-02-17"),
        (3, "Chloe S.", "Good audio when it works, but battery life makes it unusable.", "2024-02-19"),
        (3, "David H.", "Battery issue ruined this product. Need immediate customer support.", "2024-02-21"),
        (3, "Emma Z.", "Disappointed. Cannot recommend due to the fast battery drain.", "2024-02-23"),
        (3, "Frank N.", "Battery won't charge past 40 percent. Total waste of money.", "2024-02-24"),
    ]

    cursor.executemany(
        "INSERT INTO reviews (product_id, customer_name, review_text, review_date) VALUES (?, ?, ?, ?)",
        reviews_data
    )

    conn.commit()
    conn.close()
    print(f"Veritabani basariyla olusturuldu ve tohumlandi: {DB_PATH}")

if __name__ == "__main__":
    seed_database()