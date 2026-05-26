# webXis — Web Solutions

A Django marketing website for **webXis**, a web solutions company offering design, development, hosting, and support.

## Requirements

- Python 3.10+ (local development)
- [Docker](https://www.docker.com/) (optional, recommended for deployment)

## Local setup (without Docker)

```bash
cd webxis
python -m pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## Docker

Copy the environment file and start the stack:

```bash
copy .env.example .env
docker compose up --build
```

The site runs at [http://localhost:8000/](http://localhost:8000/) with Gunicorn.

### Development with hot reload

```bash
docker compose -f docker-compose.dev.yml up --build
```

## Pages

| URL | Page |
|-----|------|
| `/` | Home |
| `/services/` | Services |
| `/about/` | About |
| `/contact/` | Contact |
| `/accounts/signup/` | Client sign up |
| `/accounts/login/` | Client sign in |
| `/dashboard/` | Client dashboard (projects & progress) |
| `/dashboard/invoices/` | Invoices (maintenance/hosting clients) |

### Demo client data

```bash
python manage.py seed_demo_client
# Login: demo / demo1234
```

In Django admin, enable **Has maintenance hosting** on a client profile to show invoices.

## Environment variables

| Variable | Description |
|----------|-------------|
| `DJANGO_SECRET_KEY` | Secret key (required in production) |
| `DJANGO_DEBUG` | `True` or `False` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames |
| `DATABASE_PATH` | SQLite file path (Docker uses `/app/data/db.sqlite3`) |

## Project structure

```
webxis/
├── core/                 # Main app (views, URLs)
├── static/               # CSS, JavaScript
├── templates/            # HTML templates
├── webxis/               # Project settings
├── Dockerfile
├── docker-compose.yml
├── docker-compose.dev.yml
├── entrypoint.sh
├── manage.py
└── requirements.txt
```

## GitHub

```bash
git init
git add .
git commit -m "Initial commit: webXis Django site with Docker"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/webxis.git
git push -u origin main
```

Create an empty repository named `webxis` on GitHub first, then replace `YOUR_USERNAME`.

## Production notes

- Set `DJANGO_DEBUG=False` and a strong `DJANGO_SECRET_KEY`
- Set `DJANGO_ALLOWED_HOSTS` to your domain
- Consider PostgreSQL instead of SQLite for production
