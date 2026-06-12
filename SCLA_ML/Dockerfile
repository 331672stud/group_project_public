FROM ollama/ollama:latest

COPY ./model/SCLA_ML_model.gguf /models/SCLA_ML_model.gguf
COPY ./Modelfile /Modelfile

COPY ./entrypoint.sh /entrypoint.sh

# normalize line endings and make entrypoint executable
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

# ensure required packages available (curl, bash)
RUN apt-get update && apt-get install -y --no-install-recommends curl bash

ENTRYPOINT ["/entrypoint.sh"]
