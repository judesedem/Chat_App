# ChatApp API

A real-time room-based chat backend built with Django Channels and WebSockets. Users join rooms with a username and interact live through messages and emoji reactions. No account registration required.

---

## Features

- Real-time messaging via WebSockets
- Room-based chat — multiple rooms, isolated conversations
- Emoji reaction broadcasting
- Join/leave notifications
- Persistent message storage (SQLite)
- Active user tracking per room (in-memory)
- REST API for room management and message history
- Graceful error handling — bad input won't drop your connection

---

## Tech Stack

- Python 3
- Django 5
- Django REST Framework
- Django Channels 4
- Redis (channel layer)
- Daphne (ASGI server)
- SQLite

---

## Project Structure

```
Chat_App/
├── Chat/
│   ├── consumers.py      # WebSocket consumer
│   ├── models.py         # Room and Message models
│   ├── serializers.py    # DRF serializers
│   ├── views.py          # REST API views
│   ├── urls.py           # HTTP routes
│   └── routing.py        # WebSocket routes
├── Chat_App/
│   ├── asgi.py           # ASGI config with ProtocolTypeRouter
│   └── settings.py
└── manage.py
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Docker (for Redis)

### Installation

1. Clone the repository

```bash
git clone https://github.com/judesedem/Chat_App.git
cd chatapp-api
```

2. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Start Redis

```bash
docker run -d -p 6379:6379 redis
```

5. Run migrations

```bash
python manage.py migrate
```

6. Start the server

```bash
python manage.py runserver
```

---

## REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/Chat/room/` | List all rooms |
| POST | `/Chat/room/` | Create a room |
| GET | `/Chat/messages/<room_id>/` | Get message history for a room |

---

## WebSocket Usage

### Connect

```
ws://localhost:8000/ws/chat/<room_name>/?username=Jude
```

### Send a message

```json
{"type": "message", "message": "hello"}
```

### Send a reaction

```json
{"type": "reaction", "emoji": "👍"}
```

### Events received from server

| Event type | Payload |
|------------|---------|
| `message` | `{"type": "message", "message": "...", "username": "..."}` |
| `reaction` | `{"type": "reaction", "emoji": "...", "username": "..."}` |
| `join` | `{"type": "join", "username": "..."}` |
| `leave` | `{"type": "leave", "username": "..."}` |
| `error` | `{"error": "..."}` |

---

## Testing with Postman

1. Open Postman → New → WebSocket
2. Connect to `ws://127.0.0.1:8000/ws/chat/general/?username=Jude`
3. Send JSON messages using the formats above
4. Open a second connection with a different username to test real-time delivery

---

## Environment Variables

Create a `.env` file in the root directory:

```
SECRET_KEY=your-secret-key
DEBUG=True
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
```

---

## Author

**Jude Sedem**
GitHub: [@judesedem](https://github.com/judesedem)
