# DevOps Microservices Project

A 3-microservice application demonstrating a complete DevOps pipeline: version
control, CI, Docker containerization, and CD — built for the BSc.IT DevOps
course (KES Shroff College).

## Architecture

```
                POST /orders {user_id, product_id}
                        |
                        v
                +----------------+
                |  order-service | :5003
                +----------------+
                    |         |
        GET /users/<id>   GET /products/<id>
                    |         |
                    v         v
          +--------------+ +-----------------+
          | user-service | | product-service |
          |    :5001     | |      :5002      |
          +--------------+ +-----------------+
```

- **user-service** — owns user data, exposes `GET /users`, `GET /users/<id>`
- **product-service** — owns product data, exposes `GET /products`, `GET /products/<id>`
- **order-service** — exposes `POST /orders`; when an order is placed it calls
  user-service and product-service over HTTP to validate the user and product
  before confirming the order. This is the inter-service communication piece.

All three are independent Flask apps, each with its own `Dockerfile`,
`requirements.txt`, and `pytest` test suite, so each can be built, tested and
deployed on its own — the core idea of microservices.

## Running locally with Docker

```bash
docker compose up --build
```

Then try it:

```bash
curl http://localhost:5001/users
curl http://localhost:5002/products
curl -X POST http://localhost:5003/orders \
     -H "Content-Type: application/json" \
     -d "{\"user_id\": 1, \"product_id\": 101}"
curl http://localhost:5003/orders
```

The order-service call demonstrates real service-to-service communication:
Docker Compose's internal DNS resolves `user-service` and `product-service`
to the right containers, so order-service never needs a hardcoded IP.

## Running tests directly

```bash
cd user-service && pip install -r requirements.txt && pytest
cd product-service && pip install -r requirements.txt && pytest
cd order-service && pip install -r requirements.txt && pytest
```

order-service's tests mock the HTTP calls to the other two services, so they
run without Docker or the other services being up.

## CI/CD Pipeline

**Jenkins (`Jenkinsfile`)** — declarative pipeline:
1. Checkout — pulls the repo
2. Test (x3) — installs deps and runs pytest for each service independently
3. Build Docker Images — builds a versioned image per service, tagged with
   the Jenkins `BUILD_NUMBER` (artifact versioning)
4. Deploy — tears down and redeploys the stack with `docker compose`

To use it: create a Jenkins Pipeline job pointing at this repo, make sure
Docker and Python/pip are available to the Jenkins agent, and update the
`git` URL in the Checkout stage to your own repo.

**GitHub Actions (`.github/workflows/ci-cd.yml`)** — same idea as a second
CI option: a matrix job tests all 3 services in parallel, then a build job
builds the 3 Docker images once tests pass.

## How this maps to the syllabus

| Unit | Covered by |
|---|---|
| I — DevOps lifecycle, version control | Git repo, Plan→Code→Build→Test→Deploy flow |
| II — CI, pipeline design, artifact management | Jenkinsfile / GitHub Actions: automated build + test per service, versioned Docker images tagged by build number |
| III — CD, deployment, environment management | Deploy stage (`docker compose up -d --build`); `USER_SERVICE_URL`/`PRODUCT_SERVICE_URL` env vars show how config changes between dev/staging/prod without code changes |
| IV — Containerization | One Dockerfile per service, multi-container app via docker-compose, service discovery over a Docker bridge network |
| V — Monitoring/logging (extension) | Each service exposes a `/health` endpoint — a natural hook for Prometheus/monitoring, matching your Prometheus-Grafana practical |

## Possible extensions

- Add a `/metrics` endpoint (Prometheus client) to each service, reusing your
  Prometheus/Grafana practical.
- Convert `docker-compose.yml` into Kubernetes `Deployment` + `Service`
  manifests (you already have a working example in your Kubernetes practical)
  to demonstrate Unit IV orchestration concepts.
- Push built images to Docker Hub in the Jenkins pipeline using a
  `docker login` + `docker push` stage with stored credentials.
