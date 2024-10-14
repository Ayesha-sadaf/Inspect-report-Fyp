# Stage 1: Build the application
FROM python:3.11-alpine AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache --virtual .build-deps gcc g++ musl-dev python3-dev

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Create the runtime image
FROM python:3.11-alpine

WORKDIR /app

# Copy only necessary files from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app .

# Copy the rest of your application code
COPY . .
EXPOSE 8002
CMD ["python3", "apis/main.py"]
