-- 订单相关查询
-- 文件名: order_queries.sql
-- 描述: 包含订单信息相关的各种查询

-- 查询7: 订单按照后台四级类目进行聚合（优化版本）
-- 使用: count_forth_kind

SELECT
    *,
    SUM(
        CASE 
            WHEN 核心品宽 = 1 AND 第几日下单 < 7 THEN 1
            ELSE 0
        END
    ) OVER (PARTITION BY 客户id, 后台四级类目) AS 复购次数
FROM (
    SELECT
        nco.日期,
        nco.客户id,
        nco.后台一级类目,
        nco.后台二级类目,
        nco.后台三级类目,
        nco.后台四级类目,
        ci.首单时间,
        DATEDIFF(nco.日期, ci.首单时间) AS 第几日下单,
        CASE
            WHEN nco.后台一级类目 = '蔬菜水果' THEN '菜'
            WHEN nco.后台一级类目 IN ('肉禽水产（鲜）', '肉禽水产（冷冻）', '冷冻半成品', '速食熟食', '调理包')
                 AND nco.后台二级类目 NOT IN ('豆制品', '米面制品') THEN '肉'
            WHEN nco.后台二级类目 = '米' THEN '米'
            ELSE '非核心品'
        END AS 核心品分类,
        SUM(nco.销售额) AS 品类销售额
    FROM
        new_customer_orders AS nco
    LEFT JOIN
        customer_info AS ci ON nco.客户id = ci.客户id
    WHERE 
        nco.日期 >= 20250601
    GROUP BY
        nco.日期,
        nco.客户id,
        nco.后台一级类目,
        nco.后台二级类目,
        nco.后台三级类目,
        nco.后台四级类目,
        ci.首单时间
) t
-- 计算核心品宽
CROSS JOIN LATERAL (
    SELECT
        CASE
            WHEN t.核心品分类 = '菜' AND t.品类销售额 >= 5 THEN 1
            WHEN t.核心品分类 = '肉' AND t.品类销售额 >= 15 THEN 1
            WHEN t.核心品分类 = '米' AND t.品类销售额 >= 50 THEN 1
            ELSE 0
        END AS 核心品宽
) k
ORDER BY
    日期, 客户id;


-- 查询8: 以四级类目聚合为基础，计算首单首拓、首周复拓，未复拓四级品
-- 使用: first_week_repeat_purchase

WITH base AS (
    SELECT
        客户id,
        COUNT(DISTINCT CASE 
            WHEN 第几日下单 = 0 AND 核心品宽 = 1 
            THEN 后台四级类目 
        END) AS 首拓品宽,
        COUNT(DISTINCT CASE 
            WHEN 第几日下单 <= 6 AND 复购次数 >= 2 
            THEN 后台四级类目 
        END) AS 复购品宽,
        GROUP_CONCAT(DISTINCT CASE
            WHEN 第几日下单 <= 6 AND 复购次数 < 2 AND 核心品宽 = 1
            THEN 后台四级类目
        END SEPARATOR '，') AS 未复拓四级品
    FROM
        forth_kind_sum_202506
    GROUP BY
        客户id
)
SELECT
    客户id,
    首拓品宽,
    复购品宽,
    CASE
        WHEN 复购品宽 > 10 THEN '已达成上限'
        ELSE 未复拓四级品
    END AS 未复拓四级品
FROM base;

-- 查询9: 品类宽表
-- 使用: kind_wide_table

-- 客户首周各品类分析（宽表格式）
-- 文件名: customer_first_week_analysis.sql
-- 描述: 以客户为维度，统计各一级品类在首周（第几日下单≤6）的销售额和频次

