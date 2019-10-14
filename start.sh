./aws-config.sh
docker-compose -f docker-compose.yml config
docker-compose build --no-cache
docker-compose up -d