# Python-Orders-App


A full-stack backend service built with **Flask**, providing a REST API for managing customers and orders.  
It includes OpenID Connect authentication, unit tests with coverage, Docker support, and a GitLab CI/CD pipeline.

---

## 📸 Dashboard Preview

![Dashboard Screenshot](dashboard.png)



---

## Features

- **Customer Management**: Add and retrieve customers (name, phone, created_by).
- **Order Management**: Add and retrieve orders (item, price, timestamp).
- **Authentication & Authorization**: OpenID Connect (Google or another OIDC provider).
- **Unit Testing & Coverage**: Pytest + coverage, CI threshold enforcement.
- **Dockerized**: Build and push images to Docker Hub automatically.
- **GitLab CI/CD**: Automated test, build, deploy pipeline.

---

API ENDPOINTS
 Method  Endpoint          Description       
 POST    `/api/customers`  Create a customer 
 GET     `/api/customers`  List customers    
 POST    `/api/orders`     Create an order   
 GET     `/api/orders`     List orders       
 GET     `/health`         Health check      


