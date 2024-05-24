from common.road_network import load_rn_shp
from map_matching.hmm.hmm_map_matcher import TIHMMMapMatcher
import os
from tqdm import tqdm
import argparse

from utils.parse_trajs import ParseRawTraj
from utils.save_trajs import SaveTraj2MM

"""
nohup python -u map_match.py > mm0524.txt 2>&1 & 
"""


def mm_traj2rn(clean_traj_dir, mm_traj_dir, rn_path):
    rn = load_rn_shp(rn_path, is_directed=True)
    map_matcher = TIHMMMapMatcher(rn,search_dis=50)

    if rn is not None:
        print("道路网络加载成功")
    else:
        print("道路网络加载失败")

    # 检查mm_traj_dir目录是否存在，如果不存在则创建
    if not os.path.exists(mm_traj_dir):
        os.makedirs(mm_traj_dir)

    parser = ParseRawTraj()
    storer = SaveTraj2MM()

    for filename in tqdm(os.listdir(clean_traj_dir)):
        clean_trajs = parser.parse(os.path.join(clean_traj_dir, filename))
        mm_trajs = [map_matcher.match(clean_traj) for clean_traj in clean_trajs]
        storer.store(mm_trajs, os.path.join(mm_traj_dir, filename))

if __name__ == '__main__':
    city = 'Porto'
    parser = argparse.ArgumentParser()
    parser.add_argument('--clean_traj_dir', default=f'data/cleaned_data/{city}/cleaned_{city}', help='the directory of the cleaned trajectories')
    parser.add_argument('--mm_traj_dir', default=f'data/mm_data/{city}/mm_{city}',help= "map matched trajs dir")
    parser.add_argument('--rn_path', default=f'data/map/{city}')
    opt = parser.parse_args()
    print(opt)

    mm_traj2rn(opt.clean_traj_dir, opt.mm_traj_dir, opt.rn_path)