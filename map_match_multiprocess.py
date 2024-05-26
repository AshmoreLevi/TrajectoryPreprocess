import multiprocessing
from common.road_network import load_rn_shp
from map_matching.hmm.hmm_map_matcher import TIHMMMapMatcher
import os
from tqdm import tqdm
import argparse
import time

from utils.parse_trajs import ParseRawTraj
from utils.save_trajs import SaveTraj2MM

def process_file_wrapper(args):
    return process_file(*args)

def process_file(filename, clean_traj_dir, mm_traj_dir, rn_path):
    try:
        # 加载路网数据和初始化匹配器
        rn = load_rn_shp(rn_path, is_directed=True)
        map_matcher = TIHMMMapMatcher(rn, search_dis=50)

        # 解析轨迹数据
        parser = ParseRawTraj()
        clean_trajs = parser.parse(os.path.join(clean_traj_dir, filename))
        
        # 匹配轨迹数据并保存结果
        mm_trajs = [map_matcher.match(clean_traj) for clean_traj in clean_trajs]
        storer = SaveTraj2MM()
        storer.store(mm_trajs, os.path.join(mm_traj_dir, filename))

        return filename  # 返回已处理的文件名
    except Exception as e:
        print(f"Error processing file {filename}: {e}")

def mm_traj2rn(clean_traj_dir, mm_traj_dir, rn_path):
    if not os.path.exists(mm_traj_dir):
        os.makedirs(mm_traj_dir)

    filenames = os.listdir(clean_traj_dir)
    start_time = time.time()

    # 使用 tqdm 显示进度条
    with multiprocessing.Pool(processes=os.cpu_count()) as pool:
        with tqdm(total=len(filenames)) as pbar:
            args = [(filename, clean_traj_dir, mm_traj_dir, rn_path) for filename in filenames]
            for _ in pool.imap_unordered(process_file_wrapper, args):
                pbar.update(1)  # 更新进度条

    end_time = time.time()
    print(f"Total processing time: {end_time - start_time:.2f} seconds")

if __name__ == '__main__':
    city = 'Chengdu'
    parser = argparse.ArgumentParser()
    parser.add_argument('--clean_traj_dir', default=f'data/cleaned_data/{city}/cleaned_{city}_small', help='the directory of the cleaned trajectories')
    parser.add_argument('--mm_traj_dir', default=f'data/mm_data/{city}/mm_{city}_small', help="map matched trajs dir")
    parser.add_argument('--rn_path', default=f'data/map/{city}')
    opt = parser.parse_args()
    print(opt)

    mm_traj2rn(opt.clean_traj_dir, opt.mm_traj_dir, opt.rn_path)
