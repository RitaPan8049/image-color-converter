"""
WSGI 配置文件 - 用于 PythonAnywhere 部署
"""
import sys
import os

# 添加项目路径
project_home = '/home/yourusername/image-color-converter'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# 导入 Flask 应用
from app import app as application
