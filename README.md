# 📌 Kanmind API Backend

Kanmind is a Django-based backend API for a collaborative kanban-style task management system.

---

## 🚀 Tech Stack

- **Language**: Python 3.11+
- **Framework**: Django 4.x, Django REST Framework
- **Database**: SQLite (development) / PostgreSQL (recommended for production)

---

## 🧩 Core Features

- 🔐 Token-based user authentication
- 🧠 Role-based permissions for board owners and members
- 📋 Create and manage boards with members
- ✅ Task system with statuses, priorities, and deadlines
- 👥 Assign users as task assignees and reviewers
- 💬 Comment system per task
- 📧 Check if an email is already registered

---

## ⚙️ Setup Instructions

### 1. Clone Repository

```bash
git clone <your-repository-url>
cd kanmind-backend
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv env
env\Scripts\activate

# macOS/Linux
python3 -m venv env
source env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Start Development Server

```bash
python manage.py runserver
```

Server runs at: `http://127.0.0.1:8000`

---

## 📡 API Endpoints Overview

### 🔑 Authentication
- `POST /api/registration/` – Create new user
- `POST /api/login/` – Authenticate user
- `GET /api/email-check/?email=...` – Check email availability

### 📁 Boards
- `GET /api/boards/` – List boards of current user
- `POST /api/boards/` – Create new board
- `GET /api/boards/<id>/` – Get board details
- `PATCH /api/boards/<id>/` – Update board title/members
- `DELETE /api/boards/<id>/` – Delete board (only owner)

### 📌 Tasks
- `POST /api/tasks/` – Create task
- `PATCH /api/tasks/<id>/` – Update task
- `DELETE /api/tasks/<id>/` – Delete task (only owner)
- `GET /api/tasks/assigned-to-me/` – Tasks assigned to user
- `GET /api/tasks/reviewing/` – Tasks user should review

### 💬 Comments
- `GET /api/tasks/<task_id>/comments/` – List comments
- `POST /api/tasks/<task_id>/comments/` – Add comment
- `DELETE /api/tasks/<task_id>/comments/<comment_id>/` – Delete comment (only author)

---

## 🛡️ Environment Variables

Create a `.env` file:

```env
DEBUG=True
SECRET_KEY=your-secret-key
```

---

## 📄 License

Licensed under the **MIT License**.
