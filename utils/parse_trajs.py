#!/usr/bin/python3
# coding: utf-8
# @Time    : 2020/9/23 15:40
# Reference: https://github.com/huiminren/tptk/blob/master/common/trajectory.py

import re
from datetime import datetime
import pandas as pd

from common.trajectory import Trajectory, STPoint
from map_matching.candidate_point import CandidatePoint


class ParseTraj:
    """
    ParseTraj is an abstract class for parsing trajectory.
    It defines parse() function for parsing trajectory.
    """
    def __init__(self):
        pass

    def parse(self, input_path):
        """
        The parse() function is to load data to a list of Trajectory()
        """
        pass


class ParseRawTraj(ParseTraj):
    """
    Parse original GPS points to trajectories list. No extra data preprocessing
    """
    def __init__(self):
        super().__init__()

    def parse(self, input_path):
        """
        Args:
        -----
        input_path:
            str. input directory with file name
        Returns:
        --------
        trajs:
            list. list of trajectories. trajs contain input_path file's all gps points
        """
        time_format = '%Y/%m/%d %H:%M:%S'
        tid_to_remove = '[:/ ]'
        with open(input_path, 'r') as f:
            trajs = []
            pt_list = []
            for line in f.readlines():
                attrs = line.rstrip().split(',')
                if attrs[0] == '#':
                    if len(pt_list) > 1:
                        traj = Trajectory(oid, tid, pt_list)
                        trajs.append(traj)
                    oid = attrs[2]
                    tid = attrs[1]
                    pt_list = []
                else:
                    lat = float(attrs[1])
                    lng = float(attrs[2])
                    pt = STPoint(lat, lng, datetime.strptime(attrs[0], time_format))
                    # pt contains all the attributes of class STPoint
                    pt_list.append(pt)
            if len(pt_list) > 1:
                traj = Trajectory(oid, tid, pt_list)
                trajs.append(traj)
        return trajs


class ParseMMTraj(ParseTraj):
    """
    Parse map matched GPS points to trajectories list. No extra data preprocessing
    """
    def __init__(self):
        super().__init__()

    def parse(self, input_path, id_dict):
        """
        Args:
        -----
        input_path:
            str. input directory with file name
            id_dict: 原始uid到顺序uid的映射 uid2index.json
        Returns:
        --------
        trajs:
            list. list of trajectories. trajs contain input_path file's all gps points
        """
        time_format = '%Y/%m/%d %H:%M:%S'
        tid_to_remove = '[:/ ]'
        with open(input_path, 'r') as f:
            user_id = []
            trajs = []
            pt_list = []
            for line in f.readlines():
                attrs = line.rstrip().split(',')
                if attrs[0] == '#':
                    if len(pt_list) > 1:
                        traj = Trajectory(oid, tid, pt_list)
                        trajs.append(traj)
                        user_id.append(uid)

                    oid = attrs[2]
                    tid = attrs[1]
                    uid = id_dict[attrs[6]]
                    pt_list = []
                else:
                    lat = float(attrs[1])
                    lng = float(attrs[2])
                    if attrs[3] == 'None':
                        candi_pt = None
                    else:
                        eid = int(attrs[3])
                        proj_lat = float(attrs[4])
                        proj_lng = float(attrs[5])
                        error = float(attrs[6])
                        offset = float(attrs[7])
                        rate = float(attrs[8])
                        candi_pt = CandidatePoint(proj_lat, proj_lng, eid, error, offset, rate)
                    pt = STPoint(lat, lng, datetime.strptime(attrs[0], time_format), {'candi_pt': candi_pt})
                    # pt contains all the attributes of class STPoint
                    pt_list.append(pt)
            if len(pt_list) > 1:
                traj = Trajectory(oid, tid, pt_list)
                trajs.append(traj)
                user_id.append(uid)
        return trajs, user_id
class ParseMMTraj_MTraj(ParseTraj):
    """
    Parse map matched GPS points to trajectories list. No extra data preprocessing
    """
    def __init__(self):
        super().__init__()

    def parse(self, input_path):
        """
        Args:
        -----
        input_path:
            str. input directory with file name
        Returns:
        --------
        trajs:
            list. list of trajectories. trajs contain input_path file's all gps points
        """
        time_format = '%Y/%m/%d %H:%M:%S'
        tid_to_remove = '[:/ ]'
        with open(input_path, 'r') as f:
            trajs = []
            pt_list = []
            for line in f.readlines():
                attrs = line.rstrip().split(',')
                if attrs[0] == '#':
                    if len(pt_list) > 1:
                        traj = Trajectory(oid, tid, pt_list)
                        trajs.append(traj)
                    oid = attrs[2]
                    tid = attrs[1]
                    pt_list = []
                else:
                    lat = float(attrs[1])
                    lng = float(attrs[2])
                    if attrs[3] == 'None':
                        candi_pt = None
                    else:
                        eid = int(attrs[3])
                        proj_lat = float(attrs[4])
                        proj_lng = float(attrs[5])
                        error = float(attrs[6])
                        offset = float(attrs[7])
                        rate = float(attrs[8])
                        candi_pt = CandidatePoint(proj_lat, proj_lng, eid, error, offset, rate)
                    pt = STPoint(lat, lng, datetime.strptime(attrs[0], time_format), {'candi_pt': candi_pt})
                    # pt contains all the attributes of class STPoint
                    pt_list.append(pt)
            if len(pt_list) > 1:
                traj = Trajectory(oid, tid, pt_list)
                trajs.append(traj)
        return trajs

