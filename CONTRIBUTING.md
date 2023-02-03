# CONTRIBUTING

## How to run the docker file locally


````
docker run -dp 5005:5000 -w /app -v "$(pwd):/app" rest-apis-flask-python sh -c "flask run"
```