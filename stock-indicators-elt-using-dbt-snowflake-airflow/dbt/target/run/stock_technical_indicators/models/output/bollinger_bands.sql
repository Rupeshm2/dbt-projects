
  
    

        create or replace transient table dev.analytics.bollinger_bands
         as
        (SELECT 
    symbol,
    price_date,
    round(AVG(Close) OVER (PARTITION BY SYMBOL ORDER BY price_date ROWS BETWEEN 9 PRECEDING AND CURRENT ROW),2) AS SMA_10,
    round(AVG(Close) OVER (PARTITION BY SYMBOL ORDER BY price_date ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) + 2 * STDDEV_SAMP(Close) OVER (PARTITION BY SYMBOL ORDER BY price_date ROWS BETWEEN 9 PRECEDING AND CURRENT ROW),2) AS Upper_Band,
    round(AVG(Close) OVER (PARTITION BY SYMBOL ORDER BY price_date ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) - 2 * STDDEV_SAMP(Close) OVER (PARTITION BY SYMBOL ORDER BY price_date ROWS BETWEEN 9 PRECEDING AND CURRENT ROW),2) AS Lower_Band,
    LOAD_TIMESTAMP as ts
    from dev.analytics.stock_price_base
        );
      
  