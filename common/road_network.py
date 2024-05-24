import networkx as nx
from rtree import Rtree
from osgeo import ogr
from .spatial_func import SPoint, distance
from .mbr import MBR
import copy
import json
import os

# 字符串到数字的转化规则
candi_highway_types = {
    'motorway': 1,  # 高速公路
    'motorway_link': 1,
    'trunk': 2,  # 高速干道
    'trunk_link': 2,
    'primary': 3,  # 城市主干道
    'primary_link': 3,
    'secondary': 4,  # 城市主干道
    'secondary_link': 5,
    'tertiary': 5,  # 城市次级干道
    'tertiary_link': 5
}

class UndirRoadNetwork(nx.Graph):
    def __init__(self, g, edge_spatial_idx, edge_idx):
        super(UndirRoadNetwork, self).__init__(g)
        # entry: eid
        self.edge_spatial_idx = edge_spatial_idx
        # eid -> edge key (start_coord, end_coord)
        self.edge_idx = edge_idx

    def to_directed(self, as_view=False):
        """
        new edge will have new eid, and each original edge will have two edge with reversed coords
        :return:
        """
        assert as_view is False, "as_view is not supported"
        avail_eid = max([eid for u, v, eid in self.edges.data(data='eid')]) + 1
        g = nx.DiGraph()
        edge_spatial_idx = Rtree()
        edge_idx = {}
        # add nodes
        for n, data in self.nodes(data=True):
            new_data = copy.deepcopy(data)
            g.add_node(n, **new_data)
        # add edges
        for u, v, data in self.edges(data=True):
            mbr = MBR.cal_mbr(data['coords'])
            # add forward edge
            forward_data = copy.deepcopy(data)
            g.add_edge(u, v, **forward_data)
            edge_spatial_idx.insert(forward_data['eid'], (mbr.min_lng, mbr.min_lat, mbr.max_lng, mbr.max_lat))
            edge_idx[forward_data['eid']] = (u, v)
            # add backward edge
            backward_data = copy.deepcopy(data)
            backward_data['eid'] = avail_eid
            avail_eid += 1
            backward_data['coords'].reverse()
            g.add_edge(v, u, **backward_data)
            edge_spatial_idx.insert(backward_data['eid'], (mbr.min_lng, mbr.min_lat, mbr.max_lng, mbr.max_lat))
            edge_idx[backward_data['eid']] = (v, u)
        print('# of nodes:{}'.format(g.number_of_nodes()))
        print('# of edges:{}'.format(g.number_of_edges()))
        return RoadNetwork(g, edge_spatial_idx, edge_idx)

    def range_query(self, mbr):
        """
        spatial range query
        :param mbr: query mbr
        :return: qualified edge keys
        """
        eids = self.edge_spatial_idx.intersection((mbr.min_lng, mbr.min_lat, mbr.max_lng, mbr.max_lat))
        return [self.edge_idx[eid] for eid in eids]
    
    def valid_edge(self, mbr):
        eids = self.edge_spatial_idx.intersection((mbr.min_lng, mbr.min_lat, mbr.max_lng, mbr.max_lat))
        return eids

    def remove_edge(self, u, v):
        edge_data = self[u][v]
        coords = edge_data['coords']
        mbr = MBR.cal_mbr(coords)
        # delete self.edge_idx[eifrom edge index
        del self.edge_idx[edge_data['eid']]
        # delete from spatial index
        self.edge_spatial_idx.delete(edge_data['eid'], (mbr.min_lng, mbr.min_lat, mbr.max_lng, mbr.max_lat))
        # delete from graph
        super(UndirRoadNetwork, self).remove_edge(u, v)

    def add_edge(self, u_of_edge, v_of_edge, **attr):
        coords = attr['coords']
        mbr = MBR.cal_mbr(coords)
        attr['length'] = sum([distance(coords[i], coords[i + 1]) for i in range(len(coords) - 1)])
        # add edge to edge index
        self.edge_idx[attr['eid']] = (u_of_edge, v_of_edge)
        # add edge to spatial index
        self.edge_spatial_idx.insert(attr['eid'], (mbr.min_lng, mbr.min_lat, mbr.max_lng, mbr.max_lat))
        # add edge to graph
        super(UndirRoadNetwork, self).add_edge(u_of_edge, v_of_edge, **attr)


