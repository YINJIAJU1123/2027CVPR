all:
	bash scripts/build_paper.sh

figures:
	python3 scripts/render_evidence.py
	python3 scripts/render_followup.py
	python3 scripts/render_completed.py

check: all
	bash scripts/check_paper.sh
