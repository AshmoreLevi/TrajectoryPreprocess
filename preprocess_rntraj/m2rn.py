# 原始的M类型轨迹数据转化为RN类型轨迹数据

import os
from datetime import datetime

city = 'Porto'
input_folder = f'../data/cleaned_data/{city}/cleaned_{city}'
output_folder = f'../data/RNTraj/A_cleaned_traj/{city}_by_id'

# 确保目标文件夹存在，如果不存在则创建它
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 遍历原始文件夹中的文件
for filename in os.listdir(input_folder):
    if filename.endswith('.txt'):
        input_file_path = os.path.join(input_folder, filename)
        output_file_path = os.path.join(output_folder, filename)

        # 读取原始轨迹文件
        with open(input_file_path, 'r') as file:
            lines = file.readlines()

        # 初始化变量以存储处理后的轨迹数据
        processed_tracks = []

        # 初始化变量以存储当前轨迹信息
        current_track = []

        # 初始化变量以存储轨迹段数目
        track_number = 0

        # 遍历每一行
        for line in lines:
            if line.startswith('#'):
                # 如果当前轨迹信息不为空，将其添加到处理后的轨迹数据中，并添加新标识符
                if current_track:
                    track_number += 1
                    current_track.append(f'-{track_number}\n')
                    processed_tracks.append(current_track)
                # 重置当前轨迹信息
                current_track = []
            else:
                # 否则，按要求修改轨迹格式并添加到当前轨迹信息中
                parts = line.strip().split(',')
                if len(parts) == 3:
                    time_str, latitude, longitude = parts

                    # 使用 datetime 解析时间字符串
                    time_format = "%Y/%m/%d %H:%M:%S"
                    parsed_time = datetime.strptime(time_str, time_format)

                    # 将 datetime 对象转换为 UNIX 时间戳
                    timestamp = int(parsed_time.timestamp())

                    # 修改轨迹格式，设置road_id为-1
                    new_line = f"{timestamp} {latitude} {longitude} -1\n"
                    current_track.append(new_line)

        # 处理最后一个轨迹信息
        if current_track:
            track_number += 1
            current_track.append(f'-{track_number}\n')
            processed_tracks.append(current_track)

        # 将处理后的轨迹数据写入目标文件夹中，保持文件名不变
        with open(output_file_path, 'w') as output_file:
            for track in processed_tracks:
                output_file.writelines(track)