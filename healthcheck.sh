#!/bin/sh
curl -X GET "http://localhost:81/api/system/health?apikey=\"$API_KEY\"" -H "accept: application/json"