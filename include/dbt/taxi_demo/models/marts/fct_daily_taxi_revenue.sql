select
vendor_id,
cast(pickup_datetime as date) as service_date,
count(*) as total_trips,
sum(trip_distance) as total_distance_miles,
sum(total_amount) as total_revenue
from {{ ref('stg_yellow_tripdata') }}
group by 1, 2
