### to Start the docker container

Linux
```
docker-compose up -d 
```


MacOS
```
docker compose up -d 
```

### To force Rebuild the image

Linux
```
docker-compose up -d --build
```


MacOS
```
docker compose up -d --build

```

### To Stop  the containers

Linux
```
docker-compose down
```


MacOS
```
docker compose down
```


## to view docker logs

Linux
```
docker-compose logs -f
```


MacOS
```
docker compose logs -f
```


### to View Celery logs

```
cat /app/logs/celery_main.log
```


# Other commands that Might be helpful

### Check all running docker processes
```
docker ps -a
```

### delete a docker container
```
docker rm <container id>
```

### delete a docker image
```
docker rmi <imagename/image id>
```
### inspecting docker container `Don't try this without knowledge`
```
docker exec -it image_name bash
or 
docker exec -it image_name sh

#depending on the base image
```

### To check docker system space
```
docker system df
```

### To delete docker build cache
```
docker builder prune
```

### Space consumptin in VM per folder
```
cd <folder_name>
du -h | sort -h
```

### Space consumptin in VM overal

```
df -h
```

### Kill a processing running at port 
```
sudo lsof -n -i :<PORT NUMBER> | grep LISTEN
sudo kill <PID>
```




