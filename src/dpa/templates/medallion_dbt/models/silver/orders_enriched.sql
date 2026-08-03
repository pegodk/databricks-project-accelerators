-- Silver: orders joined with customer, nation, and region to resolve descriptive attributes.
select
    o.o_orderkey                         as o_orderkey,
    o.o_custkey                          as o_custkey,
    o.o_orderstatus                      as o_orderstatus,
    o.o_totalprice                       as o_totalprice,
    o.o_orderdate                        as o_orderdate,
    o.o_orderpriority                    as o_orderpriority,
    o.o_clerk                            as o_clerk,
    o.o_shippriority                     as o_shippriority,
    c.c_mktsegment                       as customer_segment,
    coalesce(n.n_name, 'Unknown')        as customer_nation,
    coalesce(r.r_name, 'Unknown')        as customer_region
from {{ ref('orders') }} o
left join {{ ref('customer') }} c on o.o_custkey = c.c_custkey
left join {{ ref('nation') }} n on c.c_nationkey = n.n_nationkey
left join {{ ref('region') }} r on n.n_regionkey = r.r_regionkey
