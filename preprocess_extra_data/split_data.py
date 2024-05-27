import os
import numpy as np
import random
from tqdm import tqdm

import sys
sys.path.append('../')

from utils.parse_trajs import ParseMMTraj_MTraj
from utils.save_trajs import SaveTraj2MM

def split_data_Porto(traj_input_dir, output_dir):
    """
    Split original data into train, valid, and test datasets.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    train_data_dir = os.path.join(output_dir, 'train_data')
    val_data_dir = os.path.join(output_dir, 'valid_data')
    test_data_dir = os.path.join(output_dir, 'test_data')
    
    os.makedirs(train_data_dir, exist_ok=True)
    os.makedirs(val_data_dir, exist_ok=True)
    os.makedirs(test_data_dir, exist_ok=True)

    train_data_path = os.path.join(train_data_dir, 'train_data.txt')
    val_data_path = os.path.join(val_data_dir, 'valid_data.txt')
    test_data_path = os.path.join(test_data_dir, 'test_data.txt')

    trg_parser = ParseMMTraj_MTraj()
    trg_saver = SaveTraj2MM()

    for file_name in tqdm(os.listdir(traj_input_dir)):
        traj_input_path = os.path.join(traj_input_dir, file_name)
        trg_trajs = np.array(trg_parser.parse(traj_input_path))
        ttl_lens = len(trg_trajs)

        if ttl_lens == 0:
            continue

        test_inds = random.sample(range(ttl_lens), max(1, int(ttl_lens * 0.1)))  # 10% as test data
        tmp_inds = [ind for ind in range(ttl_lens) if ind not in test_inds]
        val_inds = random.sample(tmp_inds, max(1, int(ttl_lens * 0.2)))  # 20% as validation data
        train_inds = [ind for ind in tmp_inds if ind not in val_inds]  # 70% as training data

        train_trajs = trg_trajs[train_inds]
        val_trajs = trg_trajs[val_inds]
        test_trajs = trg_trajs[test_inds]

        trg_saver.store(train_trajs, train_data_path)
        trg_saver.store(val_trajs, val_data_path)
        trg_saver.store(test_trajs, test_data_path)

    print("Data has been split and saved.")

def split_data_Chengdu(traj_input_dir, output_dir):
    """
    split original data to train, valid and test datasets
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    train_data_dir = os.path.join(output_dir, 'train_data')
    val_data_dir = os.path.join(output_dir, 'valid_data')
    test_data_dir = os.path.join(output_dir, 'test_data')
    
    os.makedirs(train_data_dir, exist_ok=True)
    os.makedirs(val_data_dir, exist_ok=True)
    os.makedirs(test_data_dir, exist_ok=True)

    train_data_path = os.path.join(train_data_dir, 'train_data.txt')
    val_data_path = os.path.join(val_data_dir, 'valid_data.txt')
    test_data_path = os.path.join(test_data_dir, 'test_data.txt')

    trg_parser = ParseMMTraj_MTraj()
    trg_saver = SaveTraj2MM()
    
    all_trajs = []

    # 收集所有轨迹
    for file_name in tqdm(os.listdir(traj_input_dir)):
        traj_input_path = os.path.join(traj_input_dir, file_name)
        trg_trajs = np.array(trg_parser.parse(traj_input_path))
        all_trajs.extend(trg_trajs)

    total_trajs = len(all_trajs)
    print(f"Total trajectories: {total_trajs}")

    # 按比例划分
    test_inds = random.sample(range(total_trajs), int(total_trajs * 0.1))  # 10% as test data
    remaining_inds = [ind for ind in range(total_trajs) if ind not in test_inds]
    val_inds = random.sample(remaining_inds, int(total_trajs * 0.2))  # 20% as validation data
    train_inds = [ind for ind in remaining_inds if ind not in val_inds]  # 70% as training data

    print(f"Train indices: {len(train_inds)}, Validation indices: {len(val_inds)}, Test indices: {len(test_inds)}")

    # 提取并保存划分后的轨迹
    train_trajs = [all_trajs[ind] for ind in train_inds]
    val_trajs = [all_trajs[ind] for ind in val_inds]
    test_trajs = [all_trajs[ind] for ind in test_inds]

    trg_saver.store(train_trajs, train_data_path)
    trg_saver.store(val_trajs, val_data_path)
    trg_saver.store(test_trajs, test_data_path)

    print("Data has been split and saved.")

def get_traj_count(traj_dir):
    # a Porto user has many trajs while most of Chengdu users have only 1 or 2
    from collections import defaultdict
    trg_parser = ParseMMTraj_MTraj()

    traj_input_dir = traj_dir

    traj_count_dict = defaultdict(int)

    for file_name in tqdm(os.listdir(traj_input_dir)):
        if file_name.endswith('.txt'):  # 假设文件都是.txt格式
            traj_input_path = os.path.join(traj_input_dir, file_name)
            trg_trajs = np.array(trg_parser.parse(traj_input_path))
            ttl_lens = len(trg_trajs)
            traj_count_dict[ttl_lens] += 1

    sorted_traj_counts = sorted(traj_count_dict.items())

    print("轨迹条数 : 文件数")
    for traj_count, file_count in sorted_traj_counts:
        print(f"{traj_count} : {file_count}")
        
if __name__ == '__main__':
    city = 'Porto'
    traj_input_dir = f'../data/mm_data/{city}/mm_{city}/'
    output_dir = f'../data/final_data/{city}/'
    
    if city == 'Chengdu':
        split_data_Chengdu(traj_input_dir, output_dir)
    elif city == 'Porto':
        split_data_Porto(traj_input_dir, output_dir)
    