# Subsidy Service

This is the repository for the back end of the Subsidy Service for Gemeente Amsterdam. This guide assumes that all commands are run from the root directory of this repository.

## Installation

To run the subsidy service you must:

1. Create a bunq.conf file
2. Build and run the dockers
3. Add a user for making requests

The subsidy service is build to run on docker. It uses two dockers: one for running the service backend, and one for the mongoDB. To build and start these 

### 1. bunq.conf

To create a bunq.conf file you need an API key. This can be obtained from the Bunq app (for a real account) or from Bunq directly for a developer key. The bunq.conf file is loaded by the Bunq API client to access account information. To generate it, a script is provided at `scripts/generate_bunq_conf.py`. This script assumes that the python Bunq SDK is installed. If you want to do this in a virtual environment, you can first run 

```bash
make venv
```

This will create a virtualenv and a symlink to the activation script. You can activate your venv with

```bash
source activate
```

If your API key is a sandbox key, you can generate your file using

```bash
python scripts/generate_bunq_conf.py --sandbox --output_path config/bunq.conf [YOUR_API_KEY]
```

If your key is for the production environment, just remove the `--sandbox` flag. For multiple bunq confs, save them to different files. Don't forget to indicate which bunq conf you are using in the `[bunq]` section of `config/subsidy_service.ini`.


### Dockers

The subsidy service runs on a docker with pore 8080 exposed, and will attempt to communicate with a mongoDB at the host and port indicated in the `[mongo]` section of `config/subsidy_service.ini`. To build and run the subsidy service container, and link it to a vanilla mongoDB container, you can use the convenience command

```bash
make docker-run
```

Now you will have the subsidy service API running on `localhost:8080`, and the mongoDB will be accessible at `localhost:27017`.

### User

To actually make API calls, you need a user in the database. This can also be done on the command line in a python3 interpreter, this time from inside the docker. (If your mongodb is available at `localhost:27017`, this can also be done from your local machine with the virtualenv activated).

You can start a python3 interpreter inside the service docker using 

```bash
docker exec -it subsidy_service_dev python3
```

Then you can use the following commands to add your user to the database:

```python
>>> import subsidy_service as service
>>> service.users.add("YOUR_USERNAME", "YOUR_PASSWORD")
{'username': 'YOUR_USERNAME', 'id': 'YOUR_DB_ID'}
```

You can check that your user was successfully added by running

```python
>>> service.users.authenticate("YOUR_USERNAME", "YOUR_PASSWORD")
True
```

You are now ready to make API calls over HTTPS, authenticated with basicauth using your username and password.

## Documentation

### Swagger

To view the interactive Swagger documentation, open the [Swagger Editor](https://editor.swagger.io/) and select `File > Import File > swagger.yaml`, or just copy/paste the contents of `swagger.yaml` into the editor. You will see the generated documentation on the right side of the screen. To generate the flask server skeleton, select `Generate Server > python-flask` in the editor. This will download all required files in a zip. For details of the yaml specification syntax, please see the documentation [here](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md). **Note that we are using Swagger v2.0**. 
