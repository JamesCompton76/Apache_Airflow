with source_data as (

select * from {{ source('fivetran_bronze', 'raw_taxi_data') }}

),

cleansed_data as (

select
    cast(VendorID as integer) as vendor_id,
    cast(tpep_pickup_datetime as timestamp) as pickup_datetime,
    cast(tpep_dropoff_datetime as timestamp) as dropoff_datetime,
    cast(passenger_count as integer) as passenger_count,
    cast(trip_distance as double) as trip_distance,
    cast(fare_amount as numeric(10, 2)) as fare_amount,
    cast(total_amount as numeric(10, 2)) as total_amount,
    cast(payment_type as double) as payment_type,
    cast(tip_amount as numeric(10, 2)) as tip_amount

from source_data

)

select *
from cleansed_data
where total_amount > 0
