if [ -z "$1" ]; then
  echo "empty topk input!"
  topk=2
else
  topk=$1
fi

python -u full-supervised.py --data cora --layer 2 --weight_decay 5e-4 --model GAT --hidden 8 --dropout 0.6 --lr 0.005 --pinv --topk $topk
python -u full-supervised.py --data citeseer --layer 2 --weight_decay 5e-4 --model GAT --hidden 8 --dropout 0.6 --lr 0.005 --pinv --topk $topk
python -u full-supervised.py --data chameleon --layer 2 --weight_decay 5e-5 --model GAT --hidden 8 --dropout 0.6 --lr 0.005 --pinv --topk $topk
python -u full-supervised.py --data cornell --layer 2 --weight_decay 5e-5 --model GAT --hidden 8 --dropout 0.6 --lr 0.005 --pinv --topk $topk
python -u full-supervised.py --data texas --layer 2 --weight_decay 5e-5 --model GAT --hidden 8 --dropout 0.6 --lr 0.005 --pinv --topk $topk
python -u full-supervised.py --data wisconsin --layer 2 --weight_decay 5e-5 --model GAT --hidden 8 --dropout 0.6 --lr 0.005 --pinv --topk $topk
python -u full-supervised.py --data film --layer 2 --weight_decay 5e-5 --model GAT --hidden 8 --dropout 0.6 --lr 0.005 --use_sparse --pinv --topk $topk
python -u full-supervised.py --data squirrel --layer 2 --weight_decay 5e-5 --model GAT --hidden 8 --dropout 0.6 --lr 0.005 --use_sparse --pinv --topk $topk
# python -u full-supervised.py --data pubmed --layer 2 --weight_decay 5e-5 --model GAT --hidden 8 --dropout 0.6 --lr 0.005 --use_sparse --pinv --topk $topk
