# KuberAI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-326ce5.svg?logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![AI Powered](https://img.shields.io/badge/AI-Powered-brightgreen.svg)](https://github.com/shreyas/project_KuberAi)

## Overview

KuberAI is an intelligent Kubernetes management platform that integrates generative AI with Kubernetes clusters to provide automated monitoring, issue identification, and debugging capabilities. This project empowers users to efficiently manage their Kubernetes infrastructure through AI-driven insights and recommendations.

## Features

- 🤖 **AI-Powered Monitoring**: Continuous cluster health monitoring with intelligent analysis
- 🛠️ **Smart Debugging**: AI-assisted troubleshooting with actionable recommendations
- 📊 **Real-time Analytics**: Comprehensive cluster metrics and performance insights
- 💡 **Optimization Suggestions**: AI-driven recommendations for resource optimization

## Architecture

- [High Level Design](./docs/architecture/High%20Level%20Design.md)

## Getting Started

### Installation Development Setup

```bash
# Clone the repository
git git clone https://github.com/Shreyas-gits/Kuber-AI.git
cd Kuber-AI
```

For development, we use `uv` for Python package management and virtual environments. The repository includes an automated setup script:

```bash
# Run the development setup script
./dev_setup.bash
```

The script will:
- ✅ Install `uv` if not already installed
- 🐍 Create and configure a Python virtual environment
- 📦 Install all dependencies from `uv.lock`
- 🔧 Set up pre-commit hooks for code quality
- 🛠️ Configure development tools (black, isort, flake8, mypy, bandit)

#### Manual Setup (Alternative)

If you prefer manual setup:

```bash
# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
uv sync --dev

# Install pre-commit hooks
uv run pre-commit install
```

#### Working with the Development Environment

```bash
# Activate virtual environment
source .venv/bin/activate

# Run pre-commit on all files
uv run pre-commit run --all-files

# Add new dependencies
uv add package-name

# Remove dependency
uv remove package-name

# Install or sync packages added to pyproject.toml
uv sync
```

### Quick Start

This application enables interaction with Kubernetes clusters using natural language.

**Prerequisites:**

- An active Kubernetes cluster.

For local development, you can set up a single-node cluster using MicroK8s.  
Refer to the [MicroK8s Setup Guide](./microk8s_setup/microk8s%20setup.md) for detailed instructions.

For instructions on running the MCP Server locally, see:  
[Running the MCP Server](./mcp_server/README.md)

For instructions on running the MCP Client locally, see:  
[Running the MCP Client](./mcp_client/README.md)

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](./docs/CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: support@kuberai.dev
- 💬 Discord: [Join our community](https://discord.gg/kuberai)
- 📚 Documentation: [docs.kuberai.dev](https://docs.kuberai.dev)
- 🐛 Issues: [GitHub Issues](https://github.com/shreyas/project_KuberAi/issues)

## Roadmap

- [ ] Multi-cloud support
- [ ] Advanced ML model integration
- [ ] Custom alert policies
- [ ] API for third-party integrations
- [ ] Enhanced security scanning

---

Made with ❤️ by the KuberAI team