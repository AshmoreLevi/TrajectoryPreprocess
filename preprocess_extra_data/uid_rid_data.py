import sys
sys.path.append('../')
from common.road_network import process_and_save_rn
from common.mbr import MBR
import os
import json


def create_uid_mapping(input_dir, output_file):
    # 获取目录中的所有文件名（用户ID）
    uids = [f.split('.')[0] for f in os.listdir(input_dir) if f.endswith('.txt')]
    
    # 按数值顺序排序用户ID
    uids = sorted(uids, key=int)
    
    # 创建用户ID到连续编号的映射
    uid_mapping = {uid: idx for idx, uid in enumerate(uids)}
    
    # 将映射写入JSON文件
    with open(output_file, 'w') as f:
        json.dump(uid_mapping, f)
    
    print(f"UID mapping saved to {output_file}")
    
if __name__ == '__main__':
    city = 'Chengdu'
    
    # 4 rn json files
    road_path = f'../data/map/{city}'
    root_dir = f'../data/map/{city}/extra_data'
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)
        
    process_and_save_rn(road_path, root_dir, is_directed=True)
    
    # uid to index json
    traj_data = f'../data/mm_data/{city}/mm_{city}'
    uid2index_dict_file = f'../data/map/{city}/extra_data/uid2index.json'
    create_uid_mapping(traj_data, uid2index_dict_file)
    