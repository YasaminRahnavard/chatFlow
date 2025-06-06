# 🚀 ChatFlow - Docker-Based Chat Platform

A comprehensive Docker-powered chat application demonstrating modern cloud computing concepts, microservices architecture, and AI integration. Perfect for learning Docker, container orchestration, and full-stack development.

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Database Setup](#-database-setup)
- [Environment Variables](#-environment-variables)
- [Docker Services](#-docker-services)
- [API Documentation](#-api-documentation)
- [Guest User Support](#-guest-user-support)
- [Development](#-development)
- [Deployment](#-deployment)
- [Monitoring](#-monitoring)
- [Troubleshooting](#-troubleshooting)
- [Use Cases & Applications](#-use-cases--applications)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🐳 **Docker & Cloud Computing**
- **Multi-container architecture** with Docker Compose
- **Custom Docker networks** for secure inter-service communication
- **Persistent volumes** for data storage
- **Health checks** for all services
- **Resource limits** and reservations
- **Container orchestration** best practices

### 💬 **Smart Chat Application**
- **Real-time messaging** with AI integration
- **Chat titles** - generated from first message content
- **Guest user support** (no registration required)
- **Chat history persistence** for both guests and authenticated users
- **Session-based storage** for guest users
- **Conversation management** with multiple chats
- **Modern responsive UI** built with React + Chakra UI

### 🧠 **Intelligent User Experience**
- **No more "New Chat" clutter** - meaningful conversation names
- **Persistent titles** across sessions

### 🤖 **AI Integration**
- **Google Gemini API** integration via FastAPI service
- **Configurable AI parameters** (temperature, max tokens)
- **Conversation context** awareness
- **Error handling** and fallback responses
- **API usage tracking** and analytics

### 🏗️ **Technical Stack**
- **Frontend**: React 18 + Vite + Chakra UI
- **Backend**: Django REST Framework
- **AI Service**: FastAPI with async support
- **Database**: PostgreSQL 15 with optimized settings
- **Cache**: Redis 7 for session storage and caching
- **Web Server**: Nginx for production deployment
- **Monitoring**: Built-in health checks (Prometheus-ready)

## 🏛️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   AI Service    │
│ (React+Chakra)  │◄──►│   (Django)      │◄──►│   (FastAPI)     │
│   Port: 3005    │    │   Port: 8003    │    │   Port: 8002    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 │                               │
         ┌───────▼─────────┐             ┌─────▼─────┐
         │   PostgreSQL    │             │   Redis   │
         │   Database      │             │   Cache   │
         │   Port: 5432    │             │Port: 6379 │
         └─────────────────┘             └───────────┘
```

### 🔌 Network Architecture

- **frontend-tier**: React app and public-facing services
- **backend-tier**: API services and business logic
- **database-tier**: Database services (internal only)

## 📋 Prerequisites

- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Git** for cloning the repository
- **Google Gemini API Key** (optional, works with demo responses without it)
- **8GB RAM** recommended for optimal performance

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/chatflow.git
cd chatflow
```

### 2. Environment Setup

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Application Settings
DEBUG=False
SECRET_KEY=your-super-secret-key-here
APP_NAME=ChatFlow

# Database Configuration
POSTGRES_DB=chatflow_db
POSTGRES_USER=chatflow_user
POSTGRES_PASSWORD=secure_password_123
DATABASE_URL=postgresql://chatflow_user:secure_password_123@chatflow-postgres:5432/chatflow_db

# Redis Configuration
REDIS_URL=redis://chatflow-redis:6379/0

# API Configuration
ALLOWED_HOSTS=localhost,127.0.0.1,chatflow-frontend

# AI Service (Optional - works without it)
GEMINI_API_KEY=your-google-gemini-api-key
```

### 3. Build and Start Services

```bash
# Build and start all services
docker-compose up --build -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Access the Application

- **Frontend**: http://localhost:3005
- **Backend API**: http://localhost:8003
- **AI Service**: http://localhost:8002

## 🗄️ Database Setup

### Initial Database Setup

The database is automatically initialized when you first start the services, but here are the manual commands if needed:

```bash
# 1. Start database service only (optional)
docker-compose up postgres-db redis-cache -d

# 2. Wait for database to be ready
docker-compose logs postgres-db

# 3. Run database migrations
docker-compose exec api-server python manage.py migrate

# 4. Create database tables (if needed)
docker-compose exec api-server python manage.py makemigrations
docker-compose exec api-server python manage.py migrate

# 5. Create a superuser (optional, for admin access)
docker-compose exec api-server python manage.py createsuperuser

# 6. Verify database connection
docker-compose exec api-server python manage.py check --database default
```

### Database Management Commands

```bash
# View database status
docker-compose exec postgres-db pg_isready -U chatuser

# Access PostgreSQL shell
docker-compose exec postgres-db psql -U chatuser -d chatdb

# Backup database
docker-compose exec postgres-db pg_dump -U chatuser chatdb > backup.sql

# Restore database
docker-compose exec -T postgres-db psql -U chatuser chatdb < backup.sql

# Reset database (⚠️ Destroys all data)
docker-compose down -v
docker volume rm docker-chat-platform_postgres-data
docker-compose up --build -d
```

### Redis Cache Management

```bash
# Access Redis CLI
docker-compose exec redis-cache redis-cli

# View Redis info
docker-compose exec redis-cache redis-cli info

# Clear cache (optional)
docker-compose exec redis-cache redis-cli flushall

# Monitor Redis activity
docker-compose exec redis-cache redis-cli monitor
```

## 🔧 Environment Variables

### Required Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | - |
| `POSTGRES_PASSWORD` | Database password | - |
| `DATABASE_URL` | Database connection string | - |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Debug mode | `False` |
| `GEMINI_API_KEY` | Google Gemini API key | - |
| `ALLOWED_HOSTS` | Django allowed hosts | `localhost,127.0.0.1` |
| `REDIS_URL` | Redis connection string | `redis://chatflow-redis:6379/0` |

## 🐳 Docker Services

### Frontend Service (`chatflow-frontend`)
- **Image**: Custom React build with Nginx
- **Port**: 3005:3000
- **Features**: Chakra UI, Smart Chat Titles, Responsive Design
- **Health Check**: HTTP endpoint monitoring
- **Dependencies**: Backend and AI services

### Backend Service (`chatflow-backend`)
- **Image**: Custom Django application
- **Port**: 8003:8000
- **Health Check**: Django health endpoint
- **Dependencies**: PostgreSQL and Redis

### AI Service (`chatflow-ai`)
- **Image**: Custom FastAPI application
- **Port**: 8002:8001
- **Health Check**: FastAPI health endpoint
- **Dependencies**: Redis cache

### Database Service (`chatflow-postgres`)
- **Image**: PostgreSQL 15 Alpine
- **Volume**: Persistent data storage
- **Health Check**: PostgreSQL ready check
- **Network**: Database-tier only

### Cache Service (`chatflow-redis`)
- **Image**: Redis 7 Alpine
- **Volume**: Persistent cache storage
- **Health Check**: Redis ping
- **Network**: Backend and database tiers

## 📚 API Documentation

### Backend API (Django REST Framework)

#### Endpoints

- `GET /api/conversations/` - List conversations
- `POST /api/conversations/` - Create conversation
- `GET /api/conversations/{id}/messages/` - Get conversation messages
- `POST /api/conversations/chat/` - Send message and get AI response
- `GET /api/usage/stats/` - Get usage statistics
- `GET /health/` - Health check

#### Example: Send Message with Smart Title

```bash
curl -X POST http://localhost:8003/api/conversations/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I deploy Docker containers?",
    "conversation_id": "optional-uuid",
    "temperature": 0.7,
    "max_tokens": 1000
  }'

# Response includes auto-generated title:
# {
#   "conversation_id": "uuid",
#   "conversation_title": "How do I deploy Docker containers?",
#   "assistant_message": {...}
# }
```

### AI Service API (FastAPI)

#### Endpoints

- `POST /chat` - Process chat message
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

## 👤 Guest User Support

ChatFlow supports guest users who can use the system without registration:

### Features for Guest Users
- **Session-based identification** using browser sessions
- **Chat history persistence** during the session
- **Full AI interaction** capabilities
- **Smart chat titles** automatically generated
- **No data collection** beyond session scope

### How It Works
1. Guest users are identified by session IDs
2. Conversations are linked to session IDs instead of user accounts
3. Chat history and titles are preserved as long as the session is active
4. No personal information is required or stored

### Session Management
```javascript
// Frontend automatically handles session creation
// Backend uses Django sessions for guest identification
// Redis stores session data for fast access
// Smart titles generated from first message content
```

## 💻 Development

### Local Development Setup

1. **Clone and enter the project**:
```bash
git clone https://github.com/yourusername/chatflow.git
cd chatflow
```

2. **Start development services**:
```bash
# Start database and cache only
docker-compose up postgres-db redis-cache -d

# Initialize database
docker-compose exec postgres-db pg_isready -U chatuser

# Run backend locally
cd backend
python manage.py migrate
python manage.py runserver 8003

# Run frontend locally (new terminal)
cd frontend
npm install
npm run dev
```

3. **Database development commands**:
```bash
# Apply migrations
docker-compose exec api-server python manage.py migrate

# Create new migrations
docker-compose exec api-server python manage.py makemigrations

# Access Django shell
docker-compose exec api-server python manage.py shell

# Create test data
docker-compose exec api-server python manage.py loaddata fixtures/test_data.json
```

### Adding New Features

1. **Frontend (React + Chakra UI)**:
   - Components in `frontend/src/`
   - Chakra UI theming in `frontend/src/main.jsx`
   - API integration in main components

2. **Backend (Django)**:
   - Models in `backend/chat/models.py`
   - Views in `backend/chat/views.py`
   - URLs in `backend/chat/urls.py`

3. **AI Service (FastAPI)**:
   - Main logic in `ai-service/main.py`
   - Add new AI providers or models

### Running Tests

```bash
# Backend tests
docker-compose exec api-server python manage.py test

# Frontend tests
docker-compose exec web-ui npm test

# Database tests
docker-compose exec api-server python manage.py test --database default

# API integration tests
curl -f http://localhost:8003/health/
curl -f http://localhost:8002/health
```

## 🚀 Deployment

### Production Deployment

1. **Update environment variables**:
```env
DEBUG=False
SECRET_KEY=your-production-secret-key
POSTGRES_PASSWORD=secure-production-password
```

2. **Deploy with Docker Compose**:
```bash
docker-compose -f docker-compose.yml up -d
```

3. **Database initialization in production**:
```bash
# Run migrations
docker-compose exec api-server python manage.py migrate

# Collect static files (if needed)
docker-compose exec api-server python manage.py collectstatic --noinput

# Create superuser
docker-compose exec api-server python manage.py createsuperuser
```

4. **SSL/HTTPS Setup** (recommended):
   - Use a reverse proxy like Nginx or Traefik
   - Configure SSL certificates
   - Update ALLOWED_HOSTS

### Cloud Deployment Options

- **AWS**: ECS, EKS, or EC2 with Docker
- **Google Cloud**: Cloud Run, GKE, or Compute Engine
- **Azure**: Container Instances or AKS
- **DigitalOcean**: App Platform or Droplets

## 📊 Monitoring

### Built-in Health Checks

All services include health checks:

```bash
# Check all service health
docker-compose ps

# Individual service health
curl http://localhost:3005/health    # Frontend
curl http://localhost:8003/health/   # Backend
curl http://localhost:8002/health    # AI Service
```

### Database Monitoring

```bash
# PostgreSQL status
docker-compose exec postgres-db pg_isready -U chatuser

# Redis status
docker-compose exec redis-cache redis-cli ping

# View database connections
docker-compose exec postgres-db psql -U chatuser -d chatdb -c "SELECT * FROM pg_stat_activity;"
```

### Optional Prometheus Monitoring

Uncomment the monitoring service in `docker-compose.yml`:

```yaml
monitoring:
  image: prom/prometheus:latest
  container_name: chatflow-monitoring
  ports:
    - "9090:9090"
  # ... configuration
```

### Logs and Debugging

```bash
# View all logs
docker-compose logs -f

# Service-specific logs
docker-compose logs -f chatflow-frontend
docker-compose logs -f chatflow-backend
docker-compose logs -f chatflow-ai

# Database logs
docker-compose logs chatflow-postgres
```

## 🔧 Troubleshooting

### Common Issues

#### 1. **Services Not Starting**
```bash
# Check Docker and Docker Compose versions
docker --version
docker-compose --version

# Rebuild containers
docker-compose down -v
docker-compose up --build
```

#### 2. **Database Connection Issues**
```bash
# Check database health
docker-compose exec chatflow-postgres pg_isready -U chatflow_user

# View database logs
docker-compose logs postgres-db

# Reset database
docker-compose down -v
docker volume rm chatflow_postgres-data
docker-compose up --build
```

#### 3. **Smart Chat Titles Not Working**
```bash
# Check frontend logs
docker-compose logs chatflow-frontend

# Verify API response
curl -X POST http://localhost:8003/api/chat/conversations/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message"}'

# Rebuild frontend
docker-compose up --build web-ui
```

#### 4. **AI Service Errors**
```bash
# Check AI service logs
docker-compose logs chatflow-ai

# Verify environment variables
docker-compose exec chatflow-ai env | grep GEMINI
```

#### 5. **Frontend Not Loading**
```bash
# Check frontend build
docker-compose logs chatflow-frontend

# Rebuild frontend
docker-compose up --build chatflow-frontend
```

### Performance Optimization

1. **Resource Allocation**:
   - Adjust CPU and memory limits in `docker-compose.yml`
   - Monitor resource usage with `docker stats`

2. **Database Optimization**:
   - Tune PostgreSQL settings for your workload
   - Consider connection pooling for high traffic

3. **Caching**:
   - Redis is used for session storage and caching
   - Configure Redis memory policies as needed

### Getting Help

- **Check Logs**: Always start with `docker-compose logs -f`
- **Health Checks**: Use the built-in health endpoints
- **Database Status**: Verify PostgreSQL and Redis connectivity
- **Issues**: Create an issue on GitHub with logs and environment details

## 🎯 Use Cases & Applications

This ChatFlow platform serves as an excellent foundation for various applications and learning scenarios:

### 🎓 **Educational & Learning**
- **Cloud Computing Course Projects**: Demonstrates microservices, Docker, and container orchestration
- **Full-Stack Development Training**: Complete frontend-backend-AI integration example
- **DevOps Learning**: Container deployment, health monitoring, and service orchestration
- **API Integration Studies**: Real-world example of AI service integration
- **Database Management**: PostgreSQL setup, migrations, and data persistence
- **Security Best Practices**: Network isolation, environment variables, and CORS

### 💬 **Personal & Professional Chatbots**
- **Personal AI Assistant**: Using Gemini API for daily tasks and questions
- **Customer Support Base**: Extend for automated customer service
- **Educational Tutor**: Subject-specific AI tutoring system
- **Content Creation Assistant**: Writing, brainstorming, and creative projects
- **Code Review Helper**: Technical assistance and programming guidance
- **Language Learning**: Conversation practice with AI

### 🏢 **Enterprise Applications**
- **Internal Knowledge Base**: Company-specific Q&A system
- **Employee Onboarding**: Interactive training and support system
- **Document Processing**: AI-powered document analysis and summarization
- **Meeting Assistant**: Note-taking and follow-up suggestions
- **Project Management**: Task planning and milestone tracking
- **HR Assistant**: Policy questions and employee support

### 🔬 **Research & Development**
- **AI Model Testing**: Framework for testing different AI models and APIs
- **Conversation Analysis**: Chat data collection and analysis
- **User Experience Research**: UI/UX testing platform
- **Performance Benchmarking**: Service scalability and load testing
- **Security Testing**: Container security and API vulnerability assessment

### 🌐 **Community & Social**
- **Study Groups**: Collaborative learning platform
- **Interest-Based Communities**: Topic-specific discussion platforms
- **Support Groups**: Peer support with AI moderation
- **Gaming Communities**: In-game assistance and strategy discussions
- **Content Creator Tools**: Audience engagement and content planning

### 🛠️ **Developer Tools & Extensions**
- **API Gateway**: Extend to route multiple AI services
- **Webhook Integration**: Connect with external services (Slack, Discord, etc.)
- **Voice Integration**: Add speech-to-text and text-to-speech
- **Mobile App Backend**: REST API ready for mobile app development
- **Analytics Platform**: Add usage tracking and conversation analytics
- **Multi-tenant SaaS**: Scale to support multiple organizations

### 📊 **Data & Analytics**
- **Conversation Analytics**: User behavior and interaction patterns
- **AI Performance Monitoring**: Response quality and accuracy tracking
- **Usage Statistics**: Service utilization and resource optimization
- **A/B Testing Platform**: UI/UX and feature testing
- **Business Intelligence**: Integration with BI tools and dashboards

### 🚀 **Deployment Scenarios**
- **Local Development**: Personal learning and experimentation
- **Cloud Deployment**: AWS, GCP, Azure container services
- **On-Premise**: Corporate internal deployment
- **Edge Computing**: IoT and local processing applications
- **Hybrid Cloud**: Multi-cloud and hybrid deployment strategies

### 🔧 **Technical Extensions**
- **Microservices Learning**: Add more services (notification, file upload, etc.)
- **Load Balancing**: Multiple backend instances with load balancer
- **Message Queues**: Asynchronous processing with RabbitMQ/Kafka
- **Search Integration**: ElasticSearch for conversation search
- **File Upload**: Document processing and analysis features
- **Real-time Features**: WebSocket integration for live updates

### 💡 **Innovation Opportunities**
- **Multi-AI Integration**: Compare responses from different AI models
- **Specialized AI Agents**: Domain-specific AI assistants (medical, legal, technical)
- **Workflow Automation**: Integration with automation tools
- **Content Generation**: Automated content creation and optimization
- **Smart Recommendations**: Personalized suggestions based on chat history


### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Standards

- **Frontend**: ESLint + Prettier for React/JavaScript with Chakra UI
- **Backend**: PEP 8 for Python/Django
- **AI Service**: PEP 8 for Python/FastAPI
- **Docker**: Best practices for Dockerfile and compose files

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


**Built with ❤️ for learning Docker and cloud computing concepts** 