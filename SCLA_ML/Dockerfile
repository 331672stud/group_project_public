FROM ollama/ollama:latest

COPY ./model/SCLA_ML_model.gguf /models/SCLA_ML_model.gguf
COPY ./Modelfile /Modelfile

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN apt-get update 

RUN apt install -y python3 python3-pip

# RUN apt-get update && apt-get install -y \
#     python \
#     python-pip

RUN if [ -f app/requirements.txt ]; then pip install --no-cache-dir -r app/requirements.txt; fi

EXPOSE 11434

ENTRYPOINT ["/entrypoint.sh"]
