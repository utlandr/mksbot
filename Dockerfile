from python:3.11-slim-bullseye

ARG USER=appuser
ARG GROUP=appuser

WORKDIR /app

# Add non-root user
RUN useradd -rms /bin/bash $USER && usermod -aG users $GROUP
RUN chown -R $USER:$GROUP /app

ENV PATH="/home/${USER}/.local/bin:${PATH}"

COPY --chown=$USER:$GROUP src src
COPY --chown=$USER:$GROUP pyproject.toml README.md .
RUN python3 -m pip install .

CMD ["start-mksbot"]
