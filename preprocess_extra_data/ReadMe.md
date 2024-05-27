# Brief Description of MMTraj Data Preprocessing

1. run `uid_rid_dara.py` to generate road network jsons and uid json
2. run `split_data.py` to split map matched trajs into 'train' 'valid' 'test'
3. run `build_graph.` to generation macro trajectory flow graph. [注意轨迹文件的eid是raw_id]
    - `graph_A.csv` the adjacent matrix of road
    - `graph_X.csv` node_name/road_id,start_lat,start_lng,end_lat,end_lng,length,level, freq_cnt
    - `graph.pkl` G
    - `graph_node_id2idx.txt` {node}, {i} 
    - `graph_edge.edgelist` {node_id2idx[src_node]} {node_id2idx[dst_node]} {weight}
4. run `cal_road_condation.py` to generate the road flow condition file
    - `flow_new.npy`
5. run `generateSE.py` to generate Graph Structure Embedding file
    - `SE.txt`