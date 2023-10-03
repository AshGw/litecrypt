#!/bin/bash

check_command() {
  if ! command -v "$1" &> /dev/null; then
    echo "false"
  else
    echo "true"
  fi
}

if [ "$(check_command docker)" = "false" ]; then
  echo "Docker is not installed. Please install Docker."
  exit 1
fi

if [ "$(check_command docker-compose)" = "false" ]; then
  echo "Docker Compose is not installed. Please install Docker Compose."
  exit 1
fi

echo "Docker and Docker Compose are installed. Continuing..."

if [ "$(check_command python)" = "false" ]; then
  echo "Python is not installed. Please install Python to run the 'gen_compose.py' script."
  exit 1
fi

if ! python -c "import requests" &> /dev/null; then
  echo "The 'requests' library is not installed. Please install it using 'pip install requests' to run the 'gen_compose.py' script."
  exit 1
fi

python -m gen_compose

echo "Created 'docker-compose.yml' in the current directory"
echo "Running docker-compose.yml.."

docker-compose up