class RoadNetwork(nx.DiGraph):
    def __init__(self, g, edge_spatial_idx, edge_idx):
        super(RoadNetwork, self).__init__(g)
        # entry: eid
        self.edge_spatial_idx = edge_spatial_idx
        # eid -> edge key (start_coord, end_coord)
        self.edge_idx = edge_idx

    def range_query(self, mbr):
        """
        spatial range query
        :param mbr: query mbr
        :return: qualified edge keys
        """
        eids = self.edge_spatial_idx.intersection((mbr.min_lng, mbr.min_lat, mbr.max_lng, mbr.max_lat))
        return [self.edge_idx[eid] for eid in eids]
    
    def valid_edge(self, mbr):
        eids = self.edge_spatial_idx.intersection((mbr.min_lng, mbr.min_lat, mbr.max_lng, mbr.max_lat))
        return eids

    def remove_edge(self, u, v):
        edge_data = self[u][v]
        coords = edge_data['coords']
        mbr = MBR.cal_mbr(coords)
        # delete self.edge_idx[eifrom edge index
        del self.edge_idx[edge_data['eid']]
        # delete from spatial index
        self.edge_spatial_idx.delete(edge_data['eid'], (mbr.min_lng, mbr.min_lat, mbr.max_lng, mbr.max_lat))
        # delete from graph
        super(RoadNetwork, self).remove_edge(u, v)

    def add_edge(self, u_of_edge, v_of_edge, **attr):
        coords = attr['coords']
        mbr = MBR.cal_mbr(coords)
        attr['length'] = sum([distance(coords[i], coords[i + 1]) for i in range(len(coords) - 1)])
        # add edge to edge index
        self.edge_idx[attr['eid']] = (u_of_edge, v_of_edge)
        # add edge to spatial index
        self.edge_spatial_idx.insert(attr['eid'], (mbr.min_lng, mbr.min_lat, mbr.max_lng, mbr.max_lat))
        # add edge to graph
        super(RoadNetwork, self).add_edge(u_of_edge, v_of_edge, **attr)


def load_rn_shp(path, is_directed=True):
    edge_spatial_idx = Rtree()
    edge_idx = {}
    # node uses coordinate as key
    # edge uses coordinate tuple as key
    g = nx.read_shp(path, simplify=True, strict=False)
    if not is_directed:
        g = g.to_undirected()
    # node attrs: nid, pt, ...
    for n, data in g.nodes(data=True):
        data['pt'] = SPoint(n[1], n[0])
        if 'ShpName' in data:
            del data['ShpName']
    # edge attrs: eid, length, coords, ...
    for u, v, data in g.edges(data=True):
        geom_line = ogr.CreateGeometryFromWkb(data['Wkb'])
        coords = []
        for i in range(geom_line.GetPointCount()):
            geom_pt = geom_line.GetPoint(i)
            coords.append(SPoint(geom_pt[1], geom_pt[0]))
        data['coords'] = coords
        data['length'] = sum([distance(coords[i], coords[i+1]) for i in range(len(coords) - 1)])
        env = geom_line.GetEnvelope()
        edge_spatial_idx.insert(data['eid'], (env[0], env[2], env[1], env[3]))
        edge_idx[data['eid']] = (u, v)
        del data['ShpName']
        del data['Json']
        del data['Wkt']
        del data['Wkb']
    print('# of nodes:{}'.format(g.number_of_nodes()))
    print('# of edges:{}'.format(g.number_of_edges()))
    if not is_directed:
        return UndirRoadNetwork(g, edge_spatial_idx, edge_idx)
    else:
        return RoadNetwork(g, edge_spatial_idx, edge_idx)

