select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select price_date
from dev.analytics.moving_averages
where price_date is null



      
    ) dbt_internal_test