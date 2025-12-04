#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
bili_convert.py
用于处理Bilibili下载的.m4s文件，删除前9个字节的'0'字符（如果存在），并使用FFmpeg合并为MP4文件。
"""

import os
import json
import re
import subprocess
from pathlib import Path


def remove_first_9_bytes_if_zero(input_file, output_file=None):
    """
    读取二进制文件，如果前9个字节都是字符'0'，则删除它们并保存剩余部分
    
    参数:
    input_file: 输入文件路径
    output_file: 输出文件路径（如果为None，则覆盖原文件）
    
    返回:
    bool: 是否成功删除了前9个字节
    """
    try:
        # 读取输入文件
        with open(input_file, 'rb') as f:
            data = f.read()
        
        # 检查文件大小是否至少有9个字节
        if len(data) < 9:
            print(f"文件大小小于9字节，无法判断前9个字节")
            return False
        
        # 检查文件名是否.m4s
        if not input_file.lower().endswith('.m4s'):
            print("文件扩展名不是.m4s，跳过处理")
            return False
        
        # 检查前9个字节是否都是字符'0'（ASCII码为48）
        # 字符'0'的二进制表示为0x30
        is_all_zero = all(byte == 0x30 for byte in data[:9])
        
        if is_all_zero:
            print("前9个字节都是字符'0'，正在删除...")
            # 删除前9个字节
            new_data = data[9:]
            
            # 确定输出文件路径
            if output_file is None:
                output_file = input_file
            
            # 写入输出文件
            with open(output_file, 'wb') as f:
                f.write(new_data)
            
            print(f"已删除前9个字节，原文件大小: {len(data)}字节，新文件大小: {len(new_data)}字节")
            return True
        else:
            print("前9个字节不全是字符'0'，不进行删除操作")
            
            # 如果指定了输出文件且不是覆盖原文件，则复制文件
            if output_file and output_file != input_file:
                with open(output_file, 'wb') as f:
                    f.write(data)
                print(f"已复制文件到: {output_file}")
            
            return False
            
    except FileNotFoundError:
        print(f"错误: 文件 '{input_file}' 未找到")
        return False
    except Exception as e:
        print(f"处理文件时发生错误: {e}")
        return False


def merge_m4s_to_mp4_with_ffmpeg(m4s_files, title, groupTitle, output_path):
    """
    使用FFmpeg合并多个.m4s文件为一个MP4文件
    
    参数:
        m4s_files: .m4s文件列表
        output_path: 输出MP4文件路径
    """
    if len(m4s_files) < 2:
        print("需要至少两个.m4s文件进行合并")
        return False
    # 假设第一个.m4s文件是视频，第二个是音频
    videofile = m4s_files[0]
    audiofile = m4s_files[1]

    if not os.path.exists(videofile):
        print(f"视频文件不存在: {videofile}")
        return False

    if not os.path.exists(audiofile):
        print(f"音频文件不存在: {audiofile}")
        return False
    
    if not title:
        print("标题为空，无法继续合并")
        return False
    
    # 构建输出文件路径
    if not groupTitle or groupTitle == title:
        output_path = os.path.join(output_path, f"{title}.mp4")
    else:
        output_path = os.path.join(output_path, groupTitle, f"{title}.mp4")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        # 构建FFmpeg命令
        # -f concat: 指定使用concat解复用器
        # -safe 0: 允许使用所有文件名
        # -c copy: 流复制模式，不重新编码
        cmd = [
            'ffmpeg',
            '-i', videofile,
            '-i', audiofile,
            '-c', 'copy',  # 复制所有流而不重新编码
            '-y',  # 覆盖已存在的输出文件
            output_path
        ]
        
        print(f"    执行FFmpeg命令: {' '.join(cmd)}")
        
        # 执行FFmpeg命令
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"    ✓ 成功合并为: {os.path.basename(output_path)}")
            # 检查输出文件大小
            if os.path.exists(output_path):
                size = os.path.getsize(output_path) / (1024 * 1024)  # 转换为MB
                print(f"    输出文件大小: {size:.2f} MB")
            return True
        else:
            print(f"    ✗ FFmpeg合并失败:")
            print(f"      错误输出: {result.stderr[:500]}")  # 只显示前500字符
            return False
            
    except subprocess.TimeoutExpired:
        print("    ✗ FFmpeg执行超时")
        return False
    except Exception as e:
        print(f"    ✗ 执行FFmpeg时出错: {e}")
        return False


def read_json_data(json_file_path):
    """
    读取JSON文件并提取title和groupTitle字段
    
    参数:
    json_file_path: JSON文件路径
    
    返回:
    tuple: (title, groupTitle) 如果成功读取，否则返回(None, None)
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        title = data.get('title', '')
        group_title = data.get('groupTitle', '')
        
        print(f"  读取JSON数据:")
        print(f"    标题: {title}")
        print(f"    组标题: {group_title}")
        
        return title, group_title
    except Exception as e:
        print(f"  读取JSON文件时发生错误: {e}")
        return None, None


def process_directory(base_dir, output_path=None):
    """
    处理指定目录下的所有数字子目录
    
    参数:
    base_dir: 基础目录路径
    """
    print(f"开始处理目录: {base_dir}")
    
    if output_path is None:
        output_path = os.path.join(base_dir, "bili_video_output")
        os.makedirs(output_path, exist_ok=True)

    # 获取基础目录下的所有子目录
    try:
        items = os.listdir(base_dir)
    except Exception as e:
        print(f"无法读取目录 {base_dir}: {e}")
        return
    
    for item in items:
        item_path = os.path.join(base_dir, item)
        
        # 检查是否为目录且名称为数字
        if os.path.isdir(item_path) and re.fullmatch(r'\d+', item):
            print(f"处理子目录: {item_path}")
            
            # 读取JSON文件
            json_file_path = os.path.join(item_path, 'videoInfo.json')
            title, group_title = read_json_data(json_file_path)
            
            # 处理.m4s文件
            m4s_list = []
            for file_name in os.listdir(item_path):
                if file_name.lower().endswith('.m4s'):
                    m4s_file_path = os.path.join(item_path, file_name)
                    m4s_list.append(m4s_file_path)
                    print(f"  处理文件: {m4s_file_path}")
                    remove_first_9_bytes_if_zero(m4s_file_path)
            # 调用合并函数
            merge_m4s_to_mp4_with_ffmpeg(m4s_list, title, group_title, output_path)
        else:
            print(f"跳过非数字目录或文件: {item_path}")
    print("目录处理完成。")


def test():
    # 示例1: 覆盖原文件
    # remove_first_9_bytes_if_zero("test.bin")
    
    # 示例2: 保存到新文件
    # remove_first_9_bytes_if_zero("test.bin", "test_modified.bin")
    
    # 示例3: 测试函数
    # 创建一个测试文件
    test_data = b'000000000Hello World!'  # 前9个字节是'0'
    file_name = "test_data/test.m4s"
    with open(file_name, "wb") as f:
        f.write(test_data)
    
    print("创建测试文件 test.m4s")
    print("文件内容前9个字节:", test_data[:9])
    
    # 调用函数
    result = remove_first_9_bytes_if_zero(file_name, file_name+"_modified")
    
    # 验证结果
    if result:
        with open(file_name+"_modified", "rb") as f:
            modified_data = f.read()
        print("修改后的文件内容:", modified_data)


# 示例用法
if __name__ == "__main__":
    if len(os.sys.argv) == 2:
        base_directory = os.sys.argv[1]
    else:
        base_directory = "."  # 默认当前目录
    process_directory(base_directory)