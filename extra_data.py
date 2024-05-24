from common.road_network import process_and_save_rn
from common.mbr import MBR
import os

if __name__ == '__main__':
    city = 'Porto'
    road_path = f'data/map/{city}'
    min_lat, min_lng, max_lat, max_lng = 41.142, -8.652, 41.174, -8.578
    mbr = MBR(min_lat, min_lng, max_lat, max_lng)
    root_dir = f'data/map/{city}/extra_data'
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)

    process_and_save_rn(road_path, mbr, root_dir, is_directed=True)