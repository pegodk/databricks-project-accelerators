select
    s.s_suppkey                         as supplier_key,
    s.s_name                            as supplier_name,
    s.s_address                         as supplier_address,
    s.s_phone                           as supplier_phone,
    coalesce(n.n_name, 'Unknown')       as supplier_nation,
    coalesce(r.r_name, 'Unknown')       as supplier_region
from {{ ref('supplier') }} s
left join {{ ref('nation') }} n on s.s_nationkey = n.n_nationkey
left join {{ ref('region') }} r on n.n_regionkey = r.r_regionkey
