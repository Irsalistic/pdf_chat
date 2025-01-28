#!/bin/bash

ollama serve &
pid=$!

sleep 5

echo "Pulling llama3 model"
ollama pull llama3.1:8b 
# ollama pull llama3:70b-instruct

wait $pid
