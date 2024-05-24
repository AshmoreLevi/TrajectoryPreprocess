#!/usr/bin/python3
# coding: utf-8
# @Time    : 2020/9/7 17:07
# Add new method
from statistics import median

from common.spatial_func import distance
from common.trajectory import Trajectory, STPoint

"""
All the methods are refered from 
Zheng, Y. and Zhou, X. eds., 2011. 
Computing with spatial trajectories. Springer Science & Business Media.
Chapter 1 Trajectory Preprocessing
"""
"""
HeuristicFilter:通过检测速度超过最大阈值的点并将其移除。
STFilter:检测超过空间与时间范围的点并将其移除。
"""


class NoiseFilter:
    def filter(self, traj):
        pass

    def get_tid(self, oid, clean_pt_list):
        return oid + '_' + clean_pt_list[0].time.strftime('%Y%m%d%H%M') + '_' + \
               clean_pt_list[-1].time.strftime('%Y%m%d%H%M')

# remove point
class HeuristicFilter(NoiseFilter):
    """
    Remove outlier if it is out of the max speed
    """

    def __init__(self, max_speed):
        super(NoiseFilter, self).__init__()
        self.max_speed = max_speed

    def filter(self, traj):
        pt_list = traj.pt_list
        if len(pt_list) <= 1:
            return None

        remove_inds = []
        for i in range(1, len(pt_list) - 1):
            time_span_pre = (pt_list[i].time - pt_list[i - 1].time).total_seconds()
            dist_pre = distance(pt_list[i - 1], pt_list[i])
            time_span_next = (pt_list[i + 1].time - pt_list[i].time).total_seconds()
            dist_next = distance(pt_list[i], pt_list[i + 1])

            # Remove points with zero time span
            if time_span_pre == 0:
                remove_inds.append(i - 1)
                continue  # Skip further checks for this point since it's invalid
            if time_span_next == 0:
                remove_inds.append(i + 1)
                continue  # Skip further checks for this point since it's invalid

            speed_pre = dist_pre / time_span_pre
            speed_next = dist_next / time_span_next

            # the first point is outlier
            if i == 1 and speed_pre > self.max_speed > speed_next:
                remove_inds.append(0)
            # the last point is outlier
            elif i == len(pt_list) - 2 and speed_next > self.max_speed >= speed_pre:
                remove_inds.append(len(pt_list) - 1)
            # middle point is outlier
            elif speed_pre > self.max_speed and speed_next > self.max_speed:
                remove_inds.append(i)

        # Remove duplicates from remove_inds
        remove_inds = list(set(remove_inds))

        # Generate the cleaned point list, skipping points marked for removal
        clean_pt_list = []
        previous_time = None
        for j, pt in enumerate(pt_list):
            if j in remove_inds:
                continue
            if pt.time == previous_time:
                continue
            clean_pt_list.append(pt)
            previous_time = pt.time

        if len(clean_pt_list) > 1:
            return Trajectory(traj.oid, self.get_tid(traj.oid, clean_pt_list), clean_pt_list)
        else:
            return None

# remove point
class STFilter(NoiseFilter):
    """
    Remove outlier if it is out of the mbr
    """
    def __init__(self, mbr, start_time, end_time):
        super(STFilter, self).__init__()
        self.mbr = mbr
        self.start_time = start_time
        self.end_time = end_time

    def filter(self, traj):
        pt_list = traj.pt_list
        if len(pt_list) <= 1:
            return None
        clean_pt_list = []
        for pt in pt_list:
            if self.start_time <= pt.time < self.end_time and self.mbr.contains(pt.lat, pt.lng):
                clean_pt_list.append(pt)
        if len(clean_pt_list) > 1:
            return Trajectory(traj.oid, self.get_tid(traj.oid, clean_pt_list), clean_pt_list)
        else:
            return None

