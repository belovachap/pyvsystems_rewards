all:
	python setup.py sdist bdist_wheel

clean:
	rm -rf build dist pyvsystems_rewards.egg-info

upload:
	twine upload dist/*
