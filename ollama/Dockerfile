FROM ollama/ollama

ENV APP_HOME=/home

WORKDIR $APP_HOME

COPY . .

RUN apt-get update && \
    apt-get install -y dos2unix && \
    rm -rf /var/lib/apt/lists/*

RUN chmod +x pull-llama3.sh && dos2unix pull-llama3.sh

ENTRYPOINT ["/usr/bin/bash", "pull-llama3.sh"]