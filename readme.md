To start the cluster, open powershell in the folder you saved the .yml file and run `docker-compose up -d`

You can open http://localhost:8080 in your browser to view the health of the nodes

You can also run `docker exec -it downtown-library ./cockroach sql --insecure` in powershell to use SQL 
