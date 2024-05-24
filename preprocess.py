city = "Porto"

from common.mbr import MBR
from statistics_tools.statistics_cleaned import statistics

from common.trajectory import Trajectory,STPoint
from utils.noise_filter import STFilter,HeuristicFilter
from utils.segmentation import TimeIntervalSegmentation,StayPointSegmentation

from utils.save_trajs import SaveTraj2Raw

import os
import argparse
from tqdm import tqdm
from datetime import datetime

"""
测试用小数据集：
head -n 100 chengdu_csv/chengdushi_1001_1010.csv > test_csv/chengdu.csv

用nohup跑clean:
nohup python -u preprocess.py --clean_traj_dir 'data/Tdrive/cleaned_tdrive' --data_root_dir 'data/Tdrive/taxi_log_2008_by_id'> clean.txt 2>&1 & 
nohup python -u preprocess.py --data_root_dir 'data/raw_data/Porto/Porto_by_id' --clean_traj_dir 'data/cleaned_data/Porto/cleaned_Porto' > clean01.txt 2>&1 & 
"""

def parse_tdrive(filename, tdrive_root_dir):
    '''
    解析TDrive数据中的一个txt文件,并将其转换为轨迹对象
    '''
    oid = filename.replace('.txt', '')
    with open(os.path.join(tdrive_root_dir, filename), 'r') as f:
        pt_list = []
        for line in f.readlines():
            attrs = line.strip('\n').split(',')
            lat = float(attrs[3])
            lng = float(attrs[2])
            time = datetime.strptime(attrs[1], '%Y-%m-%d %H:%M:%S')
            pt_list.append(STPoint(lat, lng, time))
    if len(pt_list) > 1:
        return Trajectory(oid, 0, pt_list)
    else:
        return None

def do_clean_limit(raw_traj, filters, segmentations, min_duraion, max_duration):

    clean_traj = raw_traj
    for filter in filters:
        clean_traj = filter.filter(clean_traj)
        if clean_traj is None:
            return []
    clean_traj_list = [clean_traj]

    for seg in segmentations:
        tmp_clean_traj_list = []
        for clean_traj in clean_traj_list:
            segment_trajs = seg.segment(clean_traj)
            tmp_clean_traj_list.extend(segment_trajs)
        clean_traj_list = tmp_clean_traj_list

    clean_traj_list = [traj for traj in clean_traj_list if min_duraion <= traj.get_duration() <= max_duration]

    # 删除总点数少于32的轨迹, 删除总点数大于48的轨迹（因为最后的向下采样率为4倍数）
    # 根据数据集的平均采样率不同,不能简单地规定轨迹长度
    clean_traj_list = [traj for traj in clean_traj_list if 32 <= len(traj.pt_list) <= 48]
    
    return clean_traj_list
            
def clean_trajs(raw_traj_dir, cleaned_traj_dir, start_time, end_time, mbr_coords, max_speed,
                 max_time_interval_min, dist_thresh_meter, max_stay_time_min, min_duration, max_duration):
    mbr = MBR(*mbr_coords)

    st_filter = STFilter(mbr, start_time, end_time)
    heuristic_filter = HeuristicFilter(max_speed=max_speed)
    filters = [st_filter, heuristic_filter]

    ti_seg = TimeIntervalSegmentation(max_time_interval_min=max_time_interval_min)
    sp_seg = StayPointSegmentation(dist_thresh_meter=dist_thresh_meter, max_stay_time_min=max_stay_time_min)
    segs = [ti_seg, sp_seg]

    # 检查 clean_traj_dir 目录是否存在，如果不存在则创建
    if not os.path.exists(cleaned_traj_dir):
        os.makedirs(cleaned_traj_dir)

    storer = SaveTraj2Raw()

    for filename in tqdm(os.listdir(raw_traj_dir)):
        raw_traj = parse_tdrive(filename, raw_traj_dir)
        if raw_traj is None:
            continue
        clean_trajs = do_clean_limit(raw_traj, filters, segs, min_duration, max_duration)
        if len(clean_trajs) > 0:
            storer.store(clean_trajs, os.path.join(cleaned_traj_dir, filename))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_root_dir', default=f'data/raw_data/{city}/{city}_by_id', help='the directory of the dataset')
    parser.add_argument('--clean_traj_dir', default=f'data/cleaned_data/{city}/cleaned_{city}', help='the directory of the cleaned trajectories')
    parser.add_argument('--phase', default='clean', help='the preprocessing phase [clean,stat]')
    opt = parser.parse_args()
    print(opt)

    # 起终时间
    # Tdrive:(2008, 2, 2) (2008, 2, 9)
    # Porto:(2013, 7, 1) (2014, 6, 30)
    # Chengdu:(2018, 9, 30)(2018, 11, 1)
    start_time = datetime(2013, 7, 1) 
    end_time = datetime(2014, 6, 30)

    # 空间范围mbr
    # porto:(41.142, -8.652, 41.174, -8.578)
    # Tdrive:(39.9049, 116.3255, 39.9500, 116.4331)
    # Chengdu:(30.655, 104.043, 30.727, 104.129)
    mbr_coords = (41.142, -8.652, 41.174, -8.578)

    # 最大速度（m/s）
    max_speed = 30

    # Segment
    # {"Porto": 1; "Tdrive": 1}
    # 最大间隔时间（分钟）,如果大于这个间隔，轨迹就要被分段。
    max_time_interval_min = 4
    # 停留点检测（在一个范围内停留超过时间，就要被分段）
    dist_thresh_meter = 100
    max_stay_time_min = 4

    # 平均间隔：interval
    # 一段轨迹持续时间限制 interval * 32 ～ interval * 48 秒。
    # Tdrive: (600, 900)
    # Porto:(480, 1500)
    # Chengdu:(60, 300)
    min_duration = 600
    max_duration = 900

    if opt.phase == 'clean':
        clean_trajs(opt.data_root_dir, opt.clean_traj_dir, start_time, end_time, mbr_coords, max_speed, max_time_interval_min,
                   dist_thresh_meter, max_stay_time_min, min_duration, max_duration)
    elif opt.phase == 'stat':
        statistics(opt.clean_traj_dir)
    else:
        raise Exception('unknown phase')
    
    print("done")