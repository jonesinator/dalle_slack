dalle.zip: dalle.py Pipfile.lock
	pylint dalle.py
	rm -rf build
	mkdir -p build
	cp dalle.py build
	cp -r $(shell pipenv --venv)/lib/python3.9/site-packages/* build
	rm -rf build/boto*
	cd build && zip -r ../dalle.zip .
	rm -rf build
