# table_schemas.py
# 集中管理所有表的结构（字段名、类型、主键、索引）

TABLE_SCHEMAS = {
    'customer_info': {
        'columns': [
            ('客户id', 'VARCHAR(50) NOT NULL'),
            ('首单时间', 'DATE'),
            ('当前归属大区', 'VARCHAR(100)'),
            ('当前归属分区', 'VARCHAR(100)'),
            ('首单销售组名称', 'VARCHAR(100)'),
            ('首单BDmis号', 'VARCHAR(100)'),
            ('首单BD姓名', 'VARCHAR(100)'),
            ('当前归属销售组', 'VARCHAR(100)'),
            ('当前归属BDmis号', 'VARCHAR(100)'),
            ('当前归属BD姓名', 'VARCHAR(100)'),
            ('客户名称', 'VARCHAR(100)'),
            ('客户来源', 'VARCHAR(100)'),
            ('二级业态', 'VARCHAR(100)'),
            ('创建时间', 'VARCHAR(100)'),
            ('物理城市等级', 'VARCHAR(100)'),
            ('客户类型', 'VARCHAR(100)')
        ],
        'primary_key': '客户id',
        'indexes': [
            # 普通索引
            {'name': 'idx_customer_id', 'columns': ['客户id'], 'type': 'INDEX'},
            {'name': 'idx_first_order_time', 'columns': ['首单时间'], 'type': 'INDEX'},
            {'name': 'idx_customer_source', 'columns': ['客户来源'], 'type': 'INDEX'},
            {'name': 'idx_customer_type', 'columns': ['客户类型'], 'type': 'INDEX'},
            # 复合索引
            {'name': 'idx_bd_info', 'columns': ['当前归属BDmis号', '当前归属BD姓名'], 'type': 'INDEX'},
            # 唯一索引
            {'name': 'uk_customer_id', 'columns': ['客户id'], 'type': 'UNIQUE'}
        ]
    },
    'all_customer_info': {
        'columns': [
            ('当前归属大区', 'VARCHAR(100)'),
            ('新老城', 'VARCHAR(100)'),
            ('当前归属事业部ID', 'VARCHAR(100)'),
            ('当前归属事业部', 'VARCHAR(100)'),
            ('当前物理所在事业部', 'VARCHAR(100)'),
            ('当前归属分区', 'VARCHAR(100)'),
            ('首单销售组名称', 'VARCHAR(100)'),
            ('首单BDM姓名', 'VARCHAR(100)'),
            ('首单BDmis号', 'VARCHAR(100)'),
            ('首单BD姓名', 'VARCHAR(100)'),
            ('当前归属BDid', 'VARCHAR(100)'),
            ('当前归属销售组', 'VARCHAR(100)'),
            ('当前归属BDM姓名', 'VARCHAR(100)'),
            ('当前归属BDmis号', 'VARCHAR(100)'),
            ('当前归属BD姓名', 'VARCHAR(100)'),
            ('客户id', 'VARCHAR(50) NOT NULL'),
            ('客户名称', 'VARCHAR(100)'),
            ('客户来源', 'VARCHAR(100)'),
            ('一级业态', 'VARCHAR(100)'),
            ('二级业态', 'VARCHAR(100)'),
            ('首单时间', 'DATE'),
            ('首单销售额', 'DECIMAL(10, 2)'),
            ('首单生鲜销售额', 'DECIMAL(10, 2)'),
            ('首单大米销售额', 'DECIMAL(10, 2)'),
            ('首单蔬菜销售额', 'DECIMAL(10, 2)'),
            ('首单鲜肉销售额', 'DECIMAL(10, 2)'),
            ('首单冻肉销售额', 'DECIMAL(10, 2)'),
            ('首单冷冻半成品销售额', 'DECIMAL(10, 2)'),
            ('首单速食熟食销售额', 'DECIMAL(10, 2)'),
            ('首单标品销售额', 'DECIMAL(10, 2)'),
            ('首单冻品销售额', 'DECIMAL(10, 2)'),
            ('首单品宽', 'INT'),
            ('首单大米四级品宽', 'INT'),
            ('首单鲜肉品宽', 'INT'),
            ('首单冻肉品宽', 'INT'),
            ('首单冷冻半成品品宽', 'INT'),
            ('首单速食熟食品宽', 'INT'),
            ('首单冻品品宽', 'INT'),
            ('首周销售额', 'DECIMAL(10, 2)'),
            ('首周生鲜销售额', 'DECIMAL(10, 2)'),
            ('首周大米销售额', 'DECIMAL(10, 2)'),
            ('首周蔬菜销售额', 'DECIMAL(10, 2)'),
            ('首周鲜肉销售额', 'DECIMAL(10, 2)'),
            ('首周冻肉销售额', 'DECIMAL(10, 2)'),
            ('首周冷冻半成品销售额', 'DECIMAL(10, 2)'),
            ('首周速食熟食销售额', 'DECIMAL(10, 2)'),
            ('首周标品销售额', 'DECIMAL(10, 2)'),
            ('首周冻品销售额', 'DECIMAL(10, 2)'),
            ('首周品宽', 'INT'),
            ('首周大米四级品宽', 'INT'),
            ('首周鲜肉品宽', 'INT'),
            ('首周冻肉品宽', 'INT'),
            ('首周蔬菜品宽', 'INT'),
            ('首周冷冻半成品品宽', 'INT'),
            ('首周速食熟食品宽', 'INT'),
            ('首周标品品宽', 'INT'),
            ('首周生鲜品宽', 'INT'),
            ('首周冻品品宽', 'INT'),
            ('首周下单天数', 'INT'),
            ('次周下单天数', 'INT'),
            ('次周冻品下单天数', 'INT'),
            ('次周品宽', 'INT'),
            ('次周大米四级品宽', 'INT'),
            ('次周鲜肉品宽', 'INT'),
            ('次周冻肉品宽', 'INT'),
            ('次周冷冻半成品品宽', 'INT'),
            ('次周速食熟食品宽', 'INT'),
            ('次周冻品品宽', 'INT'),
            ('14天品宽', 'INT'),
            ('14天冻品品宽', 'INT'),
            ('28天销售额', 'DECIMAL(10, 2)'),
            ('28天生鲜销售额', 'DECIMAL(10, 2)'),
            ('28天米销售额', 'DECIMAL(10, 2)'),
            ('28天蔬菜销售额', 'DECIMAL(10, 2)'),
            ('28天鲜肉销售额', 'DECIMAL(10, 2)'),
            ('28天冻肉销售额', 'DECIMAL(10, 2)'),
            ('28天冷冻半成品销售额', 'DECIMAL(10, 2)'),
            ('28天速食熟食销售额', 'DECIMAL(10, 2)'),
            ('28天标品销售额', 'DECIMAL(10, 2)'),
            ('28天冻品销售额', 'DECIMAL(10, 2)'),
            ('28天下单天数', 'INT'),
            ('28天大米下单天数', 'INT'),
            ('28天鲜肉下单天数', 'INT'),
            ('28天冻肉下单天数', 'INT'),
            ('28天冷冻半成品下单天数', 'INT'),
            ('28天速食熟食下单天数', 'INT'),
            ('28天冻品下单天数', 'INT'),
            ('28天标品下单天数', 'INT'),
            ('28天蔬菜下单天数', 'INT'),
            ('28天生鲜下单天数', 'INT'),
            ('28天品宽', 'INT'),
            ('28天大米四级品宽', 'INT'),
            ('28天鲜肉品宽', 'INT'),
            ('28天冻肉品宽', 'INT'),
            ('28天蔬菜品宽', 'INT'),
            ('28天冷冻半成品品宽', 'INT'),
            ('28天速食熟食品宽', 'INT'),
            ('28天标品品宽', 'INT'),
            ('28天生鲜品宽', 'INT'),
            ('28天冻品品宽', 'INT')
        ],
        'primary_key': '客户id',
        'indexes': [
            {'name': 'idx_customer_id', 'columns': ['客户id'], 'type': 'INDEX'},
            {'name': 'idx_first_order_time', 'columns': ['首单时间'], 'type': 'INDEX'},
            {'name': 'idx_customer_source', 'columns': ['客户来源'], 'type': 'INDEX'},
            {'name': 'idx_bd_info', 'columns': ['当前归属BDmis号', '当前归属BD姓名'], 'type': 'INDEX'},
            {'name': 'uk_customer_id', 'columns': ['客户id'], 'type': 'UNIQUE'}
        ]
    },
    'last_7_days_customer_info': {
        'columns': [
            ('事业部名称', 'VARCHAR(100)'),
            ('分区', 'VARCHAR(100)'),
            ('销售组名称', 'VARCHAR(100)'),
            ('BDM姓名', 'VARCHAR(100)'),
            ('BD_MIS', 'VARCHAR(100)'),
            ('BD姓名', 'VARCHAR(100)'),
            ('客户ID', 'VARCHAR(50) NOT NULL'),
            ('客户名称', 'VARCHAR(100)'),
            ('一级业态', 'VARCHAR(100)'),
            ('二级业态', 'VARCHAR(100)')
        ],
        'primary_key': '客户ID',
        'indexes': [
            # 普通索引
            {'name': 'idx_customer_id', 'columns': ['客户ID'], 'type': 'INDEX'},
            {'name': 'idx_business_unit', 'columns': ['事业部名称'], 'type': 'INDEX'},
            {'name': 'idx_region', 'columns': ['分区'], 'type': 'INDEX'},
            {'name': 'idx_sales_group', 'columns': ['销售组名称'], 'type': 'INDEX'},
            {'name': 'idx_bdm_name', 'columns': ['BDM姓名'], 'type': 'INDEX'},
            {'name': 'idx_bd_mis', 'columns': ['BD_MIS'], 'type': 'INDEX'},
            {'name': 'idx_bd_name', 'columns': ['BD姓名'], 'type': 'INDEX'},
            {'name': 'idx_customer_name', 'columns': ['客户名称'], 'type': 'INDEX'},
            {'name': 'idx_business_type_l1', 'columns': ['一级业态'], 'type': 'INDEX'},
            {'name': 'idx_business_type_l2', 'columns': ['二级业态'], 'type': 'INDEX'},
            {'name': 'idx_stat_date', 'columns': ['统计日期'], 'type': 'INDEX'},
            # 复合索引
            {'name': 'idx_region_sales_group', 'columns': ['分区', '销售组名称'], 'type': 'INDEX'},
            {'name': 'idx_bdm_bd', 'columns': ['BDM姓名', 'BD姓名'], 'type': 'INDEX'},
            {'name': 'idx_customer_business', 'columns': ['客户ID', '一级业态'], 'type': 'INDEX'},
            {'name': 'idx_business_types', 'columns': ['一级业态', '二级业态'], 'type': 'INDEX'},
            {'name': 'idx_customer_date', 'columns': ['客户ID', '统计日期'], 'type': 'INDEX'},
            # 唯一索引
            {'name': 'uk_id', 'columns': ['客户ID'], 'type': 'UNIQUE'},
            {'name': 'uk_customer_date', 'columns': ['客户ID', '统计日期'], 'type': 'UNIQUE'}
        ]
    },
    'visit_record': {
        'columns': [
            ('Id', 'INT NOT NULL AUTO_INCREMENT'),
            ('城市', 'VARCHAR(50)'),
            ('拜访对象', 'VARCHAR(100)'),
            ('客户ID', 'VARCHAR(50)'),
            ('销售区', 'VARCHAR(50)'),
            ('组织', 'VARCHAR(50)'),
            ('mis号', 'VARCHAR(50)'),
            ('拜访人', 'VARCHAR(50)'),
            ('拜访方式', 'VARCHAR(50)'),
            ('拜访目的', 'VARCHAR(100)'),
            ('拜访对象类型', 'VARCHAR(50)'),
            ('拜访详情', 'TEXT'),
            ('拜访日期', 'DATE'),
            ('拜访开始时间', 'TIME'),
            ('拜访结束时间', 'TIME'),
            ('拜访状态', 'VARCHAR(20)'),
            ('管理城市名称', 'VARCHAR(50)'),
            ('拜访目的-结果', 'VARCHAR(100)'),
            ('当日客户登录', 'VARCHAR(10)'),
            ('当日下单', 'VARCHAR(10)'),
            ('是否见kp', 'VARCHAR(10)'),
            ('上次摸需日期', 'DATE NULL'),
            ('注册时间', 'DATE'),
            ('首单时间', 'DATE NULL'),
            ('新客户分层', 'VARCHAR(20)'),
            ('客户生命周期', 'VARCHAR(20)'),
            ('拜访有效状态', 'VARCHAR(20)'),
            ('拜访无效不达标原因', 'VARCHAR(100)'),
            ('线索分层', 'VARCHAR(20)'),
            ('当月有效达标拜访频次', 'INT')
        ],
        'primary_key': 'Id',
        'indexes': [
            # 普通索引
            {'name': 'idx_visit_date', 'columns': ['拜访日期'], 'type': 'INDEX'},
            {'name': 'idx_customer_id', 'columns': ['客户ID'], 'type': 'INDEX'},
            {'name': 'idx_visit_mis', 'columns': ['mis号'], 'type': 'INDEX'},
            
            # 复合索引
            {'name': 'idx_customer_visit_date', 'columns': ['客户ID', '拜访日期'], 'type': 'INDEX'},
            {'name': 'idx_person_date', 'columns': ['拜访人', '拜访日期'], 'type': 'INDEX'},
            {'name': 'idx_city_date', 'columns': ['城市', '拜访日期'], 'type': 'INDEX'},
            {'name': 'idx_visit_time_range', 'columns': ['拜访开始时间', '拜访结束时间'], 'type': 'INDEX'},
            # 唯一索引
            {'name': 'uk_visit_id', 'columns': ['Id'], 'type': 'UNIQUE'}
        ]
    },
    'new_customer_orders': {
        'columns': [
            ('日期', 'BIGINT'),
            ('下单时间', 'TEXT'),
            ('管理城市', 'TEXT'),
            ('分区', 'TEXT'),
            ('销售组', 'TEXT'),
            ('bdm姓名', 'TEXT'),
            ('bd_id', 'BIGINT'),
            ('bd姓名', 'TEXT'),
            ('bd_mis', 'TEXT'),
            ('客户id', 'BIGINT'),
            ('客户名称', 'TEXT'),
            ('客户等级', 'TEXT'),
            ('订单id', 'BIGINT'),
            ('订单类型', 'TEXT'),
            ('spu ID', 'BIGINT'),
            ('spu名称', 'TEXT'),
            ('售卖单元id', 'BIGINT'),
            ('skuid', 'BIGINT'),
            ('规格', 'TEXT'),
            ('sku单价', 'DOUBLE'),
            ('品牌', 'TEXT'),
            ('后台一级类目', 'TEXT'),
            ('后台二级类目', 'TEXT'),
            ('后台三级类目', 'TEXT'),
            ('后台四级类目', 'TEXT'),
            ('售卖件数', 'BIGINT'),
            ('3P售卖件数', 'BIGINT'),
            ('自营售卖件数', 'BIGINT'),
            ('销售额', 'DOUBLE'),
            ('3P销售额', 'DOUBLE'),
            ('自营销售额', 'DOUBLE'),
            ('是否3P新客', 'TEXT'),
            ('3P新客类型', 'TEXT'),
            ('卖家ID', 'BIGINT'),
            ('卖家名称', 'TEXT'),
            ('仓库名称', 'TEXT'),
            ('一级类目首单时间', 'BIGINT'),
            ('二级类目首单时间', 'BIGINT'),
            ('三级类目首单时间', 'BIGINT'),
            ('四级类目首单时间', 'BIGINT'),
            ('新客户分层', 'TEXT'),
            ('客户类型', 'TEXT'),
            ('送达时间', 'TEXT'),
            ('销量（斤）', 'DOUBLE'),
            ('是否风险客户（处置口径）', 'TEXT'),
            ('标记风险客户时间（处置口径）', 'DOUBLE'),
            ('卫星城', 'TEXT'),
            ('首单月份', 'TEXT')
        ],
        'primary_key': '订单id',
        'indexes': [
            # 普通索引
            {'name': 'idx_order_date', 'columns': ['日期'], 'type': 'INDEX'},
            {'name': 'idx_customer_id', 'columns': ['客户id'], 'type': 'INDEX'},
            {'name': 'idx_bd_id', 'columns': ['bd_id'], 'type': 'INDEX'},
            {'name': 'idx_spu_id', 'columns': ['spu ID'], 'type': 'INDEX'},
            {'name': 'idx_sku_id', 'columns': ['skuid'], 'type': 'INDEX'},
            {'name': 'idx_seller_id', 'columns': ['卖家ID'], 'type': 'INDEX'},
            {'name': 'idx_order_type', 'columns': ['订单类型'], 'type': 'INDEX'},
            {'name': 'idx_customer_level', 'columns': ['客户等级'], 'type': 'INDEX'},
            {'name': 'idx_brand', 'columns': ['品牌'], 'type': 'INDEX'},
            {'name': 'idx_category_l1', 'columns': ['后台一级类目'], 'type': 'INDEX'},
            {'name': 'idx_category_l2', 'columns': ['后台二级类目'], 'type': 'INDEX'},
            {'name': 'idx_management_city', 'columns': ['管理城市'], 'type': 'INDEX'},
            {'name': 'idx_sales_group', 'columns': ['销售组'], 'type': 'INDEX'},
            # 复合索引
            {'name': 'idx_customer_date', 'columns': ['客户id', '日期'], 'type': 'INDEX'},
            {'name': 'idx_bd_date', 'columns': ['bd_id', '日期'], 'type': 'INDEX'},
            {'name': 'idx_city_date', 'columns': ['管理城市', '日期'], 'type': 'INDEX'},
            {'name': 'idx_category_date', 'columns': ['后台一级类目', '日期'], 'type': 'INDEX'},
            {'name': 'idx_spu_sku', 'columns': ['spu ID', 'skuid'], 'type': 'INDEX'},
            {'name': 'idx_sales_amount', 'columns': ['销售额', '日期'], 'type': 'INDEX'},
            {'name': 'idx_customer_date_kind4', 'columns': ['客户id', '日期', '后台四级类目'], 'type': 'INDEX'},
            {'name': 'idx_customer_kind1_date', 'columns': ['客户id', '后台一级类目', '日期'], 'type': 'INDEX'},
            # 唯一索引
            {'name': 'uk_order_id', 'columns': ['订单id'], 'type': 'UNIQUE'},
            {'name': 'uk_spu_sku_seller', 'columns': ['spu ID', 'skuid', '卖家ID'], 'type': 'UNIQUE'}
        ]
    },
    'last_week_customer_orders': {
        'columns': [
            ('日期', 'BIGINT'),
            ('客户id', 'BIGINT'),
            ('客户名称', 'TEXT'),
            ('客户等级', 'TEXT'),
            ('管理城市', 'TEXT'),
            ('订单id', 'BIGINT'),
            ('skuid', 'BIGINT'),
            ('后台四级类目', 'TEXT'),
            ('售卖件数', 'BIGINT'),
            ('销售额', 'DOUBLE'),
            ('仓库名称', 'TEXT')
        ],
        'primary_key': '订单id',
        'indexes': [
            # 普通索引
            {'name': 'idx_order_date', 'columns': ['日期'], 'type': 'INDEX'},
            {'name': 'idx_customer_id', 'columns': ['客户id'], 'type': 'INDEX'},
            {'name': 'idx_sku_id', 'columns': ['skuid'], 'type': 'INDEX'},
            {'name': 'idx_category_l2', 'columns': ['后台四级类目'], 'type': 'INDEX'},
            {'name': 'idx_management_city', 'columns': ['管理城市'], 'type': 'INDEX'},
            # 复合索引
            {'name': 'idx_customer_date', 'columns': ['客户id', '日期'], 'type': 'INDEX'},
            {'name': 'idx_city_date', 'columns': ['管理城市', '日期'], 'type': 'INDEX'},
            # 唯一索引
            {'name': 'uk_order_id', 'columns': ['订单id'], 'type': 'UNIQUE'},
            {'name': 'uk_spu_sku_seller', 'columns': ['skuid'], 'type': 'UNIQUE'}
        ]
    }
    # 其他表可继续添加...
}

