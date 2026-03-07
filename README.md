# aceest-fitness-and-gym

This repository contains a small Flask-based REST API for managing clients and generating simple workout programs. It includes unit tests (pytest), a multi-stage Dockerfile that runs tests during build, and CI/CD scaffolding including a `Jenkinsfile` and GitHub Actions workflow.

## Jenkins setup (brief)

This project includes a declarative `Jenkinsfile` at the repository root that:

- Builds the Docker `test` target (this runs `pytest` during the image build).
- Builds a runtime image and tags it.
- Pushes both the test and runtime images to GitHub Container Registry (GHCR).

Prerequisites on your Jenkins instance

1. A Jenkins agent (node) with Docker installed and permission to run Docker commands.
2. A Jenkins credential containing your GH username and a Personal Access Token (PAT) with the required scopes:
	- Token scopes: `write:packages` (for GHCR) and `repo` (if the registry access requires repo scope). Create the PAT on GitHub -> Settings -> Developer settings -> Personal access tokens.
3. Add the credential to Jenkins (Credentials > System > Add Credentials) as type "Username with password".
	- Set the credential ID to: `ghcr-creds` (the `Jenkinsfile` uses this ID). The username should be your GitHub username and the password should be the PAT.

How the pipeline uses the credential

- The pipeline logs into GHCR in the Push stage with:

```bash
echo $GHCR_TOKEN | docker login ghcr.io -u $GHCR_USER --password-stdin
```

where `GHCR_USER` and `GHCR_TOKEN` come from the Jenkins credential stored as `ghcr-creds`.

Configuring a Jenkins job

1. Create a new Pipeline or Multibranch Pipeline job pointing at this repository.
2. Ensure the job runs on an agent with Docker and sufficient disk/CPU/memory to build the image and run tests.
3. The default `Jenkinsfile` uses `ghcr.io/roshanjson/aceest-fitness-and-gym` as the image name; change `IMAGE_NAME` in the `Jenkinsfile` if you want to use a different registry or repository.

Local verification commands

You can locally test the same steps that Jenkins runs. From the repository root:

Build and run the tests inside the image (builds the `test` target which runs pytest during build):

```bash
docker build --target test -f dockerFile/Dockerfile -t aceest-test:latest .
```

Build the runtime image:

```bash
docker build -f dockerFile/Dockerfile -t aceest:latest .
```

Login to GHCR (replace <USER> with your GitHub username):

```bash
docker login ghcr.io -u <USER>
# Enter your PAT when prompted (or use --password-stdin with echo to pipe the token)
```

Push images (after login):

```bash
docker tag aceest:latest ghcr.io/<USER>/aceest-fitness-and-gym:latest
docker push ghcr.io/<USER>/aceest-fitness-and-gym:latest
```

Notes

- The `dockerFile/Dockerfile` is multi-stage with a `test` stage that runs `pytest` during build. A failing test will cause the build/test stage to fail just like Jenkins.
- The `Jenkinsfile` assumes the credential id `ghcr-creds`; change it if you prefer a different ID.
- Make sure to secure your PAT and rotate it per your org policy.

## API Endpoints

The Flask app exposes the following HTTP endpoints (all paths are rooted at the app base):

- GET /clients
	- Description: Return a JSON list of all clients.
	- Response: 200 with an array of client objects.

- GET /clients/<name>
	- Description: Return the client record matching <name>.
	- Response: 200 with client object if found, 404 if not found.

- POST /clients
	- Description: Create a new client. Expects a JSON body with at least the `name` field; `age` is optional.
	- Example body: `{ "name": "alice", "age": 30 }`
	- Response: 201 on success, 400 if `name` missing, 409 if a client with the same name already exists.

- POST /clients/<name>/generate_program
	- Description: Generate and assign a simple program for the named client.
	- Response: 200 with `{ "client": "<name>", "program": "<program>" }` if successful, 404 if client not found.

Notes about environment variables

- `DB_NAME` — optional: path to the SQLite DB file used by the app. Tests set this to temporary DBs; in production you can set it to a persistent path or a mounted volume.
- `PORT` — optional: port used by the Flask app; default is `5000`.
