import random
from tqdm import tqdm
city = 'Porto'

def read_trajectory_data(input_filename, output_filename):
    with open(input_filename, 'r') as input_file, open(output_filename, 'r') as output_file:
        input_lines = input_file.readlines()
        output_lines = output_file.readlines()

    trajectories = []
    current_input = []
    current_output = []
    skip_trajectory = False

    for input_line, output_line in zip(input_lines, output_lines):
        input_line = input_line.strip()
        output_line = output_line.strip()

        input_elements = input_line.split()
        output_elements = output_line.split()
        
        # 判断是否有错误标记的轨迹点
        if output_elements[-1] == '-997' or output_elements[-1] == '-999':
            # 如果有错误标记的轨迹点，则重置当前轨迹并继续下一个轨迹的处理
            skip_trajectory = True
            continue

        # 修改输入的最后一个元素为输出的最后一个元素
        input_elements[-1] = output_elements[-1]
        current_input.append(' '.join(input_elements))
        current_output.append(output_line)

        if input_line.startswith("-"):
            if not skip_trajectory:
                # 将当前轨迹添加到轨迹列表中
                trajectories.append((current_input, current_output))
            # 重置当前轨迹和跳过标志
            current_input = []
            current_output = []
            skip_trajectory = False

    return trajectories

def split_data(trajectories, train_ratio=0.7, valid_ratio=0.2, test_ratio=0.1):
    data_length = len(trajectories)
    train_count = int(data_length * train_ratio)
    valid_count = int(data_length * valid_ratio)
    test_count = int(data_length * test_ratio)

    indices = list(range(data_length))
    random.shuffle(indices)

    train_indices = indices[:train_count]
    valid_indices = indices[train_count:train_count + valid_count]
    test_indices = indices[train_count + valid_count:]

    train_data = [trajectories[i] for i in train_indices]
    valid_data = [trajectories[i] for i in valid_indices]
    test_data = [trajectories[i] for i in test_indices]

    return train_data, valid_data, test_data

def write_data_to_file(data, input_filename, output_filename):
    with open(input_filename, 'w') as input_file, open(output_filename, 'w') as output_file:
        for trajectory in tqdm(data, desc="Writing to files"):
            input_trajectory, output_trajectory = trajectory
            for input_line, output_line in zip(input_trajectory, output_trajectory):
                input_file.write(input_line + '\n')
                output_file.write(output_line + '\n')

input_file = f'../data/RNTraj/B_regular_umm_traj/{city}/integrated_urumm_traj_{city}.txt'
output_file = f'../data/RNTraj/D_epsiloned_traj/{city}/test_output_8.txt'

trajectories = read_trajectory_data(input_file, output_file)
print(len(trajectories))
train_data, valid_data, test_data = split_data(trajectories)

import os

def create_directories_and_files(city, root_dir):
    # Ensure directories exist
    os.makedirs(os.path.join(root_dir, f'{city}/train/'), exist_ok=True)
    os.makedirs(os.path.join(root_dir, f'{city}/valid/'), exist_ok=True)
    os.makedirs(os.path.join(root_dir, f'{city}/test/'), exist_ok=True)

    # Create empty files
    open(os.path.join(root_dir, f'{city}/train/train_input.txt'), 'w').close()
    open(os.path.join(root_dir, f'{city}/train/train_output.txt'), 'w').close()
    open(os.path.join(root_dir, f'{city}/valid/valid_input.txt'), 'w').close()
    open(os.path.join(root_dir, f'{city}/valid/valid_output.txt'), 'w').close()
    open(os.path.join(root_dir, f'{city}/test/test_input.txt'), 'w').close()
    open(os.path.join(root_dir, f'{city}/test/test_output.txt'), 'w').close()

# 定义城市和根目录
root_dir = '../data/RNTraj/Final/'  # 请替换为你的实际根目录路径

# 创建目录和文件
create_directories_and_files(city, root_dir)

# 写入数据到文件
write_data_to_file(train_data, os.path.join(root_dir, f'{city}/train/train_input.txt'), os.path.join(root_dir, f'{city}/train/train_output.txt'))
write_data_to_file(valid_data, os.path.join(root_dir, f'{city}/valid/valid_input.txt'), os.path.join(root_dir, f'{city}/valid/valid_output.txt'))
write_data_to_file(test_data, os.path.join(root_dir, f'{city}/test/test_input.txt'), os.path.join(root_dir, f'{city}/test/test_output.txt'))


