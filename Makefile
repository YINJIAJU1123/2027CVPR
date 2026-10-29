all:
	bash scripts/build_paper.sh

figures:
	python3 scripts/render_evidence.py

check: all
	bash scripts/check_paper.sh
