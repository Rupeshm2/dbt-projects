SELECT
 symbol,
 price_date,
 close,
 LOAD_TIMESTAMP
FROM dev.raw_data.stock_price
WHERE price_date >= CURRENT_DATE - INTERVAL '45 DAY'