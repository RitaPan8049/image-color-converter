#!/usr/bin/env python3
"""
图片格式转换工具：将 JPG 转换为只有 3 种主要颜色的 BMP 格式
"""

from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import sys
import os


def extract_main_colors(image_array, n_colors=3):
    """
    使用 K-means 聚类提取图片中的主要颜色

    Args:
        image_array: numpy 数组格式的图片数据
        n_colors: 要提取的主要颜色数量

    Returns:
        主要颜色的中心点（RGB 值）
    """
    # 将图片数据重塑为二维数组 (像素数, 3)
    pixels = image_array.reshape(-1, 3)

    # 使用 K-means 聚类找出主要颜色
    kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
    kmeans.fit(pixels)

    # 返回聚类中心（主要颜色）
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

    # 为每个像素找到最接近的主要颜色
    distances = np.zeros((pixels.shape[0], len(main_colors)))
    for i, color in enumerate(main_colors):
        distances[:, i] = np.linalg.norm(pixels - color, axis=1)

    # 获取最近颜色的索引
    closest_color_indices = np.argmin(distances, axis=1)

    # 将像素映射到主要颜色
    new_pixels = main_colors[closest_color_indices]

    # 重塑回原始图片形状
    return new_pixels.reshape(height, width, channels)


def convert_jpg_to_bmp_3colors(input_path, output_path=None):
    """
    将 JPG 图片转换为只有 3 种主要颜色的 BMP 格式

    Args:
        input_path: 输入的 JPG 文件路径
        output_path: 输出的 BMP 文件路径（可选）

    Returns:
        输出文件路径
    """
    # 检查输入文件是否存在
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"输入文件不存在: {input_path}")

    # 如果没有指定输出路径，自动生成
    if output_path is None:
        base_name = os.path.splitext(input_path)[0]
        output_path = f"{base_name}_3colors.bmp"

    print(f"正在读取图片: {input_path}")

    # 读取图片
    image = Image.open(input_path)

    # 如果是 RGBA 模式，转换为 RGB
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    elif image.mode != 'RGB':
        image = image.convert('RGB')

    # 转换为 numpy 数组
    image_array = np.array(image)

    print("正在提取 3 种主要颜色...")

    # 提取 3 种主要颜色
    main_colors = extract_main_colors(image_array, n_colors=3)

    print("主要颜色 (RGB):")
    for i, color in enumerate(main_colors):
        print(f"  颜色 {i+1}: RGB({color[0]}, {color[1]}, {color[2]})")

    print("正在将像素映射到主要颜色...")

    # 将所有像素映射到主要颜色
    new_image_array = map_to_main_colors(image_array, main_colors)

    # 转换回 PIL 图片
    new_image = Image.fromarray(new_image_array.astype('uint8'))

    print(f"正在保存为 BMP 格式: {output_path}")

    # 保存为 BMP 格式
    new_image.save(output_path, 'BMP')

    print(f"转换完成！输出文件: {output_path}")

    return output_path


def main():
    """主函数：处理命令行参数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print(f"  python {sys.argv[0]} <输入JPG文件> [输出BMP文件]")
        print()
        print("示例:")
        print(f"  python {sys.argv[0]} photo.jpg")
        print(f"  python {sys.argv[0]} photo.jpg output.bmp")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        convert_jpg_to_bmp_3colors(input_path, output_path)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
