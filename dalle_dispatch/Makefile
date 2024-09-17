dalle_dispatch.zip: dalle_dispatch.py Pipfile.lock
	pylint dalle_dispatch.py
	rm -rf build
	mkdir -p build
	cp dalle_dispatch.py build
	cp -r $(shell pipenv --venv)/lib/python3.12/site-packages/* build
	rm -rf build/boto*
	cd build && zip -r ../dalle_dispatch.zip .
	rm -rf build
