TEST_PATH=./
export FLASK_RUN_PORT=8080
export FLASK_ENV=development

testUnit:
	. .venv/bin/activate && pytest --junit-xml=unit.xml --cov-report=xml:coverage.xml --cov-report=html:coverage-html test

tests: testUnit

local:
	flask run
run:
	flask run
build:
	docker build . --tag=status-pin-api:latest
sonar-local:
	sonar-scanner sonar.projectKey=dm sonar.sources=. sonar.host.url=http://localhost:9000 sonar.login=725e074908ee281c938998db550bb91a8335ecb0
install:
	python3 -m venv .venv
	. .venv/bin/activate
	.venv/bin/pip3 install -U setuptools pip
	.venv/bin/pip3 install -r requirements-dev.txt