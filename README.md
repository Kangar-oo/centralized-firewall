# 🔒 Centralized Firewall Management System

A robust, distributed firewall solution designed for enterprise environments that require centralized management of network security policies across multiple endpoints with real-time monitoring and blockchain-verified audit trails.

## 🏗️ Project Structure

```
centralized-firewall/
├── agent/               # Lightweight agent running on protected endpoints
│   ├── api/            # Secure REST API client for server communication
│   ├── config/         # Dynamic configuration management
│   ├── enforcer/       # High-performance rule enforcement engine
│   ├── monitor/        # Real-time network traffic analysis
│   └── rules/          # Rule parsing and management
├── server/             # Central management server
│   ├── blockchain/     # Immutable audit logging using blockchain
│   └── firewall/       # Core firewall logic and API endpoints
└── dashboard-vanilla/  # Responsive web interface for administration
```

## ✨ Key Features

### 🔄 Centralized Management
- Single-pane-of-glass interface for firewall administration
- Role-based access control (RBAC) for team collaboration
- Audit trail of all configuration changes

### 🛡️ Advanced Security
- End-to-end encrypted communications (TLS 1.3)
- Certificate-based mutual authentication
- Rate limiting and brute force protection

### 📊 Real-time Monitoring
- Live traffic visualization
- Anomaly detection
- Custom alerting system

### ⛓️ Blockchain Integration
- Immutable audit logs
- Tamper-evident record keeping
- Timestamp verification

## 🚀 Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| Go | 1.21+ | Agent and server components |
| Python | 3.8+ | Server-side processing |
| Node.js | 16+ | Dashboard frontend |
| PostgreSQL | 12+ | Data persistence |
| Redis | 6.0+ | Caching and pub/sub |

## 🛠️ Installation Guide

### 🖥️ Agent Deployment

1. **Prerequisites**
   ```bash
   # Install required system packages
   sudo apt-get update && sudo apt-get install -y libpcap-dev
   ```

2. **Configuration**
   Create `.env` file with necessary settings:
   ```env
   # Connection
   SERVER_URL=https://your-firewall-server.com
   AGENT_ID=agent-$(hostname)
   AGENT_SECRET=your-strong-password-here
   
   # Network
   NETWORK_INTERFACE=eth0
   LOG_LEVEL=info
   
   # Security
   TLS_VERIFY=true
   HEARTBEAT_INTERVAL=30s
   ```

3. **Build and Run**
   ```bash
   # Build the agent
   go build -ldflags="-s -w" -o agent
   
   # Run as a service (systemd example)
   sudo cp agent.service /etc/systemd/system/
   sudo systemctl enable --now agent
   ```

### 🌐 Server Setup

1. **Database Setup**
   ```bash
   # Create database and user
   sudo -u postgres createdb firewall
   sudo -u postgres createuser firewall_user
   psql -U postgres -c "ALTER USER firewall_user WITH PASSWORD 'secure_password';"
   ```

2. **Environment Configuration**
   ```env
   # Database
   DATABASE_URL=postgresql://firewall_user:secure_password@localhost/firewall
   
   # Server
   PORT=5000
   SECRET_KEY=your-secret-key-here
   
   # Redis
   REDIS_URL=redis://localhost:6379/0
   ```

3. **Start Services**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Run database migrations
   alembic upgrade head
   
   # Start the server
   uvicorn app:app --host 0.0.0.0 --port 5000
   ```

## 📊 Dashboard Access

Access the web interface at `https://your-firewall-server.com:3000`

Default credentials:
- Username: `admin`
- Password: `changeme` (change on first login)

## 🔄 API Documentation

Explore the API documentation at `https://your-firewall-server.com:5000/docs`

## 🧪 Testing

```bash
# Run unit tests
go test ./... -v

# Run integration tests
pytest tests/

# Check code coverage
go test -coverprofile=coverage.out ./...
```

## 🐳 Docker Deployment

```bash
# Build containers
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

## 🤝 Contributing

1. Read our [Code of Conduct](CODE_OF_CONDUCT.md)
2. Fork the repository
3. Create your feature branch (`git checkout -b feature/amazing-feature`)
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

