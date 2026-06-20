select
    o.o_orderdate                                       as calendar_order_key,
    l.l_commitdate                                      as calendar_commit_key,
    l.l_receiptdate                                     as calendar_receipt_key,
    l.l_shipdate                                        as calendar_ship_key,
    o.o_custkey                                         as customer_key,
    l.l_partkey                                         as part_key,
    l.l_suppkey                                         as supplier_key,
    l.l_orderkey                                        as order_header_code,
    l.l_linenumber                                      as order_line_code,
    l.l_quantity                                        as order_quantity,
    l.l_extendedprice                                   as order_extended_price_usd,
    l.l_discount                                        as order_discount_usd,
    l.l_tax                                             as order_tax_usd,
    ps.ps_supplycost                                    as part_supply_cost_usd,
    datediff(l.l_commitdate,  o.o_orderdate)            as order_commit_lag_days,
    datediff(l.l_receiptdate, o.o_orderdate)            as order_receipt_lag_days,
    datediff(l.l_shipdate,    o.o_orderdate)            as order_ship_lag_days
from {{ ref('lineitem') }} l
join {{ ref('orders') }} o
    on l.l_orderkey = o.o_orderkey
left join {{ ref('partsupp') }} ps
    on l.l_partkey = ps.ps_partkey and l.l_suppkey = ps.ps_suppkey
