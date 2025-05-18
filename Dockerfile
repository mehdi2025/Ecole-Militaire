FROM python:3.11-slim
# Creating Working Directory inside docker container 
WORKDIR /app
#Copy all the files in working directory
COPY . /app
# install all the requirements
RUN apt-get update && pip install --no-cache-dir -r requirements.txt
CMD ["sh","-c","python manage.py runserver 0.0.0.0:8000"]
