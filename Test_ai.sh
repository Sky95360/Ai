#!/bin/bash
echo "Testing AI Commands..."

# Start auto responder
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "start auto responder"}'

sleep 2

# Check status
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "auto responder status"}'

sleep 2

# Show help
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "help"}'
