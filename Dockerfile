FROM python:3-slim AS builder
ADD . /app
WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --target=/app -r requirements.txt

FROM gcr.io/distroless/python3-debian10
COPY --from=builder . /app
WORKDIR /app
ENV PYTHONPATH /app
CMD ["./main.py"]
