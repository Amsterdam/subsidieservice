.PHONY: clean venv test docker-stop docker-run docker-data

activate=venv/subsidy/bin/activate

## Make virtual environment and install requirements (requires virtualenv)
venv: 
	-rm -rf venv
	-unlink activate
	mkdir venv
	virtualenv venv/subsidy
	ln -s venv/subsidy/bin/activate activate
	(\
		source $(activate); \
		pip3 install -r requirements.txt; \
		pip3 install -e python-flask-server -e subsidy_service; \
		deactivate; \
	)


## Update requirements in requirements.txt
requirements: 
	source $(activate) && pip3 freeze --exclude-editable > requirements.txt
	# echo "-e subsidy_service\n-e python-flask-server" >> requirements.txt


## Rebuild the docker including new requirements
docker-build: docker-stop test
	# docker build -f docker/Dockerfile -t subsidies/server .
	docker-compose build


## Run the Service API linked to Mongo docker
docker-run: # docker-stop docker-build
	# docker run -d --rm -p 27017:27017 -v $(shell pwd)/data/mongodb:/data/db \
	# 	--name "subsidy_mongo_dev" mongo
	# docker run -d --rm -p 8080:8080 -v $(shell pwd)/config:/etc/subsidy_service/config \
	# 	-v $(shell pwd)/logs:/etc/subsidy_service/logs --hostname subsidy_service_dev  \
	# 	--link subsidy_mongo_dev:mongo --name "subsidy_service_dev" subsidy/service
	docker-compose up -d
	docker ps


## Open an interactive shell in the service docker. Current directory is mounted to /opt/
docker-shell: docker-run
	docker exec -it subsidy_service_dev /bin/bash


## Kill the docker containers and remove the service containers
docker-stop:
	docker-compose down
	-docker rm subsidy_mongo_dev
	-docker rm subsidy_service_dev
	

## Copy the data/*.csv files into subsidy_service_dev:/usr/src/data
docker-data:
	-docker exec subsidy_service_dev mkdir /usr/src/data
	for file in data/*.csv; do \
		docker cp $$file subsidy_service_dev:/usr/src/data; \
		echo "Copied:" $$file; \
	done


## Update the existing models and code, BUT NOT CONTROLLERS, to new swagger spec.
## Shows the diff between the old and new controllers. Any inserts are interesting!
swagger-update: swagger.yaml
	swagger-codegen validate -i swagger.yaml
	-rm -r temp-swagger-server-dir
	mkdir temp-swagger-server-dir
	swagger-codegen generate -i swagger.yaml -l python-flask -o temp-swagger-server-dir
	rsync -Iavh temp-swagger-server-dir/ python-flask-server/ --exclude="controller*" \
		--exclude="*__pycache__*" --exclude=".DS_Store" --exclude="*__main__.py"
	source $(activate) && pip install -e python-flask-server
	git diff --no-index python-flask-server/swagger_server/controllers \
		temp-swagger-server-dir/swagger_server/controllers


## Run the subsisdy_service unit tests 
test:
	(\
		source $(activate); \
		pytest -lv --tb=long --cov=subsidy_service/subsidy_service \
			--cov-report=term --cov-report=html subsidy_service; \
	)


## Run the unit tests and open the coverage report
coverage: htmlcov/index.html
	open htmlcov/index.html

htmlcov: test


## Delete all compiled Python files and remove docker containers
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	-rm -r temp-swagger-server-dir
	-docker rm subsidy_mongo_dev
	-docker rm subsidy_service_dev


## Mirror this repository to the Gemeente Amsterdam GitHub repo
mirror: test
	cd ../service-mirror && git fetch -p && git push;


## Create the mirror repository for mirroring
mirror-init:
	-rm -rf ../service-mirror
	git clone --mirror \
		https://git.kpmg.nl/KPMG-NL-AABD/ClientProjects/GemeenteAmsterdam/SubsidyService.git \
		../service-mirror
	(\
		cd ../service-mirror; \
		git remote set-url --push origin git@github.com:Amsterdam/subsidieservice.git; \
	)


#################################################################################
# Self Documenting Commands                                                     #
# from https://github.com/drivendata/cookiecutter-data-science/                 #
#################################################################################

.DEFAULT_GOAL := show-help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: show-help
show-help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
