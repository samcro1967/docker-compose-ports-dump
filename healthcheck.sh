#!/bin/sh
curl -X GET "http://localhost:$API_PORT/api/system/health?apikey=\"$API_KEY\"" -H "accept: application/json"