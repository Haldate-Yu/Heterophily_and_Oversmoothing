import os
import time

# import dgl
import scipy
import numpy as np
import scipy.sparse as sp
import torch
import torch.nn.functional as F
import sys
import pickle as pkl
import networkx as nx
import json
from networkx.readwrite import json_graph
import pdb
from torch_sparse import coalesce
from sklearn.neighbors import kneighbors_graph

sys.setrecursionlimit(99999)


def accuracy(output, labels):
    preds = output.max(1)[1].type_as(labels)
    correct = preds.eq(labels).double()
    correct = correct.sum()
    return correct / len(labels)


def normalize(mx):
    """Row-normalize sparse matrix"""
    rowsum = np.array(mx.sum(1))
    rowsum = (rowsum == 0) * 1 + rowsum
    r_inv = np.power(rowsum, -1).flatten()
    r_inv[np.isinf(r_inv)] = 0.
    r_mat_inv = sp.diags(r_inv)
    mx = r_mat_inv.dot(mx)
    return mx


def softmax_normalized_adjacency(adj):
    # adj = sp.coo_matrix(adj)
    # adj = adj + sp.eye(adj.shape[0])
    # print(adj, type(adj))
    adj = np.where(adj > 0., adj, -9e15)
    adj -= np.max(adj, axis=1, keepdims=True)
    adj_normalized = np.exp(adj) / np.sum(np.exp(adj), axis=1, keepdims=True)
    return sp.coo_matrix(adj_normalized)


def row_normalized_adjacency(adj):
    adj = sp.coo_matrix(adj)
    adj = adj + sp.eye(adj.shape[0])
    row_sum = np.array(adj.sum(1))
    row_sum = (row_sum == 0) * 1 + row_sum
    adj_normalized = adj / row_sum
    return sp.coo_matrix(adj_normalized)


def sys_normalized_adjacency(adj):
    adj = sp.coo_matrix(adj)
    adj = adj + sp.eye(adj.shape[0])
    row_sum = np.array(adj.sum(1))
    row_sum = (row_sum == 0) * 1 + row_sum
    d_inv_sqrt = np.power(row_sum, -0.5).flatten()
    d_inv_sqrt[np.isinf(d_inv_sqrt)] = 0.
    d_mat_inv_sqrt = sp.diags(d_inv_sqrt)
    return d_mat_inv_sqrt.dot(adj).dot(d_mat_inv_sqrt).tocoo()


def sparse_mx_to_torch_sparse_tensor(sparse_mx, model_type):
    """Convert a scipy sparse matrix to a torch sparse tensor."""
    sparse_mx = sparse_mx.tocoo().astype(np.float32)
    indices = torch.from_numpy(
        np.vstack((sparse_mx.row, sparse_mx.col)).astype(np.int64))
    values = torch.from_numpy(sparse_mx.data)
    shape = torch.Size(sparse_mx.shape)
    if model_type == 'GPRGNN':
        edge_index, _ = coalesce(indices, None, shape[0], shape[1])
        return edge_index
    else:
        return torch.sparse.FloatTensor(indices, values, shape)


def parse_index_file(filename):
    """Parse index file."""
    index = []
    for line in open(filename):
        index.append(int(line.strip()))
    return index


# adapted from PetarV/GAT
def run_dfs(adj, msk, u, ind, nb_nodes):
    if msk[u] == -1:
        msk[u] = ind
        # for v in range(nb_nodes):
        for v in adj[u, :].nonzero()[1]:
            # if adj[u,v]== 1:
            run_dfs(adj, msk, v, ind, nb_nodes)


def dfs_split(adj):
    # Assume adj is of shape [nb_nodes, nb_nodes]
    nb_nodes = adj.shape[0]
    ret = np.full(nb_nodes, -1, dtype=np.int32)

    graph_id = 0

    for i in range(nb_nodes):
        if ret[i] == -1:
            run_dfs(adj, ret, i, graph_id, nb_nodes)
            graph_id += 1

    return ret


