FROM python:3.13-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ffmpeg \
        libimage-exiftool-perl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock README.md ./
COPY m_c ./m_c

RUN pip install --no-cache-dir .

ENTRYPOINT ["metadata-cleaner"]
CMD ["--help"]
