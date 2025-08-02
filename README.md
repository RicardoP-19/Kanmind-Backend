# KanMind Backend

A Django REST API backend for a Kanban-style project management tool.

## Features

- Token-based user authentication
- Board creation and member management
- Task management with status, priority, and due dates
- Task assignment and review functionality
- Comment system for each task
- Email availability check

## Prerequisites

- Python 3.11 or higher
- pip
- virtualenv (recommended)

## Installation

Clone the repository:

```bash
git clone <your-repository-url>
cd kanmind-backend
```

Create and activate a virtual environment:

```bash
# Windows
python -m venv env
env\Scripts\activate

# Linux/Mac
python3 -m venv env
source env/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
python manage.py migrate
```

Create a superuser (optional):

```bash
python manage.py createsuperuser
```

## Running the Server

```bash
python manage.py runserver
```

Server runs at: `http://localhost:8000`

## API Endpoints

### Authentication

- `POST /api/registration/` – Register new user
- `POST /api/login/` – Login user
- `GET /api/email-check/?email=...` – Check if email is registered

### Boards

- `GET /api/boards/` – List user boards
- `POST /api/boards/` – Create new board
- `GET /api/boards/<board_id>/` – Get board details
- `PATCH /api/boards/<board_id>/` – Update board title/members
- `DELETE /api/boards/<board_id>/` – Delete board (owner only)

### Tasks

- `POST /api/tasks/` – Create task
- `PATCH /api/tasks/<task_id>/` – Update task
- `DELETE /api/tasks/<task_id>/` – Delete task (owner only)
- `GET /api/tasks/assigned-to-me/` – Tasks assigned to user
- `GET /api/tasks/reviewing/` – Tasks for user to review

### Comments

- `GET /api/tasks/<task_id>/comments/` – List comments
- `POST /api/tasks/<task_id>/comments/` – Add comment
- `DELETE /api/tasks/<task_id>/comments/<comment_id>/` – Delete comment (author only)

## Environment Variables

Create a `.env` file in the root directory:

```env
DEBUG=True
SECRET_KEY=your-secret-key
```

## Contributing

1. Fork the repository
2. Create a new feature branch
3. Commit your changes
4. Push to your fork
5. Open a pull request

## License

MIT License
