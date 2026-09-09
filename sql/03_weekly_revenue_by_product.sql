-- Bulguyu doğrular: Wireless Earbuds 4. haftadan sonra belirgin bir düşüşe geçmektedir.

SELECT 
    s.week_start_date,
    p.product_name,
    s.units_sold,
    s.revenue,
    LAG(s.revenue, 1) OVER (
        PARTITION BY s.product_id 
        ORDER BY s.week_start_date
    ) AS prev_week_revenue,
    ROUND(
        (s.revenue - LAG(s.revenue, 1) OVER (PARTITION BY s.product_id ORDER BY s.week_start_date)) 
        / LAG(s.revenue, 1) OVER (PARTITION BY s.product_id ORDER BY s.week_start_date) * 100, 
        2
    ) AS wow_growth_pct
FROM sales s
JOIN products p ON s.product_id = p.product_id
ORDER BY p.product_name, s.week_start_date;