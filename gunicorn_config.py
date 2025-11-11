"""Gunicorn 配置文件 - 用于生产环境"""
import multiprocessing

# 监听地址
bind = "0.0.0.0:8080"

# Worker 进程数
workers = multiprocessing.cpu_count() * 2 + 1

# Worker 类型
worker_class = "sync"

# 超时时间（秒）
timeout = 120

# 访问日志
accesslog = "-"

# 错误日志
errorlog = "-"

# 日志级别
loglevel = "info"
