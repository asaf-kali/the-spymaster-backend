DEL_COMMAND=gio trash

build:
	$(DEL_COMMAND) -f dist/*
	python -m build

upload-only:
	twine upload dist/*

upload: build upload-only
