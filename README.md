# 🔐 Secure Auth API (FastAPI + Supabase)

A lightweight, production-ready authentication API built using **Python**, **FastAPI**, and **Supabase**. This API implements full user lifecycles, JWT token validation, protected middleware guards, and interactive Swagger UI integration with Bearer authentication.

---

## 🚀 Features

- **User Authentication:** Asynchronous sign-up and password-based sign-in.
- **Role/Admin Privileges:** Admin-level auto-confirmation using Supabase `service_role` keys.
- **Token Security:** Bearer token extraction and live signature/expiration verification via Supabase Auth SDK.
- **FastAPI Dependencies:** Reusable security guard (`get_current_user`) for protected endpoints.
- **Session Control:** Secure logout endpoint that revokes active JWT sessions.
- **Interactive Documentation:** Swagger UI with `HTTPBearer` padlock configuration.

---

## 📊 API Reference

| Endpoint | Method | Auth Required? | Description |
| :--- | :---: | :---: | :--- |
| `/auth/signup` | `POST` | ❌ No | Registers a new user account. |
| `/auth/login` | `POST` | ❌ No | Authenticates credentials and returns JWT access tokens. |
| `/public/info` | `GET` | ❌ No | Public health check / info route. |
| `/protected/profile` | `GET` | 🔑 Yes | Returns the logged-in user's profile metadata. |
| `/protected/dashboard` | `GET` | 🔑 Yes | Returns personalized VIP dashboard payload. |
| `/auth/logout` | `POST` | 🔑 Yes | Invalidates the user's active session token (HTTP 204). |

---

## 📖 Interactive Documentation (Swagger UI)

![Swagger UI Documentation](assets/Swagger_UI.png)

Access the live interactive documentation by navigating to `http://127.0.0.1:8000/docs`.

## 🛠️ Getting Started

### Prerequisites

- Python 3.10+
- A [Supabase](https://supabase.com/) project

### 1. Clone the Repository
```bash
git clone [https://github.com/shivii-mallya/Auth-Practice-Internship.git](https://github.com/shivii-mallya/Auth-Practice-Internship.git)
cd Auth-Practice-Internship