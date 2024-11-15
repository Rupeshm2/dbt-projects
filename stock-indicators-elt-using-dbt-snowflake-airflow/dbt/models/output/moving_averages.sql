
SELECT 
    SYMBOL,
    price_date,
    close,
	CAST(SMA_10 as DECIMAL(10,2)) AS SMA_10,
    CAST((close * 2 / (10 + 1)) + (SMA_10 * (1 - 2 / (10 + 1))) AS DECIMAL(10, 2)) AS EMA_10,
    LOAD_TIMESTAMP as ts
FROM  (
    SELECT 
        SYMBOL,
        price_date,
        close,
        AVG(close) OVER (PARTITION BY SYMBOL ORDER BY price_date ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS SMA_10,
	LOAD_TIMESTAMP
    FROM {{ ref("stock_price_base") }}
)