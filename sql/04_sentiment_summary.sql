-- Ajan Çalıştıktan Sonra: Sentiment & Kök Neden Dağılımı
-- Ürün bazında duygu durumu ve bayraklanan (flagged) operasyonel sorunları özetler.

SELECT 
    p.product_name,
    COUNT(r.review_id) AS total_reviews,
    SUM(CASE WHEN r.sentiment = 'positive' THEN 1 ELSE 0 END) AS positive_count,
    SUM(CASE WHEN r.sentiment = 'neutral' THEN 1 ELSE 0 END) AS neutral_count,
    SUM(CASE WHEN r.sentiment = 'negative' THEN 1 ELSE 0 END) AS negative_count,
    SUM(CASE WHEN r.flagged_for_ops = 1 THEN 1 ELSE 0 END) AS flagged_ops_count,
    GROUP_CONCAT(DISTINCT r.issue_type) AS identified_issues
FROM products p
LEFT JOIN reviews r ON p.product_id = r.product_id
GROUP BY p.product_id, p.product_name;