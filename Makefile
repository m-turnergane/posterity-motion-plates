PY ?= python
OUT ?= out
.PHONY: install test render-a render-b render-all clean
install:
	$(PY) -m pip install -r requirements.txt && $(PY) -m pip install -e .
test:
	PYTHONPATH=src $(PY) -m pytest -q
render-a:
	PYTHONPATH=src $(PY) -m motionplates render recipes/poc_a_augustus.yaml --out $(OUT)/a --compare --export-layers $(OUT)/a/layers
render-b:
	PYTHONPATH=src $(PY) -m motionplates render recipes/poc_b_corridor.yaml --out $(OUT)/b --compare --export-layers $(OUT)/b/layers
render-all: render-a render-b
clean:
	rm -rf out cache
