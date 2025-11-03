To start the cluster, open powershell in the folder you saved the .yml file and run `docker-compose up -d`

You can open http://localhost:8080 in your browser to view the health of the nodes

The init.sql file sets up the tables in the nodes (for the demo, just the tables for the books.)
So in powershell (in the same folder as the init file) run `Get-Content init.sql | docker exec -i downtown-library ./cockroach sql --insecure` to initialize these tables. 

You can also run `docker exec -it downtown-library ./cockroach sql --insecure` in powershell to manually use SQL 
