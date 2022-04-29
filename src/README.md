# Run Lizmap stack with docker-compose

## Before, how to set the IP:
In order to set the IP for Pignoletto Platform, go to [this line of code](./Makefile#L17) and set your desired IP with the port on which the service is deployed.

## How to run the docker stack
* Create environment variables:

```
make env
```

* Create and run the containers:
```
docker-compose up [-d]
```



Open your browser at `http://<YOUR_IP>:<YOUR_PORT>` for Lizmap Map management (default is: *http://127.0.0.1:8080*).

Open your browser at `http://<YOUR_IP>:<YOUR_PORT>/pignoletto/login` for Pignoletto's platform (default is: *http://127.0.0.1:8080/pignoletto/login*).
