import node2vec
import numpy as np
import networkx as nx
from gensim.models import Word2Vec

is_directed = False
p = 2
q = 1
# num_walks = 100
# walk_length = 80
# dimensions = 64
# window_size = 10
# iter = 2


dimensions = 128
window_size = 10
iter = 50

# num_walks = 2
# walk_length = 2
# dimensions = 3
# window_size = 2
# iter = 2

import sys
sys.path.append('../')


def read_graph(edgelist):
    G = nx.read_edgelist(
        edgelist, nodetype=int, data=(('weight',float),),
        create_using=nx.DiGraph())

    return G

def learn_embeddings(walks, dimensions, output_file):
    walks = [list(map(str, walk)) for walk in walks]
    model = Word2Vec(
        walks, vector_size = dimensions, window = 10, min_count=0, sg=1,
        workers = 8, epochs = iter)
    model.wv.save_word2vec_format(output_file)
	
    return

def calculate_laplacian_matrix(adj_mat, mat_type):
    from scipy.sparse.linalg import eigsh
    n_vertex = adj_mat.shape[0]

    # row sum
    deg_mat_row = np.asmatrix(np.diag(np.sum(adj_mat, axis=1)))
    # column sum
    # deg_mat_col = np.asmatrix(np.diag(np.sum(adj_mat, axis=0)))
    deg_mat = deg_mat_row

    adj_mat = np.asmatrix(adj_mat)
    id_mat = np.asmatrix(np.identity(n_vertex))

    if mat_type == 'com_lap_mat':
        # Combinatorial
        com_lap_mat = deg_mat - adj_mat
        return com_lap_mat
    elif mat_type == 'wid_rw_normd_lap_mat':
        # For ChebConv
        rw_lap_mat = np.matmul(np.linalg.matrix_power(deg_mat, -1), adj_mat)
        rw_normd_lap_mat = id_mat - rw_lap_mat
        lambda_max_rw = eigsh(rw_lap_mat, k=1, which='LM', return_eigenvectors=False)[0]
        wid_rw_normd_lap_mat = 2 * rw_normd_lap_mat / lambda_max_rw - id_mat
        return wid_rw_normd_lap_mat
    elif mat_type == 'hat_rw_normd_lap_mat':
        # For GCNConv
        wid_deg_mat = deg_mat + id_mat
        wid_adj_mat = adj_mat + id_mat
        hat_rw_normd_lap_mat = np.matmul(np.linalg.matrix_power(wid_deg_mat, -1), wid_adj_mat)
        return hat_rw_normd_lap_mat
    else:
        raise ValueError(f'ERROR: {mat_type} is unknown.')

def load_graph_adj_mtx(path):
    """A.shape: (num_node, num_node), edge from row_index to col_index with weight"""
    A = np.loadtxt(path, delimiter=',')
    for i in range(A.shape[0]):
        A[i,i] = 0
    A = calculate_laplacian_matrix(A, 'hat_rw_normd_lap_mat')
    for i in range(A.shape[0]):
        A[i,i] = 1
    return A

if __name__ == '__main__':
    city = 'Chengdu'
    Adj_file = f'../data/map/{city}/extra_data/graph_A.csv'
    SE_file = f'../data/map/{city}/extra_data/{city}_SE_' + str(dimensions) + ".txt"
    
    adj_spatial = load_graph_adj_mtx(Adj_file)
    print(adj_spatial.shape)

    nx_G = nx.from_numpy_matrix(adj_spatial)
    print(nx_G.edges())

    G = node2vec.Graph(nx_G, is_directed, p, q)
    G.preprocess_transition_probs()
    
    num_walks, walk_length = 50, 50
    walks = G.simulate_walks(num_walks, walk_length)
    
    print("learning embedding")
    learn_embeddings(walks, dimensions, SE_file)
    print("done")