# 索引类型说明
INDEX_TYPES = {
    'INDEX': '普通索引 - 提高查询性能',
    'UNIQUE': '唯一索引 - 确保字段值唯一性',
    'FULLTEXT': '全文索引 - 用于文本搜索',
    'SPATIAL': '空间索引 - 用于地理数据'
}

# 索引管理函数
def get_table_indexes(table_name):
    """获取指定表的所有索引"""
    if table_name in TABLE_SCHEMAS:
        return TABLE_SCHEMAS[table_name].get('indexes', [])
    return []

def get_index_by_name(table_name, index_name):
    """根据索引名称获取索引信息"""
    indexes = get_table_indexes(table_name)
    for index in indexes:
        if index['name'] == index_name:
            return index
    return None

def get_indexes_by_type(table_name, index_type):
    """根据索引类型获取索引列表"""
    indexes = get_table_indexes(table_name)
    return [index for index in indexes if index['type'] == index_type]

def get_indexes_by_column(table_name, column_name):
    """根据字段名获取相关索引"""
    indexes = get_table_indexes(table_name)
    return [index for index in indexes if column_name in index['columns']]

def generate_create_index_sql(table_name, index_info):
    """生成创建索引的SQL语句"""
    index_type = index_info['type']
    index_name = index_info['name']
    columns = ', '.join(index_info['columns'])
    
    if index_type == 'UNIQUE':
        return f"CREATE UNIQUE INDEX {index_name} ON {table_name} ({columns});"
    elif index_type == 'FULLTEXT':
        return f"CREATE FULLTEXT INDEX {index_name} ON {table_name} ({columns});"
    elif index_type == 'SPATIAL':
        return f"CREATE SPATIAL INDEX {index_name} ON {table_name} ({columns});"
    else:
        return f"CREATE INDEX {index_name} ON {table_name} ({columns});"

def generate_drop_index_sql(table_name, index_name):
    """生成删除索引的SQL语句"""
    return f"DROP INDEX {index_name} ON {table_name};"

def get_all_indexes_sql(table_name):
    """获取表的所有索引创建SQL"""
    indexes = get_table_indexes(table_name)
    sql_statements = []
    for index in indexes:
        sql_statements.append(generate_create_index_sql(table_name, index))
    return sql_statements

def validate_index_config(table_name):
    """验证索引配置的合理性"""
    if table_name not in TABLE_SCHEMAS:
        return False, f"表 {table_name} 不存在"
    
    table_info = TABLE_SCHEMAS[table_name]
    indexes = table_info.get('indexes', [])
    column_names = [col[0] for col in table_info['columns']]
    
    errors = []
    
    for index in indexes:
        # 检查索引字段是否存在
        for column in index['columns']:
            if column not in column_names:
                errors.append(f"索引 {index['name']} 中的字段 {column} 不存在于表中")
        
        # 检查索引名称是否重复
        index_names = [idx['name'] for idx in indexes]
        if index_names.count(index['name']) > 1:
            errors.append(f"索引名称 {index['name']} 重复")
    
    return len(errors) == 0, errors 