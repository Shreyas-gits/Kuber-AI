# Running MCP Client Locally

Follow these steps to run the MCP client on your local machine:

## 1. Go to the Project Root Folder

```bash
cd /<path-to-project>/project_KuberAi
```

## 2. Install Dependencies and Create Virtual Environment

Use [uv](https://github.com/astral-sh/uv) to install all dependencies (including optional ones) and create a `.venv`:

```bash
uv venv --all
```

This will create a `.venv` folder and install everything from `uv.lock`.

## 3. Activate the Python Virtual Environment

- On Linux/macOS:
  ```bash
  source .venv/bin/activate
  ```
- On Windows:
  ```cmd
  .venv\Scripts\activate
  ```

## 4. Run the MCP client

```bash

python -m mcp_client.main
```

The MCP client will start and be available at: [http://127.0.0.1:8080/](http://127.0.0.1:8080/mcp)
