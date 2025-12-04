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


# 示例用法
if __name__ == "__main__":
    # 示例1: 覆盖原文件
    # remove_first_9_bytes_if_zero("test.bin")
    
    # 示例2: 保存到新文件
    # remove_first_9_bytes_if_zero("test.bin", "test_modified.bin")
    
    # 示例3: 测试函数
    # 创建一个测试文件
    test_data = b'000000000Hello World!'  # 前9个字节是'0'
    with open("test.bin", "wb") as f:
        f.write(test_data)
    
    print("创建测试文件 test.bin")
    print("文件内容前9个字节:", test_data[:9])
    
    # 调用函数
    result = remove_first_9_bytes_if_zero("test.bin", "test_modified.bin")
    
    # 验证结果
    if result:
        with open("test_modified.bin", "rb") as f:
            modified_data = f.read()
        print("修改后的文件内容:", modified_data)