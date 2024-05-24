from common.trajectory import Trajectory, get_tid
from common.spatial_func import distance

def find_first_exceed_max_distance(pt_list, cur_idx, max_distance):
    cur_pt = pt_list[cur_idx]
    next_idx = cur_idx + 1
    # find all successors whose distance is within MaxStayDist w.r.t. anchor
    while next_idx < len(pt_list):
        next_pt = pt_list[next_idx]
        dist = distance(cur_pt, next_pt)
        if dist > max_distance:
            break
        next_idx += 1
    return next_idx


def exceed_max_time(pt_list, cur_idx, next_idx, max_stay_time):
    '''

    :param pt_list:
    :param cur_idx:
    :param next_idx: next idx is the first idx that outside the distance threshold
    :param max_stay_time:
    :return:
    '''
    time_span = (pt_list[next_idx - 1].time - pt_list[cur_idx].time).total_seconds()
    # the time span is larger than maxStayTimeInSecond, a stay point is detected
    return time_span > max_stay_time

class Segmentation:
    def __init__(self):
        pass

    def segment(self, traj):
        pass


class TimeIntervalSegmentation(Segmentation):
    """
    Split trajectory if the time interval between two GPS points is larger than max_time_interval_min
    Store sub-trajectory when its length is larger than min_len
    """
    def __init__(self, max_time_interval_min, min_len=1):
        super(Segmentation, self).__init__()
        self.max_time_interval = max_time_interval_min * 60
        self.min_len = min_len

    def segment(self, traj):
        segmented_traj_list = []
        pt_list = traj.pt_list
        if len(pt_list) <= 1:
            return []
        oid = traj.oid
        pre_pt = pt_list[0]
        partial_pt_list = [pre_pt]
        for cur_pt in pt_list[1:]:
            time_span = (cur_pt.time - pre_pt.time).total_seconds()
            if time_span <= self.max_time_interval:
                partial_pt_list.append(cur_pt)
            else:
                if len(partial_pt_list) > self.min_len:
                    segmented_traj = Trajectory(oid, get_tid(oid, partial_pt_list), partial_pt_list)
                    segmented_traj_list.append(segmented_traj)
                partial_pt_list = [cur_pt]  # re-initialize partial_pt_list
            pre_pt = cur_pt
        if len(partial_pt_list) > self.min_len:
            segmented_traj = Trajectory(oid, get_tid(oid, partial_pt_list), partial_pt_list)
            segmented_traj_list.append(segmented_traj)
        return segmented_traj_list
    

class StayPointSegmentation(Segmentation):
    def __init__(self, dist_thresh_meter, max_stay_time_min):
        super(Segmentation, self).__init__()
        self.dist_thresh = dist_thresh_meter
        self.max_stay_time = max_stay_time_min * 60

    def segment(self, traj):
        segment_traj_list = []
        pt_list = traj.pt_list
        if len(pt_list) <= 1:
            return []
        oid = traj.oid
        cur_idx = 0
        traj_idx = 0
        while cur_idx < len(pt_list) - 1:
            next_idx = find_first_exceed_max_distance(pt_list, cur_idx, self.dist_thresh)
            if exceed_max_time(pt_list, cur_idx, next_idx, self.max_stay_time):
                # at least two points
                if traj_idx < cur_idx - 2:
                    segment_traj = Trajectory(oid, get_tid(oid, pt_list[traj_idx:cur_idx]), pt_list[traj_idx:cur_idx])
                    segment_traj_list.append(segment_traj)
                traj_idx = next_idx
                cur_idx = next_idx
            else:
                cur_idx += 1
        # at least two points
        if traj_idx < len(pt_list) - 2:
            segment_traj = Trajectory(oid, get_tid(oid, pt_list[traj_idx:]), pt_list[traj_idx:])
            segment_traj_list.append(segment_traj)
        return segment_traj_list


