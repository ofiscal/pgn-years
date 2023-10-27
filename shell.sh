# Start a docker container based on the latest image.
docker run --name pgn -itd       \
  -v /home/jeff/of/pgn-years:/mnt \
  ofiscal/tax.co:latest

docker start pgn

docker exec -it pgn bash

docker stop pgn && docker rm pgn

# because `pytest` does not find local modules by default
PYTHONPATH=.:$PYTHONPATH pytest python/*.py
