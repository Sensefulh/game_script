import os

# 设置要修改文件名的目录
directory = r'D:\python以及各种实验代码\脚本\计算机22-7班就业指导'  # 替换为你的文件夹路径

# 获取文件列表并排序
files = os.listdir(directory)
files.sort()

# 定义起始序号
start_index = 2022304449

# 遍历文件并重命名
for file in files:
    # 获取完整路径
    old_file_path = os.path.join(directory, file)

    # 检查是否是ZIP文件
    if file.endswith('.zip'):
        # 提取姓名部分（假设姓名在文件名的最后部分）
        name_part = file.split('-')[-1].replace('.zip', '').strip()

        # 生成新的文件名
        new_file_name = f"{start_index}-计算机22-7-{name_part}.zip"
        new_file_path = os.path.join(directory, new_file_name)

        # 重命名文件
        os.rename(old_file_path, new_file_path)
        print(f"重命名: {file} -> {new_file_name}")

        # 序号递增
        start_index += 1
