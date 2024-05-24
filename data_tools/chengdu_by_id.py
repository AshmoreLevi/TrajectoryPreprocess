"""
Convert the CSV data of Chengdu into TXT data for cleaning.
includes preliminary screening.
"""
import csv
import os
import sys
from datetime import datetime
from tqdm import tqdm

from utils.spatial_func import SPoint, distance
from utils.coord_transform import GCJ02ToWGS84

"""
测试用小数据集：
head -n 100 chengdu_csv/chengdushi_1001_1010.csv > test_csv/chengdu.csv

用nohup跑:
nohup python -u chengdu_by_id.py > csv2txt.txt 2>&1 & 
"""

# 定义输入CSV文件夹路径
input_folder = "chengdu_csv"
# 定义输出文件夹路径
output_folder = "chengdu"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def read_csv_file(file_path):
    """读取CSV文件并返回总行数和内容"""
    with open(file_path, 'r', newline='') as csvfile:
        csv_reader = csv.reader(csvfile)
        content = list(csv_reader)
        total_rows = len(content)
    return total_rows, content

def process_trajectory_points(trajectory):
    """处理轨迹点，转换坐标并返回处理后的轨迹点列表（每五个点采样一次）"""
    trajectory_points = trajectory.strip('[]').split(', ')
    converted_points = []
    for i, point in enumerate(trajectory_points):
        if i % 5 == 0:
            lng, lat, t = point.split()
            converted_lng, converted_lat = GCJ02ToWGS84().convert(float(lng), float(lat))
            converted_points.append((converted_lng, converted_lat, t))
    return converted_points

def write_user_trajectories(output_folder, uid_trajectories):
    """将每个UID及其轨迹序列写入TXT文件"""
    for uid, trajectories in uid_trajectories.items():
        user_file_path = os.path.join(output_folder, f"user_{uid}.txt")
        with open(user_file_path, 'w') as user_file:
            for trajectory_points in trajectories:
                for point in trajectory_points:
                    lng, lat, t = point
                    formatted_time = datetime.utcfromtimestamp(int(t)).strftime('%Y-%m-%d %H:%M:%S')
                    user_file.write(f"{uid},{formatted_time},{lng},{lat}\n")

def process_trajectory_data(input_folder, output_folder, filter_function):
    """主函数：处理轨迹数据"""
    csv.field_size_limit(sys.maxsize)
    uid_trajectories = {}
    uid_mapping = {}

    csv_files = sorted([file for file in os.listdir(input_folder) if file.endswith('.csv')])

    for filename in csv_files:
        csv_file_path = os.path.join(input_folder, filename)
        total_rows, content = read_csv_file(csv_file_path)
        print(f"CSV文件 {filename} 共有 {total_rows - 1} 行数据。")

        uid_counter = len(uid_mapping)
        csv_reader = iter(content)
        next(csv_reader)  # 跳过标题行

        for row in tqdm(csv_reader, total=total_rows-1, desc=f"Processing {filename}"):
            raw_uid, trajectory = row[1], row[2]

            if not trajectory or len(trajectory.strip()) == 0:
                continue

            converted_trajectory_points = process_trajectory_points(trajectory)

            if not filter_function(converted_trajectory_points):
                continue

            if raw_uid not in uid_mapping:
                uid_mapping[raw_uid] = uid_counter
                uid_counter += 1

            if uid_mapping[raw_uid] not in uid_trajectories:
                uid_trajectories[uid_mapping[raw_uid]] = []
            uid_trajectories[uid_mapping[raw_uid]].append(converted_trajectory_points)

        print(f"Processed {len(uid_trajectories)} users so far.")

    write_user_trajectories(output_folder, uid_trajectories)

def filter_function(trajectory_points):
    """筛选条件函数"""
    if len(trajectory_points) < 32 or len(trajectory_points) > 48:
        return False

    timestamps = [int(point[2]) for point in trajectory_points]
    time_intervals = [timestamps[i] - timestamps[i - 1] for i in range(1, len(timestamps))]
    average_interval = sum(time_intervals) / len(time_intervals)
    if average_interval < 12 or average_interval > 16:
        return False

    mbr_range = (30.65, 104.04, 30.75, 104.14)
    for lng, lat, t in trajectory_points:
        if not (mbr_range[0] <= lat <= mbr_range[2] and mbr_range[1] <= lng <= mbr_range[3]):
            return False

    total_distance = 0
    for i in range(1, len(trajectory_points)):
        lng1, lat1, t1 = trajectory_points[i-1]
        lng2, lat2, t2 = trajectory_points[i]
        total_distance += distance(SPoint(lat1, lng1), SPoint(lat2, lng2))

    average_speed = total_distance / sum(time_intervals)
    if average_speed < 5 or average_speed > 35:
        return False

    return True

# 调用主函数处理数据
process_trajectory_data(input_folder, output_folder, filter_function)
