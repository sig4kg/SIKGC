# Virtuoso SPARQL Endpoint for test

Creates and runs a Virtuoso Open Source instance including a SPARQL endpoint preloaded with TREAT experiment data.

## Quickstart

Running the Virtuoso SPARQL Endpoint Quickstart requires Docker and Docker Compose installed on your system. If you do not have those installed, please follow the install instructions for [here](https://docs.docker.com/engine/install/) and [here](https://docs.docker.com/compose/install/). Once you have both Docker and Docker Compose installed, run

``` bash
git clone https://github.com/sylviawangfr/treatExtractor.git
cd treatExtractor
docker build -t virtuoso-loader .
docker-compose up
```

After a short delay your SPARQL endpoint will be running at [localhost:8890/sparql](localhost:8890/sparql). 
If you want to change port or data location, please change configurations in .env.

Please contact the Author for test data.

# UNC Manual html parser

Coming soon...
