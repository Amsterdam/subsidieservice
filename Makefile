.PHONY: clean venv 

activate="venv/subsidy/bin/activate"

## Make virtual environment
venv: 
	virtualenv venv/subsidy -p python3.6

## Update requirements in requirements.txt
requirements: 
	source $(activate); pip freeze > requirements.txt

## Rebuild the docker including new requirements
docker-build: docker requirements.txt subsidy_service python-flask-server
	docker build -f docker/Dockerfile -t subsidies/server .
 
## Run the Service API linked to a new or existing mongo docker
docker-run: docker-build
	-docker run -d -p 27017:27017 --name "subsidy_mongo_dev" mongo 
	docker start subsidy_mongo_dev 
	docker run --rm -p 8080:8080 --link subsidy_mongo_dev:mongo --name subsidy_service_dev subsidies/server

## Open an interactive shell in the service docker. Current directory is mounted to /opt/
docker-shell: docker-build
	docker run -it -p 8080:8080 -v $(shell pwd):/opt/$(shell basename "$(shell pwd)") \
		--entrypoint /bin/sh -w "/opt" subsidies/server

## Update the existing models and code, BUT NOT CONTROLLERS, to new swagger spec.
## Shows the diff between the old and new controllers. Any inserts are interesting!
swagger-update: swagger.yaml
	-rm -r temp-swagger-server-dir
	mkdir temp-swagger-server-dir
	swagger-codegen generate -i swagger.yaml -l python-flask -o temp-swagger-server-dir
	rsync -av python-flask-server/ test/ --exclude="controller*"
	git diff --no-index python-flask-server/swagger_server/controllers temp-swagger-server-dir/swagger_server/controllers

## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	-rm -r temp-swagger-server-dir
	-docker kill subsidy_mongo_dev
	-docker rm subsidy_service_dev

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
