FROM ghcr.io/home-assistant/home-assistant:stable

COPY requirements.txt /build/requirements.txt

RUN pip install --no-cache-dir -r /build/requirements.txt