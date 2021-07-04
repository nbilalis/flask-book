from os import environ
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(environ.get("SERVER_PORT", 8081)))
