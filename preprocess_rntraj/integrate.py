import os
from tqdm import tqdm

city = 'Porto'

# 指定存储处理好轨迹文件的文件夹
input_folder = f'../data/RNTraj/A_cleaned_traj/{city}_by_id'

# 指定整合后的输出文件名
output_file = f'../data/RNTraj/A_cleaned_traj/integrated_urumm_traj_{city}.txt'

# 创建一个新的txt文件用于整合轨迹
with open(output_file, 'w') as integrated_file:
    # 初始化轨迹计数器
    track_number = 1

    # 遍历处理好的轨迹文件
    for filename in tqdm(os.listdir(input_folder), desc="Processing Files"):
        if filename.endswith('.txt'):
           

            input_file_path = os.path.join(input_folder, filename)

            # 读取处理好的轨迹文件
            with open(input_file_path, 'r') as file:
                lines = file.readlines()

            # 逐行处理数据并写入整合文件
            for line in lines:
                if line.startswith('-'):
                    # 遇到新的轨迹段时，从行中提取新的轨迹段号并修改
                    modified_line = f'-{track_number}\n'
                    track_number = track_number+1
                    integrated_file.write(modified_line)
                else:
                    # 不是新的轨迹段，直接写入整合文件
                    integrated_file.write(line)
            
            # 检查轨迹计数器是否达到100,000，如果是，则终止循环
            # if track_number >= 120000:
            #     break


