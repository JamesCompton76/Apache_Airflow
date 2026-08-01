select 
    'fct_daily_taxi_revenue' as table_name, 
    count(*) as row_count 
from {{ ref('fct_daily_taxi_revenue') }}

union all

select 
    'fct_payment_type_metrics' as table_name, 
    count(*) as row_count 
from {{ ref('fct_payment_type_metrics') }}
