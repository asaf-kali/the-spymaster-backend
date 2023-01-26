DEL_COMMAND=gio trash

build:
	$(DEL_COMMAND) -f dist/*
	python -m build

upload:
	twine upload dist/*

build-and-upload: build upload