def test(adj, mapping):
    nb_nodes = adj.shape[0]
    for i in range(nb_nodes):
        # for j in range(nb_nodes):
        for j in adj[i, :].nonzero()[1]:
            if mapping[i] != mapping[j]:
                #  if adj[i,j] == 1:
                return False
    return True


def find_split(adj, mapping, ds_label):
    nb_nodes = adj.shape[0]
    dict_splits = {}
    for i in range(nb_nodes):
        # for j in range(nb_nodes):
        for j in adj[i, :].nonzero()[1]:
            if mapping[i] == 0 or mapping[j] == 0:
                dict_splits[0] = None
            elif mapping[i] == mapping[j]:
                if ds_label[i]['val'] == ds_label[j]['val'] and ds_label[i]['test'] == ds_label[j]['test']:

                    if mapping[i] not in dict_splits.keys():
                        if ds_label[i]['val']:
                            dict_splits[mapping[i]] = 'val'

                        elif ds_label[i]['test']:
                            dict_splits[mapping[i]] = 'test'

                        else:
                            dict_splits[mapping[i]] = 'train'

                    else:
                        if ds_label[i]['test']:
                            ind_label = 'test'
                        elif ds_label[i]['val']:
                            ind_label = 'val'
                        else:
                            ind_label = 'train'
                        if dict_splits[mapping[i]] != ind_label:
                            print('inconsistent labels within a graph exiting!!!')
                            return None
                else:
                    print('label of both nodes different, exiting!!')
                    return None
    return dict_splits


