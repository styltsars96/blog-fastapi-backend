# Dockerfile
FROM python:3.10
WORKDIR /blog-backend
COPY . /blog-backend
RUN pip install -r requirements.txt
EXPOSE 8000
ENTRYPOINT ["./scripts/docker-entrypoint.sh"]
