"""
将hmm之后的轨迹文件output.txt中的未匹配轨迹表示为-999
hmm之后文件中的valid_edge_id转换为origin_edge_id
"""
import sys
import os
sys.path.append('../')
sys.path.append('../../')
from map import RoadNetworkMap

city = 'Porto'

map_root = f'../data/RNTraj/RoadNetwork/{city}_RN'

if city == "Porto":
    road_map = RoadNetworkMap(map_root, zone_range=[41.142, -8.652, 41.174, -8.578], unit_length=50)
elif city == "Tdrive":
    road_map = RoadNetworkMap(map_root, zone_range=[39.8451, 116.2810, 39.9890, 116.4684], unit_length=50)

# 定义一个函数来进行转换
def transform_road_id(road_id):
    return road_map.valid_to_origin[int(road_id)]

def transform_trajectory(input_file, output_file):
    # 读取轨迹文件
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # 过滤出轨迹数据行和分隔符行
    trajectories = []
    trajectory = []
    separators = []
    for line in lines:
        if line.startswith('-'):
            if trajectory:
                trajectories.append(trajectory)
            trajectory = []
            separators.append(line.strip())
        else:
            trajectory.append(line.strip())
    if trajectory:
        trajectories.append(trajectory)

    # 创建一个新的文件来保存转换后的轨迹
    with open(output_file, 'w') as f:
        for trajectory, separator in zip(trajectories, separators):
            # 找出开头连续为0的行
            start_idx = 0
            while start_idx < len(trajectory) and trajectory[start_idx].split()[3] == '0':
                start_idx += 1

            # 找出结尾连续为0的行
            end_idx = len(trajectory) - 1
            while end_idx >= 0 and trajectory[end_idx].split()[3] == '0':
                end_idx -= 1

            # 特殊情况处理：所有road_id为0的情况
            if start_idx == len(trajectory):
                for line in trajectory:
                    parts = line.split()
                    time = parts[0]
                    latitude = parts[1]
                    longitude = parts[2]
                    transformed_road_id = '-999'
                    new_line = f"{time} {latitude} {longitude} {transformed_road_id}\n"
                    f.write(new_line)
                f.write(f'{separator}\n')  # 写入分隔符行并保留轨迹序号
                continue

            # 处理轨迹开头的连续为0的行
            for i in range(start_idx):
                parts = trajectory[i].split()
                time = parts[0]
                latitude = parts[1]
                longitude = parts[2]
                transformed_road_id = '-999'
                new_line = f"{time} {latitude} {longitude} {transformed_road_id}\n"
                f.write(new_line)

            # 处理轨迹中间的部分
            for i in range(start_idx, end_idx + 1):
                parts = trajectory[i].split()
                time = parts[0]
                latitude = parts[1]
                longitude = parts[2]
                road_id = parts[3]
                if road_id == '0':
                    transformed_road_id = '0'  # 中间部分的0保持不变
                else:
                    transformed_road_id = transform_road_id(road_id)
                new_line = f"{time} {latitude} {longitude} {transformed_road_id}\n"
                f.write(new_line)

            # 处理轨迹结尾的连续为0的行
            for i in range(end_idx + 1, len(trajectory)):
                parts = trajectory[i].split()
                time = parts[0]
                latitude = parts[1]
                longitude = parts[2]
                transformed_road_id = '-999'
                new_line = f"{time} {latitude} {longitude} {transformed_road_id}\n"
                f.write(new_line)

            f.write(f'{separator}\n')  # 写入分隔符行并保留轨迹序号

    print("转换完成。")

# 定义输入文件名和输出文件名data/RNTraj/A2C_hmmed_traj/
input_file = f"../data/RNTraj/A2C_hmmed_traj/{city}/test_output_8.txt"
output_dir = f"../data/RNTraj/A2C_hmmed_traj/Porto_HMM"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_file = os.path.join(output_dir, 'test_output_8.txt')
# 调用函数进行转换
transform_trajectory(input_file, output_file)
