test:
	flake8
	python setup.py test	

install_precommit: 
	echo "#!/bin/sh\nmake test" > .git/hooks/pre-commit;
	chmod +x .git/hooks/pre-commit;

distribute:
	devpi upload