SELECT
    客户id,
    -- 蔬菜水果
    SUM(CASE WHEN 后台一级类目 = '蔬菜水果' AND 第几日下单 <= 6 THEN 品类销售额 ELSE 0 END) AS 首周蔬菜销售额,
    COUNT(DISTINCT CASE WHEN 后台一级类目 = '蔬菜水果' AND 第几日下单 <= 6 THEN 日期 ELSE NULL END) AS 首周蔬菜频次,
    
    -- 米面粮油
    SUM(CASE WHEN 后台一级类目 = '米面粮油' AND 第几日下单 <= 6 THEN 品类销售额 ELSE 0 END) AS 首周米面销售额,
    COUNT(DISTINCT CASE WHEN 后台一级类目 = '米面粮油' AND 第几日下单 <= 6 THEN 日期 ELSE NULL END) AS 首周米面频次,
    
    -- 冷冻半成品
    SUM(CASE WHEN 后台一级类目 = '冷冻半成品' AND 第几日下单 <= 6 THEN 品类销售额 ELSE 0 END) AS 首周冷冻半成品销售额,
    COUNT(DISTINCT CASE WHEN 后台一级类目 = '冷冻半成品' AND 第几日下单 <= 6 THEN 日期 ELSE NULL END) AS 首周冷冻半成品频次,
    
    -- 餐厨用品
    SUM(CASE WHEN 后台一级类目 = '餐厨用品' AND 第几日下单 <= 6 THEN 品类销售额 ELSE 0 END) AS 首周餐厨销售额,
    COUNT(DISTINCT CASE WHEN 后台一级类目 = '餐厨用品' AND 第几日下单 <= 6 THEN 日期 ELSE NULL END) AS 首周餐厨频次,
    
    -- 调料干货
    SUM(CASE WHEN 后台一级类目 = '调料干货' AND 第几日下单 <= 6 THEN 品类销售额 ELSE 0 END) AS 首周调料销售额,
    COUNT(DISTINCT CASE WHEN 后台一级类目 = '调料干货' AND 第几日下单 <= 6 THEN 日期 ELSE NULL END) AS 首周调料频次,
    
    -- 鲜蛋及蛋制品
    SUM(CASE WHEN 后台一级类目 = '鲜蛋及蛋制品' AND 第几日下单 <= 6 THEN 品类销售额 ELSE 0 END) AS 首周鲜蛋销售额,
    COUNT(DISTINCT CASE WHEN 后台一级类目 = '鲜蛋及蛋制品' AND 第几日下单 <= 6 THEN 日期 ELSE NULL END) AS 首周鲜蛋频次,
    
    -- 冷冻饮品、饮料、酒
    SUM(CASE WHEN 后台一级类目 = '冷冻饮品、饮料、酒' AND 第几日下单 <= 6 THEN 品类销售额 ELSE 0 END) AS 首周饮品销售额,
    COUNT(DISTINCT CASE WHEN 后台一级类目 = '冷冻饮品、饮料、酒' AND 第几日下单 <= 6 THEN 日期 ELSE NULL END) AS 首周饮品频次,
    
    -- 速食熟食
    SUM(CASE WHEN 后台一级类目 = '速食熟食' AND 第几日下单 <= 6 THEN 品类销售额 ELSE 0 END) AS 首周速食销售额,
    COUNT(DISTINCT CASE WHEN 后台一级类目 = '速食熟食' AND 第几日下单 <= 6 THEN 日期 ELSE NULL END) AS 首周速食频次,
    
    -- 肉禽水产（冷冻）
    SUM(CASE WHEN 后台一级类目 = '肉禽水产（冷冻）' AND 第几日下单 <= 6 THEN 品类销售额 ELSE 0 END) AS 首周冷冻肉销售额,
    COUNT(DISTINCT CASE WHEN 后台一级类目 = '肉禽水产（冷冻）' AND 第几日下单 <= 6 THEN 日期 ELSE NULL END) AS 首周冷冻肉频次,
    
    -- 调理包
    SUM(CASE WHEN 后台一级类目 = '调理包' AND 第几日下单 <= 6 THEN 品类销售额 ELSE 0 END) AS 首周调理包销售额,
    COUNT(DISTINCT CASE WHEN 后台一级类目 = '调理包' AND 第几日下单 <= 6 THEN 日期 ELSE NULL END) AS 首周调理包频次,
    
    -- 肉禽水产（鲜）
    SUM(CASE WHEN 后台一级类目 = '肉禽水产（鲜）' AND 第几日下单 <= 6 THEN 品类销售额 ELSE 0 END) AS 首周鲜肉销售额,
    COUNT(DISTINCT CASE WHEN 后台一级类目 = '肉禽水产（鲜）' AND 第几日下单 <= 6 THEN 日期 ELSE NULL END) AS 首周鲜肉频次,
    
    -- 休闲食品
    SUM(CASE WHEN 后台一级类目 = '休闲食品' AND 第几日下单 <= 6 THEN 品类销售额 ELSE 0 END) AS 首周休闲食品销售额,
    COUNT(DISTINCT CASE WHEN 后台一级类目 = '休闲食品' AND 第几日下单 <= 6 THEN 日期 ELSE NULL END) AS 首周休闲食品频次,
    
    -- 焙烤食品
    SUM(CASE WHEN 后台一级类目 = '焙烤食品' AND 第几日下单 <= 6 THEN 品类销售额 ELSE 0 END) AS 首周焙烤销售额,
    COUNT(DISTINCT CASE WHEN 后台一级类目 = '焙烤食品' AND 第几日下单 <= 6 THEN 日期 ELSE NULL END) AS 首周焙烤频次
    
FROM
    forth_kind_sum_202506
GROUP BY
    客户id
ORDER BY
    客户id;

