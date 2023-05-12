DEL_COMMAND=gio trash

build:
	$(DEL_COMMAND) -f dist/*
	poetry build

upload:
	twine upload dist/*

build-and-upload: build upload
