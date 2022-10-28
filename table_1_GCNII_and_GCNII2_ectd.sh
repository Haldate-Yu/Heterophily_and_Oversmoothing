if [ -z "$1" ]; then
  echo "empty topk input!"
  topk=2
else
  topk=$1
fi

python -u full-supervised.py --data cora --layer 64 --alpha 0.2 --weight_decay 1e-4 --model GCNII --pinv --topk $topk
python -u full-supervised.py --data cora --layer 64 --alpha 0.2 --weight_decay 1e-4 --variant --model GCNII --pinv --topk $topk
python -u full-supervised.py --data citeseer --layer 64 --weight_decay 5e-6 --model GCNII --pinv --topk $topk
python -u full-supervised.py --data citeseer --layer 64 --weight_decay 5e-6 --variant --model GCNII --pinv --topk $topk
python -u full-supervised.py --data chameleon --layer 4 --lamda 1.5 --alpha 0.2 --weight_decay 5e-4 --model GCNII --pinv --topk $topk
python -u full-supervised.py --data chameleon --layer 4 --lamda 1.5 --alpha 0.2 --weight_decay 5e-4 --variant --model GCNII --pinv --topk $topk
python -u full-supervised.py --data cornell --layer 16 --lamda 1 --weight_decay 1e-3 --model GCNII --pinv --topk $topk
python -u full-supervised.py --data cornell --layer 16 --lamda 1 --weight_decay 1e-3 --variant --model GCNII --pinv --topk $topk
python -u full-supervised.py --data texas --layer 32 --lamda 1.5 --weight_decay 1e-4 --model GCNII --pinv --topk $topk
python -u full-supervised.py --data texas --layer 32 --lamda 1.5 --weight_decay 1e-4 --variant --model GCNII --pinv --topk $topk
python -u full-supervised.py --data wisconsin --layer 16 --lamda 1 --weight_decay 5e-4 --model GCNII --pinv --topk $topk
python -u full-supervised.py --data wisconsin --layer 16 --lamda 1 --weight_decay 5e-4 --variant --model GCNII --pinv --topk $topk
python -u full-supervised.py --data squirrel --layer 2 --weight_decay 1e-3 --model GCNII --hidden 16 --dropout 0.6 --pinv --topk $topk
python -u full-supervised.py --data squirrel --layer 2 --weight_decay 1e-3 --model GCNII --variant --hidden 16 --dropout 0.6 --pinv --topk $topk
python -u full-supervised.py --data film --layer 2 --weight_decay 1e-3 --model GCNII --variant --hidden 16 --dropout 0 --pinv --topk $topk
python -u full-supervised.py --data film --layer 2 --weight_decay 1e-3 --model GCNII --hidden 16 --dropout 0 --pinv --topk $topk
# python -u full-supervised.py --data pubmed --layer 64 --alpha 0.1 --weight_decay 5e-6 --model GCNII --pinv --topk $topk
# python -u full-supervised.py --data pubmed --layer 64 --alpha 0.1 --weight_decay 5e-6 --variant --model GCNII --pinv --topk $topk