def load_ppi():
    print('Loading G...')
    with open('ppi/ppi-G.json') as jsonfile:
        g_data = json.load(jsonfile)
    # print (len(g_data))
    G = json_graph.node_link_graph(g_data)

    # Extracting adjacency matrix
    adj = nx.adjacency_matrix(G)

    prev_key = ''
    for key, value in g_data.items():
        if prev_key != key:
            # print (key)
            prev_key = key

    # print ('Loading id_map...')
    with open('ppi/ppi-id_map.json') as jsonfile:
        id_map = json.load(jsonfile)
    # print (len(id_map))

    id_map = {int(k): int(v) for k, v in id_map.items()}
    for key, value in id_map.items():
        id_map[key] = [value]
    # print (len(id_map))

    print('Loading features...')
    features_ = np.load('ppi/ppi-feats.npy')
    # print (features_.shape)

    # standarizing features
    from sklearn.preprocessing import StandardScaler

    train_ids = np.array([id_map[n] for n in G.nodes() if not G.node[n]['val'] and not G.node[n]['test']])
    train_feats = features_[train_ids[:, 0]]
    scaler = StandardScaler()
    scaler.fit(train_feats)
    features_ = scaler.transform(features_)

    features = sp.csr_matrix(features_).tolil()

    print('Loading class_map...')
    class_map = {}
    with open('ppi/ppi-class_map.json') as jsonfile:
        class_map = json.load(jsonfile)
    # print (len(class_map))

    # pdb.set_trace()
    # Split graph into sub-graphs
    # print ('Splitting graph...')
    splits = dfs_split(adj)

    # Rearrange sub-graph index and append sub-graphs with 1 or 2 nodes to bigger sub-graphs
    # print ('Re-arranging sub-graph IDs...')
    list_splits = splits.tolist()
    group_inc = 1

    for i in range(np.max(list_splits) + 1):
        if list_splits.count(i) >= 3:
            splits[np.array(list_splits) == i] = group_inc
            group_inc += 1
        else:
            # splits[np.array(list_splits) == i] = 0
            ind_nodes = np.argwhere(np.array(list_splits) == i)
            ind_nodes = ind_nodes[:, 0].tolist()
            split = None

            for ind_node in ind_nodes:
                if g_data['nodes'][ind_node]['val']:
                    if split is None or split == 'val':
                        splits[np.array(list_splits) == i] = 21
                        split = 'val'
                    else:
                        raise ValueError('new node is VAL but previously was {}'.format(split))
                elif g_data['nodes'][ind_node]['test']:
                    if split is None or split == 'test':
                        splits[np.array(list_splits) == i] = 23
                        split = 'test'
                    else:
                        raise ValueError('new node is TEST but previously was {}'.format(split))
                else:
                    if split is None or split == 'train':
                        splits[np.array(list_splits) == i] = 1
                        split = 'train'
                    else:
                        pdb.set_trace()
                        raise ValueError('new node is TRAIN but previously was {}'.format(split))

    # counting number of nodes per sub-graph
    list_splits = splits.tolist()
    nodes_per_graph = []
    for i in range(1, np.max(list_splits) + 1):
        nodes_per_graph.append(list_splits.count(i))

    # Splitting adj matrix into sub-graphs
    subgraph_nodes = np.max(nodes_per_graph)
    adj_sub = np.empty((len(nodes_per_graph), subgraph_nodes, subgraph_nodes))
    feat_sub = np.empty((len(nodes_per_graph), subgraph_nodes, features.shape[1]))
    labels_sub = np.empty((len(nodes_per_graph), subgraph_nodes, 121))

    for i in range(1, np.max(list_splits) + 1):
        # Creating same size sub-graphs
        indexes = np.where(splits == i)[0]
        subgraph_ = adj[indexes, :][:, indexes]

        if subgraph_.shape[0] < subgraph_nodes or subgraph_.shape[1] < subgraph_nodes:
            subgraph = np.identity(subgraph_nodes)
            feats = np.zeros([subgraph_nodes, features.shape[1]])
            labels = np.zeros([subgraph_nodes, 121])
            # adj
            subgraph = sp.csr_matrix(subgraph).tolil()
            subgraph[0:subgraph_.shape[0], 0:subgraph_.shape[1]] = subgraph_
            adj_sub[i - 1, :, :] = subgraph.todense()
            # feats
            feats[0:len(indexes)] = features[indexes, :].todense()
            feat_sub[i - 1, :, :] = feats
            # labels
            for j, node in enumerate(indexes):
                labels[j, :] = np.array(class_map[str(node)])
            labels[indexes.shape[0]:subgraph_nodes, :] = np.zeros([121])
            labels_sub[i - 1, :, :] = labels

        else:
            adj_sub[i - 1, :, :] = subgraph_.todense()
            feat_sub[i - 1, :, :] = features[indexes, :].todense()
            for j, node in enumerate(indexes):
                labels[j, :] = np.array(class_map[str(node)])
            labels_sub[i - 1, :, :] = labels

    # Get relation between id sub-graph and tran,val or test set
    dict_splits = find_split(adj, splits, g_data['nodes'])

    # Testing if sub graphs are isolated
    # print ('Are sub-graphs isolated?')
    # print (test(adj, splits))

    # Splitting tensors into train,val and test
    train_split = []
    val_split = []
    test_split = []
    for key, value in dict_splits.items():
        if dict_splits[key] == 'train':
            train_split.append(int(key) - 1)
        elif dict_splits[key] == 'val':
            val_split.append(int(key) - 1)
        elif dict_splits[key] == 'test':
            test_split.append(int(key) - 1)

    train_adj = adj_sub[train_split, :, :]
    val_adj = adj_sub[val_split, :, :]
    test_adj = adj_sub[test_split, :, :]

    train_feat = feat_sub[train_split, :, :]
    val_feat = feat_sub[val_split, :, :]
    test_feat = feat_sub[test_split, :, :]

    train_labels = labels_sub[train_split, :, :]
    val_labels = labels_sub[val_split, :, :]
    test_labels = labels_sub[test_split, :, :]

    train_nodes = np.array(nodes_per_graph[train_split[0]:train_split[-1] + 1])
    val_nodes = np.array(nodes_per_graph[val_split[0]:val_split[-1] + 1])
    test_nodes = np.array(nodes_per_graph[test_split[0]:test_split[-1] + 1])

    # Masks with ones

    tr_msk = np.zeros((len(nodes_per_graph[train_split[0]:train_split[-1] + 1]), subgraph_nodes))
    vl_msk = np.zeros((len(nodes_per_graph[val_split[0]:val_split[-1] + 1]), subgraph_nodes))
    ts_msk = np.zeros((len(nodes_per_graph[test_split[0]:test_split[-1] + 1]), subgraph_nodes))

    for i in range(len(train_nodes)):
        for j in range(train_nodes[i]):
            tr_msk[i][j] = 1

    for i in range(len(val_nodes)):
        for j in range(val_nodes[i]):
            vl_msk[i][j] = 1

    for i in range(len(test_nodes)):
        for j in range(test_nodes[i]):
            ts_msk[i][j] = 1

    train_adj_list = []
    val_adj_list = []
    test_adj_list = []
    for i in range(train_adj.shape[0]):
        adj = sp.coo_matrix(train_adj[i])
        adj = adj + adj.T.multiply(adj.T > adj) - adj.multiply(adj.T > adj)
        tmp = sys_normalized_adjacency(adj)
        train_adj_list.append(sparse_mx_to_torch_sparse_tensor(tmp))
    for i in range(val_adj.shape[0]):
        adj = sp.coo_matrix(val_adj[i])
        adj = adj + adj.T.multiply(adj.T > adj) - adj.multiply(adj.T > adj)
        tmp = sys_normalized_adjacency(adj)
        val_adj_list.append(sparse_mx_to_torch_sparse_tensor(tmp))
        adj = sp.coo_matrix(test_adj[i])
        adj = adj + adj.T.multiply(adj.T > adj) - adj.multiply(adj.T > adj)
        tmp = sys_normalized_adjacency(adj)
        test_adj_list.append(sparse_mx_to_torch_sparse_tensor(tmp))

    train_feat = torch.FloatTensor(train_feat)
    val_feat = torch.FloatTensor(val_feat)
    test_feat = torch.FloatTensor(test_feat)

    train_labels = torch.FloatTensor(train_labels)
    val_labels = torch.FloatTensor(val_labels)
    test_labels = torch.FloatTensor(test_labels)

    tr_msk = torch.LongTensor(tr_msk)
    vl_msk = torch.LongTensor(vl_msk)
    ts_msk = torch.LongTensor(ts_msk)

    return train_adj_list, val_adj_list, test_adj_list, train_feat, val_feat, test_feat, train_labels, val_labels, test_labels, train_nodes, val_nodes, test_nodes


