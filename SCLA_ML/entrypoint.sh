#!/bin/bash

set -e

MODEL_NAME="SCLA_ML_vuln_scanner"
MODELFILE_PATH="/Modelfile"
export OLLAMA_HOST="0.0.0.0"

echo "launching ollama"
ollama serve &
OLLAMA_PID=$!
echo "ollama running"

until curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; do
    echo "sleeping"
    sleep 1
done

if ! ollama list | grep -q "${MODEL_NAME}"; then
    ollama create "${MODEL_NAME}" -f "${MODELFILE_PATH}"
    echo "model created"
else
    echo "Model '${MODEL_NAME}' already registered, skipping."
fi

kill ${OLLAMA_PID}
wait ${OLLAMA_PID} 2>/dev/null || true

exec ollama serve
