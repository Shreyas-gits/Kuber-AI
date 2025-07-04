"""Main entry point for the mcp_client package."""

# import requests


# def execute_tool_on_server(tool_name, payload, host="127.0.0.1", port=8080):
#     url = f"http://{host}:{port}/tools/{tool_name}/execute"
#     response = requests.post(url, json=payload)
#     response.raise_for_status()
#     return response.json()


# if __name__ == "__main__":
#     tool_name = "kubernetes_read_tool_wrapper"  # Replace with actual tool name
#     payload = {}  # No parameters required
#     try:
#         result = execute_tool_on_server(tool_name, payload)
#         print(f"Tool '{tool_name}' executed successfully. Result:")
#         print(result)
#     except Exception as e:
#         print(f"Failed to execute tool '{tool_name}': {e}")
#         print(f"Tool '{tool_name}' executed successfully. Result:")
