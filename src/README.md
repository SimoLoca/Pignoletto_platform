# Run Lizmap stack with docker-compose

## Before, how to set the IP:
- In order to set the IP for Lizmap, go to [this line of code](https://github.com/dros1986/pignoletto-project/blob/edad9d742617244def08ae00a6d6003f699f6d0f/DOCKER/Makefile#L17)
- In order to set the IP for Pignoletto platform, go to [this line of code](https://github.com/dros1986/pignoletto-project/blob/edad9d742617244def08ae00a6d6003f699f6d0f/DOCKER/nginx/nginx.conf#L4) and [this line of code](https://github.com/dros1986/pignoletto-project/blob/edad9d742617244def08ae00a6d6003f699f6d0f/DOCKER/pignoletto/pignoletto_app#L3)
  - Also, if you want to change the Pignoletto platform port, go to [this line of code](https://github.com/dros1986/pignoletto-project/blob/edad9d742617244def08ae00a6d6003f699f6d0f/DOCKER/docker-compose.yml#L42) and set to `<your_port>:5000`

## How to run the docker stack
* Create environment variables:

```
make env
```

* Create and run the containers:
```
docker-compose up [-d]
```



Open your browser at `http://<YOUR_LIZMAP_IP>:9090` for Lizmap management (default is: *http://149.132.178.176:9090*).

Open your browser at `http://<YOUR_PIGNOLETTO_IP>:<YOUR_PORT>` for Pignoletto's platform (default is: *http://149.132.178.176:5000/pignoletto/login*).