def cal_2hop_adj(args, adj):
    os.makedirs('./2hop-dataset', exist_ok=True)
    file = './2hop-dataset/{}.pt'.format(args.data)

    if os.path.exists(file):
       _2nd_adj = torch.load(file)
    else:
        dense_adj = adj.to_dense()
        dense_2nd_adj = dense_adj @ dense_adj
        _2nd_adj = ((dense_2nd_adj > 0.).to(torch.long) + dense_adj) == 1.
        _2nd_adj = _2nd_adj.long()
        torch.save(_2nd_adj, file)
        
    return _2nd_adj


def cal_knn(features, knn_neighbors=5):
    knn_graph = kneighbors_graph(features.numpy(), n_neighbors=knn_neighbors, metric='cosine')
    return knn_graph.toarray()


def cal_mfpt(args, adj, topk):
    os.makedirs('./pinv-dataset', exist_ok=True)
    file = './pinv-dataset/{}.npy'.format(args.data)

    if os.path.exists(file):
        mfpt = np.load(file)
    else:
        adj = adj.to_dense().numpy()
        adj = sp.csr_matrix(adj)

        adj = (adj + sp.eye(adj.shape[0])).toarray()
        nnodes = adj.shape[0]
        deg = np.diag(adj.sum(1))
        # Symmetric Form
        d_inv_sqrt = np.power(deg, -0.5)
        d_inv_sqrt[np.isinf(d_inv_sqrt)] = 0.
        lap = np.identity(nnodes) - d_inv_sqrt.dot(adj).dot(d_inv_sqrt)
        # lap_pinv = np.linalg.pinv(lap)
        lap_pinv = scipy.linalg.pinvh(lap)

        volG = deg.sum().sum()
        tmp = lap_pinv @ deg @ np.ones((nnodes, 1))
        AFT = -lap_pinv * volG + tmp - tmp.T + np.diag(lap_pinv) * volG
        AFT = AFT / volG

        mfpt = AFT + AFT.T
        mfpt = np.power(mfpt, -1.)
        mfpt[np.isinf(mfpt)] = 0.
        # mfpt[mfpt < 0] = 1.
        np.save(file, mfpt)

    # strict rules
    mfpt[mfpt < 0.] = 0.
    # soft rules
    # mfpt[mfpt < 0.] = 1.
    
    # topk filter
    mfpt = np.apply_along_axis(get_topk_matrix, 1, mfpt, k=topk)
    # thres filter
    # mfpt[mfpt < topk] = 0.
    # use topo only
    mfpt = np.where(mfpt > 0., 1., 0.)
    # adj filter
    # adj = adj.to_dense().numpy()
    # adj = sp.csr_matrix(adj)
    # adj = (adj + sp.eye(adj.shape[0])).toarray()
    # mfpt = np.where(adj <= 0., 0., mfpt)

    return mfpt

    # self loops
    # mfpt += np.eye(mfpt.shape[0])
    # normalize adj
    # row_sum = mfpt.sum(1)
    # row_sum - (row_sum == 0) * 1 + row_sum
    # deg_mfpt = np.diag(row_sum)
    # d_inv_sqrt_mfpt = np.power(deg_mfpt, -0.5)
    # d_inv_sqrt_mfpt[np.isinf(d_inv_sqrt_mfpt)] = 0.
    # mfpt = d_inv_sqrt_mfpt.dot(mfpt).dot(d_inv_sqrt_mfpt)

    # return mfpt
    # mfpt = sp.coo_matrix(mfpt).tocoo().astype(np.float32)
    # indices = torch.from_numpy(
    #     np.vstack((mfpt.row, mfpt.col)).astype(np.int64))
    # values = torch.from_numpy(mfpt.data)
    # shape = torch.Size(mfpt.shape)
    # return torch.sparse.FloatTensor(indices, values, shape)


def logger(args, acc_list, t_total):
    os.makedirs('./results', exist_ok=True)
    file = './results/{}.txt'.format(args.model)

    summary_1 = '\ndataset={}, hidden={}, layer={}, lr={}, wd={}' \
        .format(args.data, args.hidden, args.layer, args.lr, args.weight_decay)

    if args.pinv is True:
        summary_1 += ' ECTD topk={}'.format(args.topk)
        
    train_cost = time.time() - t_total
    test_acc = np.mean(acc_list)
    test_std = np.std(acc_list)
    summary_2 = 'Train cost: {:.4f}s, Test acc.:{:.2f}, Test std.:{:.2f}, Final Results: {:.2f} ± {:.2f}' \
        .format(train_cost, test_acc, test_std, test_acc, test_std)

    with open(file, 'a+') as f:
        f.write('{}: {}\n{}: {}\n{}\n'.format(
            'Model Details',
            summary_1,
            'Final Result',
            summary_2,
            '-' * 30
        ))


def get_topk_matrix(adj, k=20):
    indexes = adj.argsort()[-k:][::-1]
    a = set(indexes)
    b = set(list(range(adj.shape[0])))
    adj[list(b.difference(a))] = 0

    return adj
