#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL查询示例模板
包含各种常用的数据库查询语句，可直接复制使用
"""

# ========== 基础查询示例 ==========

# 1. 查询所有数据（限制行数）
QUERY_ALL_DATA = """
SELECT * FROM table_name 
LIMIT 1000
"""

# 2. 查询特定字段
QUERY_SPECIFIC_FIELDS = """
SELECT 
    id,
    name,
    created_date,
    status
FROM table_name
"""

# 3. 条件查询
QUERY_WITH_CONDITION = """
SELECT 
    id,
    name,
    amount,
    created_date
FROM orders
WHERE created_date >= '2024-01-01'
    AND status = 'completed'
    AND amount > 100
ORDER BY created_date DESC
"""

# ========== 关联查询示例 ==========

# 4. 内连接查询
QUERY_INNER_JOIN = """
SELECT 
    o.order_id,
    c.customer_name,
    o.order_date,
    o.total_amount,
    p.product_name
FROM orders o
INNER JOIN customers c ON o.customer_id = c.id
INNER JOIN products p ON o.product_id = p.id
WHERE o.status = 'completed'
ORDER BY o.order_date DESC
"""

# 5. 左连接查询
QUERY_LEFT_JOIN = """
SELECT 
    c.customer_name,
    c.email,
    o.order_id,
    o.order_date,
    o.total_amount
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
WHERE c.created_date >= '2024-01-01'
ORDER BY c.created_date DESC
"""

# ========== 聚合查询示例 ==========

# 6. 分组统计
QUERY_GROUP_BY = """
SELECT 
    customer_id,
    COUNT(*) as order_count,
    SUM(total_amount) as total_spent,
    AVG(total_amount) as avg_order_value,
    MAX(order_date) as last_order_date
FROM orders
WHERE order_date >= '2024-01-01'
GROUP BY customer_id
HAVING total_spent > 1000
ORDER BY total_spent DESC
"""

# 7. 按月统计
QUERY_MONTHLY_STATS = """
SELECT 
    DATE_FORMAT(order_date, '%Y-%m') as month,
    COUNT(*) as order_count,
    SUM(total_amount) as monthly_revenue,
    AVG(total_amount) as avg_order_value
FROM orders
WHERE order_date >= '2024-01-01'
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY month DESC
"""

# ========== 复杂查询示例 ==========

# 8. 子查询
QUERY_SUBQUERY = """
SELECT 
    customer_name,
    email,
    total_orders,
    total_spent
FROM customers c
WHERE c.id IN (
    SELECT customer_id 
    FROM orders 
    WHERE total_amount > (
        SELECT AVG(total_amount) 
        FROM orders
    )
)
ORDER BY total_spent DESC
"""

# 9. 窗口函数
QUERY_WINDOW_FUNCTION = """
SELECT 
    customer_name,
    order_date,
    total_amount,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) as order_rank,
    SUM(total_amount) OVER (PARTITION BY customer_id) as customer_total
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE order_date >= '2024-01-01'
ORDER BY customer_id, order_date DESC
"""

# ========== 实际业务查询示例 ==========

# 10. 客户订单汇总
CUSTOMER_ORDER_SUMMARY = """
SELECT 
    c.customer_id,
    c.customer_name,
    c.contact_phone,
    c.email,
    c.region,
    COUNT(o.order_id) as total_orders,
    SUM(o.total_amount) as total_spent,
    AVG(o.total_amount) as avg_order_value,
    MAX(o.order_date) as last_order_date,
    MIN(o.order_date) as first_order_date
FROM customer_info c
LEFT JOIN new_customer_orders o ON c.customer_id = o.customer_id
WHERE c.created_date >= '2024-01-01'
GROUP BY c.customer_id, c.customer_name, c.contact_phone, c.email, c.region
ORDER BY total_spent DESC
"""

# 11. 拜访记录统计
VISIT_RECORD_STATS = """
SELECT 
    v.visit_id,
    v.customer_name,
    v.visit_date,
    v.visit_type,
    v.notes,
    CASE 
        WHEN v.visit_type = '首次拜访' THEN '新客户'
        WHEN v.visit_type = '跟进拜访' THEN '老客户'
        ELSE '其他'
    END as customer_type
FROM visit_record v
WHERE v.visit_date >= '2024-01-01'
ORDER BY v.visit_date DESC
"""

# 12. 销售业绩分析
SALES_PERFORMANCE = """
SELECT 
    DATE_FORMAT(o.order_date, '%Y-%m') as month,
    COUNT(DISTINCT o.customer_id) as unique_customers,
    COUNT(o.order_id) as total_orders,
    SUM(o.total_amount) as total_revenue,
    AVG(o.total_amount) as avg_order_value,
    SUM(o.total_amount) / COUNT(DISTINCT o.customer_id) as revenue_per_customer
FROM new_customer_orders o
WHERE o.order_date >= '2024-01-01'
    AND o.status = 'completed'
GROUP BY DATE_FORMAT(o.order_date, '%Y-%m')
ORDER BY month DESC
"""

# ========== 使用示例 ==========

def get_query_examples():
    """获取所有查询示例"""
    return {
        "基础查询": {
            "查询所有数据": QUERY_ALL_DATA,
            "查询特定字段": QUERY_SPECIFIC_FIELDS,
            "条件查询": QUERY_WITH_CONDITION
        },
        "关联查询": {
            "内连接查询": QUERY_INNER_JOIN,
            "左连接查询": QUERY_LEFT_JOIN
        },
        "聚合查询": {
            "分组统计": QUERY_GROUP_BY,
            "按月统计": QUERY_MONTHLY_STATS
        },
        "复杂查询": {
            "子查询": QUERY_SUBQUERY,
            "窗口函数": QUERY_WINDOW_FUNCTION
        },
        "业务查询": {
            "客户订单汇总": CUSTOMER_ORDER_SUMMARY,
            "拜访记录统计": VISIT_RECORD_STATS,
            "销售业绩分析": SALES_PERFORMANCE
        }
    }

def print_query_examples():
    """打印所有查询示例"""
    examples = get_query_examples()
    
    print("📋 SQL查询示例模板")
    print("=" * 50)
    
    for category, queries in examples.items():
        print(f"\n📂 {category}:")
        for name, query in queries.items():
            print(f"  📝 {name}:")
            print(f"    {query.strip()[:100]}...")
            print()

if __name__ == "__main__":
    print_query_examples() 