docker build -t gcr.io/`gcloud config get-value project`/canada-prison-initiative:latest -f Dockerfile . && \
    docker push gcr.io/`gcloud config get-value project`/canada-prison-initiative:latest
