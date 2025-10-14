FROM --platform=linux/amd64 python:3.10-slim-bookworm as builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir --platform manylinux_2_17_x86_64 --only-binary=:all: -r requirements.txt

FROM --platform=linux/amd64 python:3.10-slim-bookworm

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY . .

CMD ["python", "-u", "job_bot.py"]