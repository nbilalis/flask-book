# Build your Python image | Docker Documentation - https://docs.docker.com/language/python/build-images/
# Get started with Docker Compose | Docker Documentation - https://docs.docker.com/compose/gettingstarted/

# syntax=docker/dockerfile:1

# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.9-slim-buster

EXPOSE 5000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.docker.txt ./requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

ENV SECRET_KEY=DrObbpjywUW0Pnq7zy6oxyPKH9VRqafM
ENV SQLALCHEMY_ECHO=False

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
# CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

# Remove any existing container with same name (--force: if it's running, kill it)
# docker rm flask-book-container --force

# Remove any existing image with same name
# docker image rm flask-book

# Build an image from current directry (.) and name it as `fast-book`
# docker build -t flask-book .

# Run the 'fast-apbooki' image in a container. Map 5000 port to 8080.
# docker run -d --name flask-book-container -p 8080:5000 flask-book
