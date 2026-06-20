select
    order_month,
    market_segment,
    region,
    count(*)                      as order_count,
    sum(total_price)              as total_revenue,
    avg(total_price)              as avg_order_value,
    count(distinct customer_name) as unique_customers
from {{ ref('orders_enriched') }}
group by 1, 2, 3
