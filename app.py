#!/usr/bin/env python3
"""
Flask 网页应用：JPG 到 BMP 转换器（3 种颜色）
"""

from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import os
import io

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 最大 16MB

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_main_colors(image_array, n_colors=3):
    """
    使用 K-means 聚类提取图片中的主要颜色

    Args:
        image_array: numpy 数组格式的图片数据
        n_colors: 要提取的主要颜色数量

    Returns:
        主要颜色的中心点（RGB 值）
    """
    pixels = image_array.reshape(-1, 3)
    kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
    kmeans.fit(pixels)
    return kmeans.cluster_centers_.astype(int)


def map_to_main_colors(image_array, main_colors):
    """
    将图片中的所有像素映射到最接近的主要颜色

    Args:
        image_array: numpy 数组格式的图片数据
        main_colors: 主要颜色数组

    Returns:
        映射后的图片数组
    """
    height, width, channels = image_array.shape
    pixels = image_array.reshape(-1, 3)

    distances = np.zeros((pixels.shape[0], len(main_colors)))
    for i, color in enumerate(main_colors):
        distances[:, i] = np.linalg.norm(pixels - color, axis=1)

    closest_color_indices = np.argmin(distances, axis=1)
    new_pixels = main_colors[closest_color_indices]

    return new_pixels.reshape(height, width, channels)


def process_image(image_file, n_colors=3):
    """
    处理上传的图片

    Args:
        image_file: 上传的文件对象
        n_colors: 要提取的颜色数量

    Returns:
        (处理后的图片字节流, 主要颜色列表)
    """
    # 读取图片
    image = Image.open(image_file)

    # 转换为 RGB
    if image.mode == 'RGBA':
        # 创建白色背景
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])  # 使用 alpha 通道作为蒙版
        image = background
    elif image.mode != 'RGB':
        image = image.convert('RGB')

    # 转换为 numpy 数组
    image_array = np.array(image)

    # 提取主要颜色
    main_colors = extract_main_colors(image_array, n_colors=n_colors)

    # 映射到主要颜色
    new_image_array = map_to_main_colors(image_array, main_colors)

    # 转换回 PIL 图片
    new_image = Image.fromarray(new_image_array.astype('uint8'))

    # 保存到字节流
    img_io = io.BytesIO()
    new_image.save(img_io, 'BMP')
    img_io.seek(0)

    # 转换颜色为十六进制格式
    color_list = [
        {
            'rgb': f'RGB({color[0]}, {color[1]}, {color[2]})',
            'hex': f'#{color[0]:02x}{color[1]:02x}{color[2]:02x}'
        }
        for color in main_colors
    ]

    return img_io, color_list


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert():
    """处理图片转换请求"""
    if 'file' not in request.files:
        flash('没有选择文件', 'error')
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        flash('没有选择文件', 'error')
        return redirect(url_for('index'))

    if not allowed_file(file.filename):
        flash('不支持的文件格式，请上传 PNG、JPG、JPEG、GIF 或 BMP 文件', 'error')
        return redirect(url_for('index'))

    try:
        # 获取颜色数量（默认 3）
        n_colors = int(request.form.get('n_colors', 3))
        if n_colors < 2 or n_colors > 10:
            n_colors = 3

        # 处理图片
        img_io, colors = process_image(file, n_colors=n_colors)

        # 生成输出文件名
        original_filename = secure_filename(file.filename)
        base_name = os.path.splitext(original_filename)[0]
        output_filename = f'{base_name}_{n_colors}colors.bmp'

        # 将颜色信息存储在会话中（可选）
        # 这里我们直接返回文件
        return send_file(
            img_io,
            mimetype='image/bmp',
            as_attachment=True,
            download_name=output_filename
        )

    except Exception as e:
        flash(f'处理图片时出错: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/preview', methods=['POST'])
def preview():
    """预览转换效果"""
    if 'file' not in request.files:
        return {'error': '没有选择文件'}, 400

    file = request.files['file']

    if file.filename == '':
        return {'error': '没有选择文件'}, 400

    if not allowed_file(file.filename):
        return {'error': '不支持的文件格式'}, 400

    try:
        # 获取颜色数量
        n_colors = int(request.form.get('n_colors', 3))
        if n_colors < 2 or n_colors > 10:
            n_colors = 3

        # 处理图片
        img_io, colors = process_image(file, n_colors=n_colors)

        # 返回预览数据
        return {
            'success': True,
            'colors': colors,
            'message': f'成功提取 {n_colors} 种主要颜色'
        }

    except Exception as e:
        return {'error': str(e)}, 500


if __name__ == '__main__':
    import os

    # 获取环境变量，如果在生产环境（如 Render）会有 PORT 环境变量
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') != 'production'

    print("=" * 60)
    print("图片转换工具 - 网页版")
    print("=" * 60)
    print("服务器启动中...")
    if debug:
        print(f"请在浏览器中打开: http://localhost:{port}")
    print("按 Ctrl+C 停止服务器")
    print("=" * 60)

    app.run(debug=debug, host='0.0.0.0', port=port)
