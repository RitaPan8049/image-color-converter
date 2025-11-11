#!/usr/bin/env python3
"""创建一个测试图片"""
from PIL import Image, ImageDraw
import numpy as np

# 创建一个彩色测试图片
width, height = 400, 300
image = Image.new('RGB', (width, height))
draw = ImageDraw.Draw(image)

# 绘制不同颜色的区域（包含多种相近的颜色）
# 红色系区域
for i in range(50):
    color = (200 + np.random.randint(-30, 30),
             50 + np.random.randint(-30, 30),
             50 + np.random.randint(-30, 30))
    draw.rectangle([np.random.randint(0, 150), np.random.randint(0, 150),
                    np.random.randint(0, 150) + 30, np.random.randint(0, 150) + 30],
                   fill=color)

# 蓝色系区域
for i in range(50):
    color = (50 + np.random.randint(-30, 30),
             100 + np.random.randint(-30, 30),
             200 + np.random.randint(-30, 30))
    draw.rectangle([np.random.randint(200, 350), np.random.randint(0, 150),
                    np.random.randint(200, 350) + 30, np.random.randint(0, 150) + 30],
                   fill=color)

# 绿色系区域
for i in range(50):
    color = (50 + np.random.randint(-30, 30),
             180 + np.random.randint(-30, 30),
             80 + np.random.randint(-30, 30))
    draw.rectangle([np.random.randint(100, 300), np.random.randint(150, 270),
                    np.random.randint(100, 300) + 30, np.random.randint(150, 270) + 30],
                   fill=color)

# 保存为 JPG
image.save('test_image.jpg', 'JPEG', quality=95)
print("测试图片已创建: test_image.jpg")
