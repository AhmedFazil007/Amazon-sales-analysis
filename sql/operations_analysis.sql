-- Run against analysis/amazon_orders.sqlite after python/analyze_amazon.py.
-- 'records' are workbook rows; order counts use DISTINCT order_id.
SELECT status, COUNT(*) AS records, COUNT(DISTINCT order_id) AS distinct_orders
FROM orders GROUP BY status ORDER BY records DESC;

-- Fulfillment and status comparison, if the source workbook has fulfilment.
SELECT fulfilment, status, COUNT(DISTINCT order_id) AS orders
FROM orders
GROUP BY fulfilment, status
ORDER BY fulfilment, orders DESC;

-- Category contribution by recorded amount, if amount and category exist.
-- This is NOT automatically net sales; cancellation/return handling needs verification.
SELECT category, COUNT(*) AS records, ROUND(SUM(amount),2) AS recorded_amount
FROM orders
GROUP BY category ORDER BY recorded_amount DESC;

-- Monthly recorded amount if dates were successfully parsed.
SELECT SUBSTR(date,1,7) AS month, COUNT(DISTINCT order_id) AS orders,
       ROUND(SUM(amount),2) AS recorded_amount
FROM orders WHERE date IS NOT NULL
GROUP BY SUBSTR(date,1,7) ORDER BY month;
