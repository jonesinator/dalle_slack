dalle.zip: dalle.py Pipfile.lock
	pylint dalle.py
	rm -rf build
	mkdir -p build
	cp dalle.py build
	cp -r $(shell pipenv --venv)/lib/python3.9/site-packages/* build
	rm -rf build/boto*
	cd build && zip -r ../dalle.zip .
	rm -rf build

dalle_dispatch.zip: dalle_dispatch.py Pipfile_dispatch.lock
	pylint dalle_dispatch.py
	rm -rf build_dispatch
	mkdir -p build_dispatch
	cp dalle_dispatch.py build_dispatch
	cp -r $(shell pipenv --venv)/lib/python3.9/site-packages/* build_dispatch
	rm -rf build_dispatch/boto*
	cd build_dispatch && zip -r ../dalle_dispatch.zip .
	rm -rf build_dispatch
