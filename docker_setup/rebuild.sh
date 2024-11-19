#!/bin/bash
# variables
echo "COMPOSE_PROJECT_NAME=uniquebible" > .env
echo "UID="$UID >> .env
echo "USER="$USER >> .env
echo "DATA_DIR="$HOME"/UniqueBible" >> .env
# stop first
docker compose down --remove-orphans
# build
docker compose build --no-cache