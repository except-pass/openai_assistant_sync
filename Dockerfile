FROM python:3.11-slim

WORKDIR /usr/src/app

#requirements depends on git
RUN apt-get update \
 && apt-get install -y --no-install-recommends git \
 && apt-get purge -y --auto-remove \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
#install the requirements first because these change less frequently than the code
RUN pip install -r requirements.txt

COPY sync.py sync.py
ENTRYPOINT [ "python", "sync.py" ]
