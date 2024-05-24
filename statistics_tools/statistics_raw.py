"""
最原始轨迹的统计情况
"""
import os
from datetime import datetime
from tqdm import tqdm

def is_in_range(lat, lng, min_lat, max_lat, min_lng, max_lng):
    """
    检查经纬度是否在指定的矩形范围内。
    """
    return min_lat <= lat <= max_lat and min_lng <= lng <= max_lng

def calculate_statistics(tracks_folder):
    # 初始化统计数据
    user_ids = set()
    total_tracks = 0
    total_points = 0
    
    
    min_longitude = float('inf')
    max_longitude = float('-inf')
    min_latitude = float('inf')
    max_latitude = float('-inf')

    # Tdrive最离谱的mbr 39.8, 40.0, 116.2, 116.5
    # Porto 最离谱的mbr 41.1, 41.2, -8.7, -8.5
    # min_lat, max_lat, min_lng, max_lng = 41.1, 41.2, -8.7, -8.5
    # Chengdu最离谱的mbr 
    min_lat, max_lat, min_lng, max_lng = 30.65, 104.04, 30.75, 104.14

    min_duration = float('inf')
    max_duration = float('-inf')
    total_duration = 0
    total_sampling_intervals = 0
    valid_intervals = 0
    earliest_timestamp = None
    latest_timestamp = None

    # 获取轨迹文件列表
    track_files = os.listdir(tracks_folder)

    # 遍历每个轨迹文件
    for track_file in tqdm(track_files, desc='Processing tracks'):
        user_id = os.path.splitext(track_file)[0]  # 获取文件名作为用户ID
        user_ids.add(user_id)  # 将用户ID添加到集合中
        with open(os.path.join(tracks_folder, track_file), 'r') as f:
            lines = f.readlines()

            if not lines:  # 跳过空文件
                continue

            total_tracks += 1
            track_points = len(lines)
            total_points += track_points

            timestamps = []
            for line in lines:
                attrs = line.strip().split(',')
                lat = float(attrs[3])
                lng = float(attrs[2])
                # 检查经纬度是否在指定范围内
                if not is_in_range(lat, lng, min_lat, max_lat, min_lng, max_lng):
                    continue  # 如果不在范围内，则跳过这行轨迹点的处理

                timestamp = datetime.strptime(attrs[1], '%Y-%m-%d %H:%M:%S')
                timestamps.append(timestamp)
                min_longitude = min(min_longitude, lng)
                max_longitude = max(max_longitude, lng)
                min_latitude = min(min_latitude, lat)
                max_latitude = max(max_latitude, lat)

            if not timestamps:
                continue
            # 计算轨迹持续时间和采样间隔
            duration = (max(timestamps) - min(timestamps)).total_seconds()
            total_duration += duration
            min_duration = min(min_duration, duration)
            max_duration = max(max_duration, duration)
            
            # 过滤间隔时间大于20秒的采样间隔
            sampling_intervals = [(timestamps[i] - timestamps[i - 1]).total_seconds() for i in range(1, len(timestamps)) if (timestamps[i] - timestamps[i - 1]).total_seconds() <= 20]
            total_sampling_intervals += sum(sampling_intervals)
            valid_intervals += len(sampling_intervals)

            # 更新最早和最晚时间戳
            if earliest_timestamp is None or min(timestamps) < earliest_timestamp:
                earliest_timestamp = min(timestamps)
            if latest_timestamp is None or max(timestamps) > latest_timestamp:
                latest_timestamp = max(timestamps)

    # 计算地理范围和矩形面积
    geo_range = {
        'min_longitude': min_longitude,
        'max_longitude': max_longitude,
        'min_latitude': min_latitude,
        'max_latitude': max_latitude
    }
    rect_area = (max_longitude - min_longitude) * (max_latitude - min_latitude)
    # 一度纬度和经度的大致长度（在赤道附近）
    approx_degree_length_km = 111.32  # 1度纬度约等于111.32千米
    # 将rect_area从平方度转换为平方千米
    rect_area = rect_area / (approx_degree_length_km ** 2)

    # 计算平均采样间隔
    average_sampling_interval = total_sampling_intervals / valid_intervals if valid_intervals else 0

    # 组装统计数据
    statistics = {
        'user_count': len(user_ids),
        'total_tracks': total_tracks,
        'total_points': total_points,
        'geo_range': geo_range,
        'rect_area': rect_area,
        'min_duration': min_duration,
        'max_duration': max_duration,
        'total_duration': total_duration,
        'average_sampling_interval': average_sampling_interval,
        'earliest_timestamp': earliest_timestamp,
        'latest_timestamp': latest_timestamp
    }

    return statistics

if __name__ == "__main__":
    # 指定原始轨迹文件夹的路径
    # tracks_folder = 'tptk-master/data/Tdrive/taxi_log_2008_by_id'
    # tracks_folder = 'tptk-master/data/Porto/porto_by_id'
    tracks_folder = 'data/Chengdu/chengdu'

    # 调用统计函数计算统计数据
    statistics = calculate_statistics(tracks_folder)

    # 打印统计结果
    print("User Count:", statistics['user_count'])
    print("Total Tracks:", statistics['total_tracks'])
    print("Total Points:", statistics['total_points'])
    print("Geo Range:", statistics['geo_range'])
    print("Rect Area:", statistics['rect_area'])
    print("Min Duration:", statistics['min_duration'])
    print("Max Duration:", statistics['max_duration'])
    print("Total Duration:", statistics['total_duration'])
    print("Average Sampling Interval:", statistics['average_sampling_interval'])
    print("Earliest Timestamp:", statistics['earliest_timestamp'])
    print("Latest Timestamp:", statistics['latest_timestamp'])
   