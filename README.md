# 📚 Cloud Microservices Library (v3)

A cloud-native microservices application for managing a library system. Built with modular services for users, books, and borrowing, this system leverages Docker and Kubernetes for scalable deployment.

---

## 🧩 Microservices Overview

- **UserService** – Manages user registration and profile queries  
- **BookService** – Handles book catalog management  
- **BorrowService** – Processes book borrowing requests and history  

Services communicate asynchronously using **RabbitMQ** and are orchestrated via **Kubernetes**.

---

## ⚙️ Tech Stack

- **Backend:** Python (Flask)  
- **Containerization:** Docker, Docker Compose  
- **Orchestration:** Kubernetes (YAML configs)  
- **Messaging:** RabbitMQ  

---

## 🚀 Getting Started

### ▶️ Local Setup with Docker Compose

```bash
docker-compose up --build
```

### ☁️ Kubernetes Deployment (Minikube)

1. Start your cluster:
   ```bash
   minikube start
   ```

2. (Optional) Use Minikube’s Docker daemon:
   ```bash
   eval $(minikube docker-env)
   ```

3. Apply configurations:
   ```bash
   kubectl apply -f .
   ```

4. Verify deployments:
   ```bash
   kubectl get pods
   kubectl get services
   ```

---

## 🌐 API Endpoints

### UserService (`http://localhost:5002`)
- `POST /users/add` – Add new user  
- `GET /users/all` – Get all users  
- `GET /users/<id>` – Get user by ID  
- `PUT /users/<id>` – Update user by ID  
- `DELETE /users/<id>` – Delete user by ID  

### BookService (`http://localhost:5001`)
- `POST /books/add` – Add new book  
- `GET /books/all` – Get all books  
- `GET /books/<id>` – Get book by ID  
- `PUT /books/<id>` – Update book by ID  
- `DELETE /books/<id>` – Delete book by ID  

### BorrowService (`http://localhost:5000`)
- `POST /borrow` – Borrow a book  
- `GET /borrow/history` – Get all borrow records  

---

## 🔧 Testing Instructions

### 1. Port-Forward Services

In separate terminals:

```bash
kubectl port-forward service/userservice 5002:5002
kubectl port-forward service/bookservice 5001:5001
kubectl port-forward service/borrowservice 5000:5000
```

### 2. Sample Requests (JSON)

#### `POST /users/add`
```json
{
  "name": "Alice",
  "email": "alice@example.com"
}
```

#### `POST /books/add`
```json
{
  "title": "Example Book",
  "author": "John Doe"
}
```

#### `POST /borrow`
```json
{
  "user_id": 1,
  "book_id": 101
}
```

Use Postman or cURL to test the endpoints. Ensure RabbitMQ is up and running.

---

## 📁 Project Structure

```
CML-V3/
├── BookService/
├── UserService/
├── BorrowService/
├── *.yaml         # Kubernetes configs
├── docker-compose.yaml
├── Cloud Microservices Library.postman_collection.json
```

---

## 👨‍💻 Author

**Manish Tawade**  
MSc Computer Science, University College Dublin


---

## 🔄 Docker Compose Conversion

This project uses **`kompose`** to convert Docker Compose files into Kubernetes manifests:

```bash
kompose convert
```

This command generates the necessary Kubernetes deployment and service YAMLs from `docker-compose.yaml`.

---

## 📫 Postman Collection

A Postman collection is included in the repository for easier testing:

**Filename:** `Cloud Microservices Library.postman_collection.json`

You can import it into Postman to quickly access and test all endpoints for UserService, BookService, and BorrowService.

---
