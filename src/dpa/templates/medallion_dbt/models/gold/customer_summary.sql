select
    customer_name,
    nation,
    region,
    count(*)         as order_count,
    sum(total_price) as lifetime_revenue,
    min(order_date)  as first_order_date,
    max(order_date)  as last_order_date
from {{ ref('orders_enriched') }}
group by 1, 2, 3
