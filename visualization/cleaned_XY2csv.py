import os
import csv

import sys
sys.path.append("../")

# 文件夹路径
folder_path = '../data/cleaned_data/Porto/cleaned_Porto'

# 存储所有经度和纬度的列表
coordinates = []

n = 10000

# 遍历文件夹
for file_name in os.listdir(folder_path):
    if file_name.endswith('.txt'):  # 假设文件都是.txt格式
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith('#'):
                    continue
                # 假设经纬度在第2列和第3列
                parts = line.strip().split(',')
                if len(parts) >= 3:
                    try:
                        latitude = float(parts[1])
                        longitude = float(parts[2])
                        coordinates.append((longitude, latitude))
                        # 检查是否达到了需要写入的行数
                        if len(coordinates) >= n:
                            break
                    except ValueError:
                        # 如果转换失败，则忽略该行
                        continue

print(f"Total coordinates extracted: {len(coordinates)}")

# 将经度和纬度写入CSV文件
output_file = 'coordinates.csv'
with open(output_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['X', 'Y'])  # 标题行
    writer.writerows(coordinates)

print("Coordinates saved to", output_file)
