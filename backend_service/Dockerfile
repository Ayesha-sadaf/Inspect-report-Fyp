FROM python:3.11-alpine AS builder

WORKDIR /app


RUN apk add --no-cache --virtual .build-deps gcc g++ musl-dev python3-dev


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.11-alpine

WORKDIR /app


COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app .


COPY . .
EXPOSE 8002
CMD ["python3", "apis/main.py"]
