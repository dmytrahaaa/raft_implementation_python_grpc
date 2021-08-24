# Raft implementation (python/grpc)

How to up: docker-compose up --build

How to check: disconnect any node, then connect back
docker commands: docker network ls, docker network disconnect 'my_network' raft-1, docker network connect 'my_network' raft-1

How to test as a client: download https://appimage.github.io/BloomRPC/, add raft.proto to app, send vote or append message requests in appropriate format
