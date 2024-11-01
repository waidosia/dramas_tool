# 短剧发种工具


## 目录结构
```bash
├── app
│   ├── api              // 接口
│   │   ├── __init__.py  // 在这里对蓝图统一导出
│   │   ├── admin.py
│   │   └── user.py
│   ├── models           // 数据库模型
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services     // 服务可以在这里写
│   │   ├── __init__.py
│   │   └── services.py
│   ├── static
│   ├── templates
│   ├── __init__.py 
│   ├── config.py       // 项目配置项
│   └── extension.py    // 拓展实例化
├── manage.py           // 在这里实例化 flask
├── requirements.txt    // 拓展版本管理文件
└── README.md
```


## 实现功能
