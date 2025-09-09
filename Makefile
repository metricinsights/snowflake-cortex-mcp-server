CONTAINER = snowflake_mcp
rebuild:
	sudo docker stop ${CONTAINER}
	sudo docker-compose up --build -d
restart:
	sudo docker-compose restart
logs:
	sudo docker logs -f ${CONTAINER}