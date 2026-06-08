#!/bin/bash

set -e

MODEL_NAME="SCLA_ML_vuln_scanner"
MODELFILE_PATH="/Modelfile"
OLLAMA_HOST="0.0.0.0"


OLLAMA_HOST=${OLLAMA_HOST} ollama serve &
OLLAMA_PID=$!

until curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; do
    sleep 1
done

if ! ollama list | grep -q "${MODEL_NAME}"; then
    ollama create "${MODEL_NAME}" -f "${MODELFILE_PATH}"
else
    echo "Model '${MODEL_NAME}' already registered, skipping."
fi


wait ${OLLAMA_PID}
