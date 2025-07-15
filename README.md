# MySQL 数据批量导入与灵活导出工具集

如果你面临以下问题:
1、需要处理的原始数据已经超百万行,Excel难以胜任,power query又性能堪忧。
2、想使用/学习SQL，又没有线上环境。
欢迎使用这个项目！

对于学习者来说，项目可以帮你生成一个本地的SQL环境，你可以自由编写增删改查语句，不用担心造成不可逆影响。
对于业务操作者来说，excel转化到数据库再回到excel的过程实属无奈之举，但如果你的公司不给你开放SQL权限，而你又不得不处理超大量的数据，你可以通过本项目节约大量时间。

本项目是一套支持 MySQL 数据批量导入、灵活导出、SQL文件化管理的自动化工具集，适合数据分析、报表开发、数据同步等多种场景。

---

## 目录结构

```
├── src/
│   ├── importers/          # 数据导入模块（Excel/CSV→MySQL）
│   ├── exporters/          # 数据导出模块（MySQL→Excel）
│   ├── shared/             # 配置、表结构等共享组件
│   └── scripts/            # 各类命令行脚本
├── sql_queries/            # SQL查询文件（按业务模块分类）
├── tests/                  # 测试脚本
├── data/                   # 数据目录（导入/导出文件）
├── docs/                   # 专题文档
├── requirements.txt        # 依赖包
├── run_export.bat          # 一键启动菜单
└── README.md               # 项目说明
```

---

## 主要功能

### 1. 数据导入
- 支持 Excel/CSV 批量导入 MySQL
- 表结构自动同步（自动建表/加字段/删字段/类型变更）
- 支持增量导入、清空重传等多种更新策略
- 支持大文件分块导入，内存友好
- 数据源、表结构、导入策略集中配置

### 2. 数据导出
- 支持自定义 SQL 查询导出为 Excel
- 支持参数化查询、命名查询、批量导出
- 支持命令行参数、脚本调用、批处理
- 支持多查询导出到同一 Excel 多工作表
- 输出路径、文件名、工作表名灵活可配

### 3. SQL 文件化管理
- 所有 SQL 查询集中存放于 `sql_queries/`，按业务模块分类
- 查询命名规范，支持参数化
- 可视化 SQL 查询查看器，便于维护和扩展
- 详见 [`docs/README_SQL文件管理系统.md`](docs/README_SQL文件管理系统.md)

### 4. 配置管理
- 数据库连接、数据源路径、表结构、导入策略等集中配置
- 支持多表多源灵活扩展

---

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置数据库和数据源
编辑 `src/shared/config.py`，配置数据库连接、数据源路径、导入策略等。

### 3. 数据导入
- 批量导入所有表：
  ```bash
  python src/importers/db_importer.py
  ```
- 导入指定表：
  ```bash
  python src/importers/db_importer.py 表名
  ```
- Excel 批量转 CSV：
  ```bash
  python src/importers/xlsx_to_csv.py
  ```

### 4. 数据导出
- 快速导出（命名查询/参数化）：
  ```bash
  python src/scripts/quick_export.py 查询名 [参数1=值1 ...] [--output 文件名] [--sheet 工作表名]
  ```
- 批量导出：
  ```bash
  python src/scripts/batch_export.py
  ```
- SQL 查询查看器：
  ```bash
  python src/scripts/sql_viewer.py
  ```

### 5. 一键菜单
```bash
run_export.bat
```

---

## 命令行用法
详见 [`docs/命令行使用说明.md`](docs/命令行使用说明.md)

---

## SQL 文件管理说明
详见 [`docs/README_SQL文件管理系统.md`](docs/README_SQL文件管理系统.md)

---

## 配置说明
- 数据库配置、数据源配置、表结构说明详见 `src/shared/config.py`、`src/shared/table_schemas.py`
- 更新策略详见 [`docs/更新策略配置说明.md`](docs/更新策略配置说明.md)

---

## 常见问题与故障排查
- 数据库连接失败、SQL错误、导入导出失败、编码问题等，详见主README和各专题文档。
- 日志文件：`db_export.log`，详细记录所有操作和错误。

---

## 测试
- 运行测试脚本验证导出功能：
  ```bash
  python tests/test_export.py
  ```

---

## 附录
- 详细表结构说明：[`docs/数据库表结构说明.md`](docs/数据库表结构说明.md)
- 开发备忘录：`docs/开发备忘录.md`

---

如需详细功能说明、SQL管理、命令行用法、表结构、导入策略等，请查阅 `docs/` 目录下的各专题文档。

**欢迎反馈建议与贡献！** 
