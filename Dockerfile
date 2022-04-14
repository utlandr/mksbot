FROM docker.io/library/python:3.10-slim-bullseye

# install system dependencies
RUN	apt update && \
	apt install -y ffmpeg libnacl-dev libssl-dev python3-dev

# create mksbot user
RUN useradd -rm -d /home/mksbot -u 1001 -G sudo -s /bin/bash mksbot

# create root directory and install python packages
USER mksbot
WORKDIR /home/mksbot/
COPY --chown=mksbot requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY --chown=mksbot mksbot ./mksbot
WORKDIR mksbot/
ENTRYPOINT ["python3", "mksbot_main.py"]

