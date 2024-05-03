#!/bin/bash

docker image build --platform=linux/amd64 -t ivangudak096/afb-x64:latest --build-arg AGENT=agents .
docker image build --platform=linux/arm64 -t ivangudak096/afb-arm:latest --build-arg AGENT=agents .

docker push ivangudak096/afb-x64:latest
docker push ivangudak096/afb-arm:latest
