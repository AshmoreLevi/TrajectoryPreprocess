"""
Convert the CSV data of Porto into TXT data for cleaning.
"""
import os
import pandas as pd
import ast
from datetime import datetime, timedelta
from tqdm import tqdm

# 读取CSV文件
df = pd.read_csv('data/csv_data/train.csv')
print('读取csv结束')

# 定义目录路径和文件夹名称
base_dir = 'data/raw_data/Porto'
folder_name = 'porto_by_id'

print('开始转化')
# 选择需要的属性
selected_columns = ['TAXI_ID', 'TIMESTAMP', 'POLYLINE']
df_selected = df[selected_columns].copy()  # 创建一个副本
print('创建副本成功')

# 创建一个字典，用于按照taxi_id分组存储数据
taxi_data_dict = {}

# 使用tqdm来添加进度条
for index, row in tqdm(df_selected.iterrows(), total=len(df_selected)):
    taxi_id = row['TAXI_ID']
    polyline_str = row['POLYLINE']

    try:
        # 尝试将POLYLINE列的字符串转换为列表
        polyline = ast.literal_eval(polyline_str)
    except (ValueError, SyntaxError):
        # 捕获异常并跳过当前数据点
        continue

    # 获取时间戳并递增15秒
    timestamp = row['TIMESTAMP']
    timestamp = int(timestamp)  # 转换为整数
    time_increment = 15  # 15秒递增
    
    # 遍历POLYLINE中的坐标点
    for point in polyline:
        longitude, latitude = point

        # 格式化时间戳为指定格式
        formatted_timestamp = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

        # 检查是否已经有该taxi_id的数据，如果没有则创建一个列表
        if taxi_id not in taxi_data_dict:
            taxi_data_dict[taxi_id] = []

        # 将数据添加到对应的列表中
        taxi_data_dict[taxi_id].append([taxi_id, formatted_timestamp, longitude, latitude])
        
        # 递增时间戳
        timestamp += time_increment


# 获取保存文件的目录
save_dir = os.path.join(base_dir, folder_name)

# 如果目录不存在，创建目录
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# 将数据写入txt文件夹，每个taxi_id一个文件
for taxi_id, data in tqdm(taxi_data_dict.items()):
    filename = os.path.join(save_dir, f"{taxi_id}.txt")
    with open(filename, 'w') as file:
        for data_row in data:
            line = f"{data_row[0]},{data_row[1]},{data_row[2]},{data_row[3]}\n"
            file.write(line)

print('Data has been converted and saved as txt files.')
