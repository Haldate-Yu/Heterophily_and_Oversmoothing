# Heterophily and Oversmoothing
Codes for the paper "Two Sides of the Same Coin: Heterophily and Oversmoothing in Graph Convolutional Neural Networks", which is accepted to The IEEE International Conference on Data Mining (ICDM 2022). [Heterophily and Oversmoothing]: https://arxiv.org/abs/2102.06462

## To run the code
### Environment

```
Python=3.7.8
numpy=1.18.5
scipy=1.5.3
pytorch=1.6.0
networkx=2.5
scikit-learn=0.23.2
dgl=0.4.3
```

**dgl is only used to run baseline GeomGCN.**

If you do **not** need to run GeomGCN baseline, you can install **any version of dgl** or remove the the codes related to the GeomGCN baseline (in process.py and full-supervised.py).

------

### Datasets

|             | Texas | Wisconsin | Actor  | Squirrel | Chameleon | Cornell | Citeseer | Pubmed | Cora  |
| :---------: | :---: | :-------: | :----: | :------: | :-------: | :-----: | :------: | :----: | :---: |
| Homo. level | 0.11  |   0.21    |  0.22  |   0.22   |   0.23    |  0.30   |   0.74   |  0.8   | 0.81  |
|    Nodes    |  183  |    251    | 7,600  |  5,201   |   2,277   |   183   |  3,327   | 19,717 | 2,708 |
|    Edges    |  295  |    466    | 26,752 | 198,493  |  31,421   |   280   |  4,676   | 44,327 | 5,278 |
|   Classes   |   5   |     5     |   5    |    5     |     5     |    5    |    7     |   3    |   6   |
| Avg Neigh.  | 1.61  |   1.86    |  3.52  |  38.16   |   13.79   |  1.53   |   1.41   |  2.25  | 1.95  |

For all benchmarks, we use the feature vectors, class labels and 10 random splits(48%/32%/20% of nodes per class for train/valid/test). 

### Experiments

#### Experiments in origin paper

To replicate the results of **Table 1**[baselines], you can using ./table_1_[model_name].sh to obatin the results of the specified model, for example:

```bash
bash table_1_GCN.sh
```

To replicate **Table 2**[parameter sensitivity on layers], you can still use hyper-parameters used in table_1_[model_name].sh and modify the layers, for example:

```bash
bash table_1_GCN.sh --layer 4
```

and you still need to manually change the hyper-parameter, or change it to an external input like $1

To replicate **Table B1**[ablation study of GGCN], you can run ./table_B1.sh, for example:

```bash
bash table_B1.sh
```

#### Experiments for ECTD

To replicate the results of ECTD enhanced models, you can use ./table_1_[model_name]_ectd.sh to obtain the results of the specified model, for example:

```bash
bash table_1_GCN_ectd.sh 2
```

with a topk value set to 2, then you will get the result of CTD-GCN[topk=2]. In particular, when you do not enter the topk value, it will be set to 2 by default.

## Cite:

```tex
@article{yan2021two, 
  title={Two sides of the same coin: Heterophily and oversmoothing in graph convolutional neural networks}, 
  author={Yan, Yujun and Hashemi, Milad and Swersky, Kevin and Yang, Yaoqing and Koutra, Danai}, 
  journal={arXiv preprint arXiv:2102.06462}, 
  year={2021}
}
```

