```
                                           _  __
                                          | |/ /
                                          |   /
                                         /   |
   _____       __         _     __      /_/|_|  _____                 _
  / ___/__  __/ /_  _____(_)___/ /_  __ | |/ / / ___/___  ______   __(_)_______
  \__ \/ / / / __ \/ ___/ / __  / / / / |   /  \__ \/ _ \/ ___/ | / / / ___/ _ \
 ___/ / /_/ / /_/ (__  ) / /_/ / /_/ / /   |  ___/ /  __/ /   | |/ / / /__/  __/
/____/\__,_/_.___/____/_/\__,_/\__, / /_/|_| /____/\___/_/    |___/_/\___/\___/
                              /____/  | |/ /
                                      |   /
                                     /   |
                                    /_/|_|


```

This is the repository for the back end of the Subsidy Service for Gemeente Amsterdam. This README assumes that all commands are run from the root directory of this repository.
NOTE: most links will show `/api/v1` but pay attention if you are deploying targeting `/api/v1` or `/api/v2`!

## Installation

To run the subsidy service you must:

1. Create a bunq.conf file
2. Build and run the dockers
3. Add a user for making requests

The subsidy service is built to run on docker. It uses two containers: one for running the service backend, and one for the mongoDB. Building and starting these is as simple as:

```bash
docker-compose up -d --build
```

### 1. bunq.conf

To create a bunq.conf file you need an API key. This can be obtained from the Bunq app (for a real account) or from Bunq directly for a developer key to their Sandbox environment. The bunq.conf file is loaded by the Bunq API client to access account information. To generate it, a script is provided at `scripts/generate_bunq_conf.py`. This script assumes that the python Bunq SDK is installed. If you want to do this in a virtual environment, you can first run 

```bash
make venv
```

This will create a virtualenv and a symlink to the activation script. You can activate your venv with

```bash
source activate
```

You may have to install required packages e.g.:

```bash
pip install bunq_sdk --upgrade
pip install click
```

If your API key is for the Bunq sandbox, you can generate your file using

```bash
python3 scripts/generate_bunq_conf.py --sandbox --output_path config/bunq.conf "YOUR_API_KEY"
```

If your key is for the production environment (real money), just remove the `--sandbox` flag. For multiple bunq confs, save them to different files. Don't forget to indicate which bunq conf you are using in the `[bunq]` section of `config/subsidy_service.ini` (and other places as needed).


### 2. Dockers

The subsidy service runs on a docker with port 8080 exposed, and will attempt to communicate with a mongoDB at the host and port indicated in the `[mongo]` section of `config/subsidy_service.ini`. To build and run the subsidy service container, and link it to a vanilla mongoDB container, you can use the convenience commands

```bash
make docker-build docker-run
```

