FROM ghcr.io/home-assistant/home-assistant:2026.2.2

COPY requirements.txt /build/requirements.txt

RUN pip install --no-cache-dir -r /build/requirements.txt