# Redis Setup Documentation for Gmail Webhook Rate Limiting

## Table of Contents
1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Usage](#usage)
4. [Project Structure](#project-structure)
5. [Commands Reference](#commands-reference)
6. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites
- Windows 10 or later
- WSL2 (Windows Subsystem for Linux)
- Ubuntu on WSL
- Python 3.x
- FastAPI project

### Step 1: Install WSL and Ubuntu
```bash
# Open PowerShell as Administrator and run:
wsl --install

# After restart, open Ubuntu and set up user:
# Create username and password when prompted
```

### Step 2: Install Redis on Ubuntu
```bash
# Update package list
sudo apt update

# Install Redis
sudo apt install redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf
# Find and change: supervised no -> supervised systemd
# Save and exit: Ctrl + X, then Y, then Enter
```

### Step 3: Install Redis Python Package
```bash
# In your Python project's virtual environment
pip install redis
```

## Configuration

### Redis Service Configuration
Create the following directory structure in your project:
```
app/
└── services/
    └── redis/
        ├── __init__.py
        └── redis_service.py
```

### Redis Connection Settings
Default settings in redis_service.py:
```python
host='localhost'
port=6379
db=0
decode_responses=True
```

## Usage

### Starting Redis Server
```bash
# Start Redis server
sudo service redis-server start

# Verify Redis is running
redis-cli ping
# Should return: PONG

# Check Redis status
sudo service redis-server status
```

### Stopping Redis Server
```bash
sudo service redis-server stop
```

### Basic Redis Commands
```bash
# Access Redis CLI
redis-cli

# Test connection
ping

# Exit Redis CLI
exit
```

## Project Structure

```
app/
├── services/
│   └── redis/
│       ├── __init__.py
│       └── redis_service.py
├── routers/
│   └── gmail_router.py
└── main.py
```

### Key Files and Their Purpose

1. `redis_service.py`: Redis service implementation
   - Rate limiting functionality
   - Message processing tracking
   - Connection management

2. `gmail_router.py`: Gmail webhook implementation
   - Uses Redis for rate limiting
   - Handles message deduplication
   - Processes Gmail notifications

## Commands Reference

### WSL Commands
```bash
# Check WSL version
wsl --version
wsl --status

# List installed distributions
wsl --list --verbose
```

### Redis Server Commands
```bash
# Start Redis
sudo service redis-server start

# Stop Redis
sudo service redis-server stop

# Restart Redis
sudo service redis-server restart

# Check status
sudo service redis-server status
```

### Redis CLI Commands
```bash
# Access Redis CLI
redis-cli

# Common Redis commands
SET key value
GET key
DEL key
EXISTS key
KEYS *
FLUSHALL  # Clear all data (use with caution)
```

## Troubleshooting

### Common Issues and Solutions

1. Redis Connection Failed
```bash
# Check if Redis is running
sudo service redis-server status

# Restart Redis
sudo service redis-server restart

# Check Redis logs
sudo tail -f /var/log/redis/redis-server.log
```

2. WSL Issues
```bash
# Restart WSL
wsl --shutdown
# Then reopen Ubuntu terminal

# Update WSL
wsl --update
```

3. Permission Issues
```bash
# If Redis commands fail with permission error
sudo chmod 777 /var/run/redis/redis-server.pid
sudo chown redis:redis /var/run/redis/redis-server.pid
```

### Health Checks

1. Check Redis Connection
```python
# In your Python code
from redis import Redis
redis_client = Redis(host='localhost', port=6379, db=0)
redis_client.ping()  # Should return True
```

2. Monitor Redis Memory Usage
```bash
# In redis-cli
INFO memory
```

Remember to start Redis before starting your FastAPI application to ensure proper functionality of the rate limiting and message deduplication features.

## Notes

- Redis data persists across server restarts but not across Redis server restarts
- Rate limiting window is set to 5 seconds by default
- Message processing history expires after 24 hours
- Always ensure Redis is running before starting your application