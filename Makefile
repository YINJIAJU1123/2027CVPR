.PHONY: paper check

paper:
	bash scripts/build_paper.sh

check: paper
	bash scripts/check_paper.sh
