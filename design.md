# 王小明智能体设计文档

## 1. 系统概述

### 1.1 核心说明
王小明是一个基于 DeepSeek Chat API 的对话系统。他的人设是一个25岁的年轻人，性格热情、好奇、犀利而幽默，喜欢科技、音乐、电影和美食。他用年轻人的方式与人交流，善于使用流行语和生动的比喻。

### 1.2 系统架构
- 前端：HTML + JavaScript（原生实现）
- 后端：Python + Flask
- AI模型：DeepSeek API
- 环境管理：Python虚拟环境
- 配置管理：JSON配置文件

## 2. 技术实现

### 2.1 目录结构
```
wangxiaoming/
├── .env                 # 环境变量配置文件（包含API密钥）
├── config/             
│   └── persona.json    # 人设配置文件
├── static/             
│   ├── css/            # 样式文件
│   │   └── style.css   # 主样式文件
│   └── js/             # JavaScript文件
│       └── main.js     # 主交互逻辑
├── templates/
│   └── index.html      # 主页面模板
├── app.py              # Flask应用主文件
├── requirements.txt     # 项目依赖
├── README.md           # 项目说明
└── design.md           # 设计文档
```

### 2.2 组件说明

#### 2.2.1 后端实现 (app.py)
- Flask Web框架
- 两个主要路由：
  - GET `/`: 返回主页
  - POST `/chat`: 处理对话请求
- DeepSeek API集成
  - 使用环境变量管理API密钥
  - 支持异步对话处理
  - 错误处理机制
- 人设管理
  - 从配置文件加载人设
  - 维护对话上下文
  - 动态系统提示

#### 2.2.2 人设配置 (persona.json)
- 基础信息：姓名、年龄
- 性格特征：热情、好奇、犀利、幽默
- 兴趣爱好：科技、音乐、电影、美食
- 对话风格：
  - 口语化表达
  - 网络流行语
  - 适时幽默
  - 生动比喻
- 系统提示：完整的人设引导提示

#### 2.2.3 前端实现
- **HTML (index.html)**
  - 响应式布局
  - 简洁的聊天界面
  - 消息输入区域
  
- **CSS (style.css)**
  - 现代化UI设计
  - 响应式布局支持
  - 消息气泡样式
  - 交互状态样式

- **JavaScript (main.js)**
  - 异步消息发送
  - 实时消息显示
  - 错误处理
  - 用户体验优化（输入控制、滚动等）

### 2.3 依赖要求
- Python 3.8+
- Flask==3.0.2
- python-dotenv==1.0.1
- requests==2.31.0

## 3. 部署和运行

### 3.1 环境配置
1. 创建虚拟环境：
```bash
python -m venv venv
```

2. 激活虚拟环境：
```bash
# Windows
venv\Scripts\activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

### 3.2 运行说明
1. 确保虚拟环境已激活
2. 运行Flask应用：
```bash
python app.py
```
3. 访问 http://localhost:5000 开始对话

## 4. 安全性考虑
1. 所有敏感信息通过环境变量管理
2. API密钥保护
3. 错误信息处理
4. 输入验证和清理

## 5. 注意事项
- 请勿将包含敏感信息的.env文件提交到版本控制系统
- 可以根据需要修改persona.json来调整王小明的人设
- 建议定期更新依赖包以获取安全更新
- 在生产环境部署时，请确保使用安全的HTTPS连接