You might have to install `docker-compose` separately (see [here](https://docs.docker.com/compose/install/)). Some installer versions on OSX have been reported not to create the standard symlinks - you may fix this with:
```bash
PATH=$PATH:/Applications/Docker.app/Contents/Resources/bin/; export PATH
```

Also, do not forget to create the referenced environment file:
```bash
touch .env
```
where you can set the environment variables for the images, also referenced in the `docker_run.sh`. For example, set the Mongo user and password to `root` if you want to match the Mongo default configuration appearing in the `docker-compose.sh`.

and to start the Docker daemon of course.

Now you will have the subsidy service API running on `localhost:8080`, and the mongoDB will be accessible at `localhost:27017`. if you have already build images, then `make docker-run` is enough to get everything up and running from the previous build.

### 3. User

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

The swagger documentation is also hosted by the service. If you have the service running, you can see the documentation at https://localhost:8080/v1/ui/. 

## Testing

Bunq offers the possibility to test on full functionality by exposing a sandbox environment, see [here](https://doc.bunq.com/). When working against this endpoint no activity from and towards real world bank accounts is supported, but one can work with virtual internal accounts.
See a sandbox like a virtual user account where anything can be done, but just virtual money. For a random profile, multiple accounts can be created, payments made etc. 

To close the circle, app-level interaction via an emulator is also possible, follow the setup instructions [here](https://doc.bunq.com/#/android-emulator). 

The API interaction environment of Bunq itself, Tinker, is the interface to this "fake" bank backend where you can create multiple IBANs and top up money for a virtual user; install it with:

```bash
bash <(curl -s https://tinker.bunq.com/python/setup.sh)
```

In order to come into the same virtual world, do not forget to copy over the `bunq.conf` we create into Tinker, respecting the name just to be sure (`tinker/bunq-sandbox.conf`).

When configuring the application on the sandbox backend, a master account you are adding is always empty. For example, create a master account with the IBAN from `tinker/user_overview.py`; to top it up, use `tinker/make_request.py` to the very known sugardaddy@bunq.com (maximum amount 500).

If you follow the guide above, you can login as the virtual user from Tinker in the Bunq app on the emulator. You may just login directly, the login code, also displayed in Tinker, should be `000000`. Once you are in, a test account with ten cents on it is displayed.

All in all it is just easier to test the deployment with real, controlled accounts, transfering small amounts. The flow is as follows:

1. Open a real account with Bunq, possibly a business one
2. Create an API key for it; this can be done from the mobile app itself, from Profile -> Security -> Developer (check out the docs)
3. With this key, create a `bunq.conf` (see above)
4. `POST` a new master account; `name` and `description` are free, but make sure to fill in the `iban` of the account itself
5. `POST` a few citizens, in particular:
  1. An existing and active Bunq account
  2. An existing one, but inactive (ie pending identity validation)
  3. A non-existing account
6. `POST` a subsidy; at the moment of writing, the API just needs a master account, a target citizen and an amount (timings not impl.)
7. For 4.1 wait for the person to accept the Bunq connect; the other two cases are covered by the cron scripts which take care of fetching the state from Bunq - is the connect sent now (4.2) or retrying the creation (4.3)
8. Go further with more complex testing flows

NB. The application is not instance-safe nor multi-tenant, this means that an API key and Bunq account may be used in at most one and only one deployment. For example, if you have tested and you want to go to production on the same account, first `DELETE` everything locally and stop the instance, then move to the prod. env.

Important: whenever you create a file containing sensitive information (Bunq API keys, citizen or account JSON payloads...) make sure to add them to `.gitignore` - the project repo is public!

### Example flow (sandbox)

From zero to subsidy for the impatient on the sandbox setup. Perform the following steps:

* fetch a new sandbox key
* create a new `bunq.conf` from the key, and copy it over to `tinker/bunq-sandbox.conf`
* start the dockers, and create a user for the REST simple auth
* create a master account on the main sandbox IBAN from `tinker/user_overview.py`
* top up something on the account
* download a second tinker (citizen)
* use the account of this second tinker to create a citizen
* login in the sandbox app as this new citizen
* perform a subsidy request; state will be `PENDING_ACCEPT`
* in the app, you should see a connect invite under the events tab
* accept the connect; if you check the subsidy, state will be `OPEN`

To play the game again:
* `-X DELETE` everything
* delete the citizen tinker configuration and fetch a fresh a new user with `tinker/user_overview.sh`
* login with this fresh citizen on the mobile (code is `000000`)
* ask Sugar Daddy some more money
* proceed making masters, citizens and connects
* see the subsidy status transitioning from pending to open

### When creating a new endpoint

It is important to leverage code generation in Swagger but also to understand that blindly copypasting can cause troubles. A suggested flow:

* copy `swagger.yaml`
* paste it into the [https://editor.swagger.io](Swagger editor)
* add the new verb and related models - stick to the same structure and convention
* click to generate server code for `python-flask` and download it, but not in the project folder
* copy from the editor back into `swagger.yaml` 
* replace `./python-flask-server/swagger_server/swagger/swagger.yaml` with its downloaded version (this is not the same as `swagger.yaml`!)
* from the download, copy any new models into `./python-flask-server/swagger_server/models`, just the changes
* the same for the controllers, e.g. paste just the new controller function into the existing `./python-flask-server/swagger_server/controllers/subsidies_controller.py`; fill in the controller to call the expected service in `./subsidy_service/subsidy_service`
* add new unit tests or suites into `./python-flask-server/swagger_server/test`
* create new functionality in the service

There could be of course little variation on this, if you feel confident enough you may just copy all at once, point is that you should always `git diff` to make sure that nothing could break (this does not replace local testing of course, before acceptance when possible).

### Migrating from the first iteration

Anything before the commits `v2`, `second_iteration` and the like is referred to as *first iteration*. Before firing up the v2 UI on a v1 Mongo the following `curl` iterations must take place:
* create a first initiative; this will be the default initiative: `curl -v -u admin:admin -H "Content-Type: application/json" -d @scripts/rest/data/maas-initiative.json -X POST http://localhost:8080/api/v2/initiatives`
* create others; they will not be default (optional): `curl -v -u admin:admin -H "Content-Type: application/json" -d @scripts/rest/data/leraren-initiative.json -X POST http://localhost:8080/api/v2/initiatives`
* grant any existing user admin access from the Python shell (fetch all users with `.read_all()`):
  1. `import subsidy_service as service`
  2. `service.users.get('admin')`
  3. `{'username': 'admin', 'password': '$bcrypt-sha256$2b,12$SCkv2VzI4Pt2tmcpXK/OtO$Jocia5lH7AIwjh6knoVbvse.HTelsbm', 'id': '5c3f3be5b4fd67002205ec7f'}`
  4. `service.users.update('5c3f3be5b4fd67002205ec7f', {"username": "admin", "is_admin": True})`
  5. `{'username': 'admin', 'is_admin': True}`
  6. if already logged in the UI, logout and login again to see the admin panel

### Manually modifying the database

Important: as always, datastores should never be accessed directly. One case where this may be needed is if users are added manually via `create_subsidies_mongo.py` or others but some properties e.g. `bunq_id` were forgotten and the system status becomes inconsistent.

1. Connect to the instance, e.g. `mongo localhost:27017/admin -u root -p root`
2. `use subsidieservice`
3. `db.subsidies.find()`
4. property to fill in or modify: `subsidy[account][bunq_id]`
5. `db.subsidies.update({'_id' : ObjectId("5c631a4c7e6c4d00103db8d8")}, {'$set' : {'account': {'bunq_id': 'XXX'}}})` where...
6. ... `XXX` is the Bunq ID for the connect account: you can get them with `tinker`:
  - using the production configuration ie `config/bunq.conf`
  - using `create_production_configuration.py --api-key [api-key]`
  