def process_and_save_rn(path, mbr, root_dir, is_directed=True):
    # 创建空间索引和边索引
    edge_spatial_idx = Rtree()
    edge_idx = {}
    res_dict = {}
    raw2rn_dict = {}
    rn2raw_dict = {}
    raw_rn_dict = {}
    valid_edge_count = 0
    
    # 从shapefile中读取图形
    g = nx.read_shp(path, simplify=True, strict=False)
    if not is_directed:
        g = g.to_undirected()

    # 遍历节点和边
    for n, data in g.nodes(data=True):
        # 将坐标作为节点属性
        data['pt'] = SPoint(n[1], n[0])
        if 'ShpName' in data:
            del data['ShpName']
            
    for u, v, data in g.edges(data=True):
        # 从Wkb数据中创建几何线
        geom_line = ogr.CreateGeometryFromWkb(data['Wkb'])
        coords = []
        res_coords = []
        
        # 提取坐标
        for i in range(geom_line.GetPointCount()):
            geom_pt = geom_line.GetPoint(i)
            coords.append(SPoint(geom_pt[1], geom_pt[0]))
            res_coords.append([geom_pt[1], geom_pt[0]])
            
        data['coords'] = coords
        # 计算边长
        data['length'] = sum([distance(coords[i], coords[i+1]) for i in range(len(coords) - 1)])
        env = geom_line.GetEnvelope()
        edge_spatial_idx.insert(data['eid'], (env[0], env[2], env[1], env[3]))
        edge_idx[data['eid']] = (u, v)
        
        # 转换 'level' 字段
        highway_type = data['highway']
        if highway_type in candi_highway_types:
            data['level'] = candi_highway_types[highway_type]
        else:
            data['level'] = 0  # 默认值，如果类型不在字典中

        # 存储边信息
        eid = data['eid']
        res_dict[eid] = {
            'coords': res_coords,
            'length': data['length'],
            'level': data['level']
        }

        # 存储原始边信息
        raw_rn_dict[eid] = res_dict[eid]
        
        # 删除不必要的数据
        del data['ShpName']
        del data['Json']
        del data['Wkt']
        del data['Wkb']

    # 创建原始路网对象
    if not is_directed:
        rn_raw = UndirRoadNetwork(g, edge_spatial_idx, edge_idx)
    else:
        rn_raw = RoadNetwork(g, edge_spatial_idx, edge_idx)

    # 获取有效边（在空间范围内）
    valid_edges = rn_raw.valid_edge(mbr=mbr)
    
    # 创建有效边的字典
    valid_res_dict = {}
    for valid_edge_id in valid_edges:
        raw_edge_id = valid_edge_id
        valid_edge_data = res_dict[raw_edge_id]
        valid_res_dict[valid_edge_count] = valid_edge_data
        
        # 创建映射
        raw2rn_dict[raw_edge_id] = valid_edge_count
        rn2raw_dict[valid_edge_count] = raw_edge_id
        
        valid_edge_count += 1
    
    # 构建文件路径
    valid_rn_dict_path = os.path.join(root_dir, 'valid_rn_dict.json')
    raw_rn_dict_path = os.path.join(root_dir, 'raw_rn_dict.json')
    raw2rn_dict_path = os.path.join(root_dir, 'raw2rn_dict.json')
    rn2raw_dict_path = os.path.join(root_dir, 'rn2raw_dict.json')

    # 将有效边字典写入JSON文件
    with open(valid_rn_dict_path, 'w') as f:
        json.dump(valid_res_dict, f)

    # 将原始边字典写入JSON文件
    with open(raw_rn_dict_path, 'w') as f:
        json.dump(raw_rn_dict, f)
    
    # 将原始边到有效边的映射写入JSON文件
    with open(raw2rn_dict_path, 'w') as f:
        json.dump(raw2rn_dict, f)
    
    # 将有效边到原始边的映射写入JSON文件
    with open(rn2raw_dict_path, 'w') as f:
        json.dump(rn2raw_dict, f)
    
    print('# of nodes:{}'.format(g.number_of_nodes()))
    print('# of edges:{}'.format(g.number_of_edges()))

def store_rn_shp(rn, target_path):
    print('# of nodes:{}'.format(rn.number_of_nodes()))
    print('# of edges:{}'.format(rn.number_of_edges()))
    for _, data in rn.nodes(data=True):
        if 'pt' in data:
            del data['pt']
    for _, _, data in rn.edges(data=True):
        geo_line = ogr.Geometry(ogr.wkbLineString)
        for coord in data['coords']:
            geo_line.AddPoint(coord.lng, coord.lat)
        data['Wkb'] = geo_line.ExportToWkb()
        del data['coords']
        if 'length' in data:
            del data['length']
    if not rn.is_directed():
        rn = rn.to_directed()
    nx.write_shp(rn, target_path)
