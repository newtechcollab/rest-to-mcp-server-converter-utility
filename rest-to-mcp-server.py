import httpx
from fastmcp import FastMCP
import certifi
import os
import sys
import json
import yaml
import asyncio
import aiohttp
import requests
import logging
logging.basicConfig(level=logging.DEBUG)

class LogResponse(httpx.Response):
    async def aiter_bytes(self, *args, **kwargs):
        async for chunk in super().aiter_bytes(*args, **kwargs):
            print(chunk)
            yield chunk


class LogTransport(httpx.AsyncBaseTransport):
    def __init__(self, transport: httpx.AsyncBaseTransport):
        self.transport = transport

    async def handle_async_request(self, request: httpx.Request):
        response = await self.transport.handle_async_request(request)

        return LogResponse(
            status_code=response.status_code,
            headers=response.headers,
            stream=response.stream,
            extensions=response.extensions,
        )

transport = LogTransport(httpx.AsyncHTTPTransport())

async def log_request(request):
    logging.debug(f"Request headers: {request.headers}")

os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
os.environ["SSL_CERT_FILE"] = certifi.where()

# Load your OpenAPI spec 
#openapi_spec = httpx.get("https://registry.scalar.com/@scalar/apis/galaxy/latest?format=json").json()
#openapi_spec = httpx.get("https://raw.githubusercontent.com/swagger-api/swagger-petstore/refs/heads/master/src/main/resources/openapi.yaml").json()
#openapi_spec = httpx.get(sys.argv[1]).json()
openapi_spec_file = sys.argv[1]
if openapi_spec_file.startswith("http"):
    # The Spec file is located in a HTTP server
    print(f"The REST API Spec file is {openapi_spec_file}")
    response = httpx.get(openapi_spec_file)
    file_content = response.text
    print(f"File Content -> {file_content}")

    # Now, check whether the content is JSON or YAML
    try:
        openapi_spec = json.loads(file_content)
    except json.JSONDecodeError:
        print("This is NOT a JSON content, so, let's try to process this as YAML")
        data_dict = yaml.safe_load(file_content)
        openapi_spec = json.loads(json.dumps(data_dict))
else:
    # The Spec file is located on local machine
    print(f"The REST API Spec file is {openapi_spec_file}")
    if openapi_spec_file.endswith(".json"):
        print("The local REST API Spec file is a JSON file !!")
        try:
            with open(openapi_spec_file, "r") as f:
                openapi_spec = json.load(f)
        except FileNotFoundError:
            print(f"Error: {openapi_spec_file} not found. Please ensure the file exists.")
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {openapi_spec_file}. Check file format.")
    else:
        print("The local REST API Spec file is a YAML file !!")
        try:
            with open(openapi_spec_file, "r") as f:
                openapi_spec = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Error: {openapi_spec_file} not found in current directory !!")
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")

print(f"The JSON-formatted OpenAPI Spec is {openapi_spec}")

# Create an HTTP client for the REST API
#client = httpx.AsyncClient(base_url="https://github.com/scalar")
#client = httpx.AsyncClient(base_url="https://petstore3.swagger.io/api/v3")
servers = openapi_spec["servers"]
print(f"Server URL is {servers[0]['url']}")

# Get the HTTP Headers, in case passed as Input to this Program, to be passed on to target REST API
if len(sys.argv) > 3:
    print(sys.argv)
    headers_input = sys.argv[3]
    print(f"Header passed is {headers_input}")
    client = httpx.AsyncClient(base_url=servers[0]['url'], event_hooks={'request': [log_request]})
    #client = httpx.AsyncClient(base_url=servers[0]['url'])
    #client = httpx.AsyncClient(base_url=servers[0]['url'], headers=json.loads(headers_input))
    #client = httpx.AsyncClient(base_url=servers[0]['url'], headers=json.loads(headers_input), event_hooks={'request': [log_request]})
else:
    print("No Header passed")
    #client = httpx.AsyncClient(base_url=servers[0]['url'])
    client = httpx.AsyncClient(base_url=servers[0]['url'], transport=transport)

headers={'user-agent': 'gomez', 'Accept': 'application/json', 'x-api_key': 'G5qMQZioRNVqPR7VffudCzGFPWVkHK9E', 'ultasite': 'en-US'}    

#client = httpx.AsyncClient(base_url=servers[0]['url'], headers=headers, event_hooks={'request': [log_request]})
#client = httpx.AsyncClient(base_url=servers[0]['url'], headers=headers)
#response = await client.get("https://da1.ulta.com/v1/core/catalog/brands?country=US")
#print("Response")
#print(response)

mcp = FastMCP.from_openapi(
    openapi_spec=openapi_spec,
    client=client,
    name="Demo API Server"
)
#mcp.run(transport="streamable-http", port=3333)

if __name__ == "__main__":
    mcp_port = sys.argv[2]
    mcp.run(transport="streamable-http", port=int(mcp_port))
    #mcp.run(transport="sse", port=3333)
