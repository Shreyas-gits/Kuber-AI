# KuberAI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-326ce5.svg?logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![AI Powered](https://img.shields.io/badge/AI-Powered-brightgreen.svg)](https://github.com/shreyas/project_KuberAi)

## Overview

KuberAI is an intelligent Kubernetes management platform that integrates generative AI with Kubernetes clusters to provide automated monitoring, issue identification, and debugging capabilities. This project empowers users to efficiently manage their Kubernetes infrastructure through AI-driven insights and recommendations.

## Features

- 🤖 **AI-Powered Monitoring**: Continuous cluster health monitoring with intelligent analysis
- 🔍 **Issue Detection**: Automated identification of cluster problems and anomalies
- 🛠️ **Smart Debugging**: AI-assisted troubleshooting with actionable recommendations
- 📊 **Real-time Analytics**: Comprehensive cluster metrics and performance insights
- 🚨 **Intelligent Alerting**: Context-aware notifications and alerts
- 💡 **Optimization Suggestions**: AI-driven recommendations for resource optimization

## High-Level Design

![KuberAI High-Level Design](./docs/attachments/Kuber%20AI%20HLD.png)

## Getting Started

### Prerequisites

- Kubernetes cluster (v1.20+)
- kubectl configured
- Python (v3.8+)
- Docker

#### Development Prerequisites

- Git
- curl (for uv installation)
- A terminal with bash/zsh support

### Installation

```bash
# Clone the repository
git git clone https://github.com/Shreyas-gits/Kuber-AI.git
cd Kuber-AI

# Install dependencies
npm install  # or pip install -r requirements.txt

# Configure cluster connection
kubectl config current-context
```

### Development Setup

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
# Or use the shortcut script
./activate_env.sh

# Run pre-commit on all files
uv run pre-commit run --all-files

# Run specific workspace components
uv run --directory mcp_server python -m src.main
uv run --directory mcp_client python -m src.main

# Add new dependencies
uv add package-name
uv add --dev dev-package-name
```

### Quick Start

```bash
# Deploy KuberAI to your cluster
kubectl apply -f deployment/

# Access the dashboard
kubectl port-forward svc/kuberai-dashboard 8080:80

# Open http://localhost:8080 in your browser
```

## Usage

1. **Connect your cluster**: Configure KuberAI to monitor your Kubernetes cluster
2. **View dashboard**: Access real-time cluster insights and AI recommendations
3. **Receive alerts**: Get notified about potential issues before they impact your workloads
4. **Apply suggestions**: Implement AI-recommended optimizations and fixes

## Architecture

KuberAI consists of several key components:

- **AI Engine**: Core machine learning models for analysis and recommendations
- **Cluster Monitor**: Kubernetes API integration for real-time data collection
- **Dashboard**: Web-based interface for visualization and management
- **Alert Manager**: Intelligent notification and alerting system

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

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