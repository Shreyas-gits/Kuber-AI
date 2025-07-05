# Running the MCP Client Locally

Follow the instructions below to set up and launch the MCP client on your local machine.

## 1. Navigate to the Project Root Directory

```bash
cd <path-to-project>/Kuber-AI
```

## 2. Activate the Python Virtual Environment

- **Linux/macOS:**
  ```bash
  source .venv/bin/activate
  ```
- **Windows:**
  ```cmd
  .venv\Scripts\activate
  ```

## 3. Configure Environment Variables

Create a `.env` file in the `/mcp_client` directory using the provided `.env.sample` as a template.

[Sample Environment File](./.env.sample)

## 4. Start the MCP client

```bash
python -m mcp_client.main
```

Once started, the MCP client will be available at: [http://127.0.0.1:8000/mcp](http://127.0.0.1:8000/mcp)
