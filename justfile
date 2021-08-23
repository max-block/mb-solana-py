version := `python3 setup.py --version | tr '+' '-'`

clean:
	rm -rf .pytest_cache build dist *.egg-info


dist: clean
	python3 setup.py sdist bdist_wheel


release: dist
    git diff-index --quiet --cached HEAD --
    twine upload dist/*
    git tag -a 'v{{version}}' -m 'v{{version}}'
    git push origin v{{version}}
