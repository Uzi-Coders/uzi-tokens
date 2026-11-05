# Uzi Tokens

A small Django REST API for authentication and API token management.

Base URL: `/api/uzi-token/`

## Docs (Persian)

- [Authentication](docs/auth.md)
- [Core endpoints](docs/core.md)
- [API tokens](docs/tokens.md)

## Quick start (Docker)

Create a `.env` file:

```bash
cp .env.example .env
```

Build and run:

```bash
docker build -t uzi-tokens .

docker run -d --name uzi-tokens \
  --env-file .env \
  -p 8000:8000 \
  uzi-tokens
```

Notes:

- Use `DEBUG=0` in production.
- Values passed with `--env-file` are not unquoted by Docker, so do not wrap them in `"`.
- Data lives in SQLite inside the container. To persist it, add a volume.

## License

[MIT License](LICENSE)]
