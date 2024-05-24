import random
from tqdm import tqdm
city = 'Porto'

def read_trajectory_data(input_filename):
    with open(input_filename, 'r') as input_file:
        trajectories = []
        current_trajectory = []

        for line in input_file:
            current_trajectory.append(line.strip())
            if line.startswith("-"):
                if current_trajectory:
                    trajectories.append(current_trajectory)
                    current_trajectory = []
                continue

        return trajectories

def remove_percentage_of_trajectory(trajectory_data, percentage):
    modified_trajectory_data = []
    for trajectory in trajectory_data:
        num_points = len(trajectory)
        num_points_to_remove = int(num_points * percentage)
        
        # 找到轨迹末尾的-id行
        end_id_line = trajectory[-1]
        # 从轨迹中删除要删除的行，但保留末尾的-id行
        indices_to_remove = random.sample(range(num_points - 1), num_points_to_remove)
        
        modified_trajectory = [point for idx, point in enumerate(trajectory) if idx == num_points - 1 or idx not in indices_to_remove]
        modified_trajectory_data.append(modified_trajectory)
    
    return modified_trajectory_data

def write_data_to_file(data, output_filename):
    with open(output_filename, 'w') as output_file:
        for trajectory in tqdm(data, desc="Writing to files"):
            for point in trajectory:
                output_file.write(point + '\n')

# 读取原始数据
input_file = f'Final/{city}/test/test_input.txt'
output_file = f'Final/{city}/test/test_input_mask.txt'
original_data = read_trajectory_data(input_file)

# 删除30%的轨迹点数
modified_data = remove_percentage_of_trajectory(original_data, 0.875)

# 将处理后的数据写入文件
write_data_to_file(modified_data, output_file)
