# 王小明智能对话系统

基于DeepSeek API的智能对话系统，提供简洁的Web界面进行交互。

## 快速开始

1. 创建并激活虚拟环境：
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行应用：
```bash
python app.py
```

4. 访问 http://localhost:5000 开始对话

## 目录结构
```
wangxiaoming/
├── .env                 # 环境变量配置文件
├── static/             
│   └── css/            # 样式文件
│   └── js/             # JavaScript文件
├── templates/
│   └── index.html      # 主页面
├── app.py              # Flask应用主文件
├── requirements.txt     # 项目依赖
└── README.md           # 项目说明
```
