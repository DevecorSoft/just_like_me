```shell
docker volume create hindsight_pgdata

docker run -d \
  --name hindsight-postgres \
  --restart unless-stopped \
  -p 15432:5432 \
  -e POSTGRES_DB=hindsight \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -v hindsight_pgdata:/var/lib/postgresql/data \
  pgvector/pgvector:pg16

python3 -m pip install hindsight-api

export HINDSIGHT_API_LLM_PROVIDER=none
export HINDSIGHT_API_DATABASE_URL=postgresql://postgres:mysecretpassword@localhost:15432/hindsight
export HF_HUB_OFFLINE=1
hindsight-api

npx @vectorize-io/hindsight-control-plane --api-url http://localhost:8888
```
