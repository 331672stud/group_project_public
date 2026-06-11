FROM ollama/ollama:latest

COPY ./model/SCLA_ML_model.gguf /models/SCLA_ML_model.gguf
COPY ./Modelfile /Modelfile

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN apt-get update && apt-get install -y --no-install-recommends curl

ENTRYPOINT ["./entrypoint.sh"]
