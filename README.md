# Tugas 3 Kelompok 5 Big Data

## API
### Cara Penggunaan
1. Run this for the first time:
```
docker-compose up --build
```
or
```
docker-compose up -d --build
docker-compose logs -f api
```
for detached mode

2. For the second time just run
```
docker-compose up
```
or
```
docker-compose up -d
docker-compose logs -f api
```
for detached mode

3. API should be accessable in an ngrok link, and the guide to how to use the API will be available when accessing the index page

### Additional Notes
Don't forget to fill in your own **NGROK AUTH TOKEN** in the .env, refer to .env example
