select
    payment_type,
    count(*) as total_trips,
    sum(total_amount) as total_revenue,
    avg(tip_amount) as avg_tip_amount,
    avg(trip_distance) as avg_trip_distance_miles
from {{ ref('stg_yellow_tripdata') }}
group by 1
