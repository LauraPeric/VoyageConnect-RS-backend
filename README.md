# 🚀 VoyageConnect – Distributed Microservices System

VoyageConnect is a distributed backend system for a travel-based social networking platform that enables users to create destinations, share posts, comment, and participate in forum discussions.

This project was developed as part of a university course in Distributed Systems at the Faculty of Informatics, Juraj Dobrila University of Pula.

The system is built using a microservices architecture where services communicate over HTTP and are managed using NGINX as a reverse proxy.

---

## 🧠 Project Overview

- Microservices-based backend system
- REST API built with FastAPI
- JWT-based authentication
- MongoDB database with async operations
- Fully containerized using Docker and Docker Compose

Each microservice is responsible for a specific domain, ensuring scalability and separation of concerns.

---

## 🛠 Tech Stack

- **Backend:** FastAPI, Pydantic
- **Database:** MongoDB (Motor async driver)
- **Authentication:** JWT (python-jose, passlib/bcrypt)
- **Infrastructure:** Docker, Docker Compose
- **Proxy:** NGINX

---

## 🎯 Features

- User registration and login (JWT authentication)
- Create and browse destinations
- Create and manage posts
- Comment system with nested replies
- Forum discussions system

---

## 🧩 Microservices

| Service | Description |
|--------|-------------|
| auth-service | User authentication and JWT handling |
| destination-service | Manage travel destinations |
| post-service | Handle posts within destinations |
| comment-service | Comments and nested replies |
| forum-service | Forum topics and discussions |

---

## 🚀 Run the Project

### Start all services
```bash
cd voyageconnect_project
docker-compose up --build
```

### Run a single service

```bash
cd auth-service
docker build -t auth-service:1.0 .
docker run -p 8001:8000 auth-service:1.0
```

## 👨‍💻 Author

**Laura Perić**  
Full design and implementation of the application

