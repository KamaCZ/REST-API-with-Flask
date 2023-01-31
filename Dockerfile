FROM python:3.11
# port we gonna run the flask app on
EXPOSE 5000
# going to the folder within our docker image, where we can 
# put our flask app,py, copying app.py into the image
WORKDIR /app
# copying the requirements.txt file into current folder
# which is /app fodler in docker image
COPY requirements.txt .
# isntalling all the packages in requirements.txt file
RUN pip install -r requirements.txt
# Copying all from the project folder into the app folder in 
# docker image
COPY . . 
# running the flask app
# "--host", "0.0.0.0" - this will enable the client to make
# requests to the app that is running in a container
CMD ["python", "-m", "flask", "run", "--host", "0.0.0.0"]

