#!/bin/sh
if [ $# -lt 2 ]
then 
    echo ""
    echo "Usage: sh rest-to-mcp-server.sh <<REST API OpenAPI-compliant JSON Specs>> <<MCP Server Port>> <<JSON String of HTTP Headers in Key:Value format e.g. header1:value1,header2:value2>>"
    echo ""
    exit 
fi
if [ $# -eq 3 ]
then
    json_data="$3"
    python3 rest-to-mcp-server.py $1 $2 "$json_data"
else
    python3 rest-to-mcp-server.py $1 $2
fi
