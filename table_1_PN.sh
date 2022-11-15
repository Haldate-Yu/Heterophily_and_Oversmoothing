for l in 2 4 8 16 32 64
do
	python -u full-supervised.py --data cora --layer $l --lr 0.005 --dropout 0.6 --weight_decay 5e-4 --model PN --hidden 64
	python -u full-supervised.py --data citeseer --layer $l --lr 0.005 --dropout 0.6 --weight_decay 5e-4 --model PN --hidden 64
	python -u full-supervised.py --data pubmed --layer $l --lr 0.005 --dropout 0.6 --weight_decay 5e-4 --model PN --hidden 64
	python -u full-supervised.py --data chameleon --layer $l --lr 0.005 --dropout 0.6 --weight_decay 5e-4 --model PN --hidden 64
	python -u full-supervised.py --data cornell --layer $l --lr 0.005 --dropout 0.6 --weight_decay 5e-4 --model PN --hidden 64
	python -u full-supervised.py --data texas --layer $l --lr 0.005 --dropout 0.6 --weight_decay 5e-4 --model PN --hidden 64
	python -u full-supervised.py --data wisconsin --layer $l --lr 0.005 --dropout 0.6 --weight_decay 5e-4 --model PN --hidden 64
	python -u full-supervised.py --data squirrel --layer $l --lr 0.005 --dropout 0.6 --weight_decay 5e-4 --model PN --hidden 64
	python -u full-supervised.py --data film --layer $l --lr 0.005 --dropout 0.6 --weight_decay 5e-4 --model PN --hidden 64
done
