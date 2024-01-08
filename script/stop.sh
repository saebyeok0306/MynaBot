#!/bin/bash

if docker ps -a -q --filter "name=${{ secrets.DOCKER_CONTAINER_NAME }}" | grep -q .; then
  if docker ps -q --filter "name=${{ secrets.DOCKER_CONTAINER_NAME }}" | grep -q .; then
    echo "INFO: Bot Container is stopping..."
    docker stop ${{ secrets.DOCKER_CONTAINER_NAME }} || true
    echo "INFO: Bot Container is removing... True"
    docker rm ${{ secrets.DOCKER_CONTAINER_NAME }} || true
  else
    echo "INFO: Bot Container is removing... True"
    docker rm ${{ secrets.DOCKER_CONTAINER_NAME }} || true
  fi
else
  echo "ERROR: Bot Container is not exists... False"
fi