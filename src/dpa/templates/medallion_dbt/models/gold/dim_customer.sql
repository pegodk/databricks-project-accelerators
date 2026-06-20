select
    c.c_custkey                         as customer_key,
    c.c_name                            as customer_name,
    c.c_address                         as customer_address,
    c.c_phone                           as customer_phone,
    c.c_acctbal                         as customer_acctbal,
    c.c_mktsegment                      as customer_segment,
    coalesce(n.n_name, 'Unknown')       as customer_nation,
    coalesce(r.r_name, 'Unknown')       as customer_region
from {{ ref('customer') }} c
left join {{ ref('nation') }} n on c.c_nationkey = n.n_nationkey
left join {{ ref('region') }} r on n.n_regionkey = r.r_regionkey
