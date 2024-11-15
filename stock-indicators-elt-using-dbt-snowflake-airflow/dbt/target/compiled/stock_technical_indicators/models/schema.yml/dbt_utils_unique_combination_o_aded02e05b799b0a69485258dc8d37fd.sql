





with validation_errors as (

    select
        symbol, price_date
    from dev.analytics.bollinger_bands
    group by symbol, price_date
    having count(*) > 1

)

select *
from validation_errors


