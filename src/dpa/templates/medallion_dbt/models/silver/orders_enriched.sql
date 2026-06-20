select
    o.o_orderkey      as order_key,
    o.o_orderdate     as order_date,
    date_format(o.o_orderdate, 'yyyy-MM') as order_month,
    o.o_orderstatus   as order_status,
    o.o_orderpriority as order_priority,
    o.o_totalprice    as total_price,
    c.c_name          as customer_name,
    c.c_mktsegment    as market_segment,
    n.n_name          as nation,
    r.r_name          as region
from {{ ref('orders') }} o
join {{ ref('customer') }} c on o.o_custkey   = c.c_custkey
join {{ ref('nation') }}   n on c.c_nationkey = n.n_nationkey
join {{ ref('region') }}   r on n.n_regionkey = r.r_regionkey
