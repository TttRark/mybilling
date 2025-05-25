# 个人记账系统

这是一个基于Flask的个人记账系统，支持多账本管理、交易记录、数据导入导出等功能。

## 功能特点

- 用户认证（注册、登录、登出）
- 多账本管理
- 交易记录管理（收入/支出）
- 数据导入导出（Excel格式）
- 响应式界面设计

## 技术栈

- Python 3.8+
- Flask 3.0.0
- SQLAlchemy
- Flask-Login
- Flask-WTF
- Pandas
- Bootstrap 5
- PyMySQL

## 安装说明

1. 克隆项目到本地：
```bash
git clone [项目地址]
cd mybilling_flask
```

2. 创建虚拟环境并激活：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
创建 `.env` 文件并添加以下配置：
```
SECRET_KEY=your-secret-key
DATABASE_URL=mysql+pymysql://数据库用户:数据用户密码@数据库地址:数据库端口/数据库
```

5. 初始化数据库：
```bash
mysql -uroot -pxxxx < doc/database.sql
```

6. 运行应用：
```bash
python app.py
```

## 使用说明

1. 访问 http://localhost:5000 进入应用
2. 注册新用户或使用已有账号登录
3. 创建账本并开始记录交易
4. 使用导入/导出功能管理数据

## 项目结构

```
mybilling_flask/
├── app.py              # 应用入口
├── config.py           # 配置文件
├── models.py           # 数据模型
├── requirements.txt    # 项目依赖
├── forms/             # 表单类
│   ├── auth.py
│   ├── ledger.py
│   └── transaction.py
├── routes/            # 路由处理
│   ├── auth.py
│   ├── ledger.py
│   ├── transaction.py
├── static/            # 静态文件
├── templates/         # 模板文件
└── temp/             # 临时文件目录
```

## 数据库结构

### User 表
- id: 主键
- username: 用户名
- email: 邮箱
- password_hash: 密码哈希
- created_at: 创建时间

### Ledger 表
- id: 主键
- name: 账本名称
- description: 描述
- user_id: 用户外键
- created_at: 创建时间

### Transaction 表
- id: 主键
- amount: 金额
- description: 描述
- category: 分类
- transaction_type: 交易类型（收入/支出）
- date: 交易日期
- ledger_id: 账本外键
- created_at: 创建时间

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License 