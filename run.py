from os import environ
from app import app

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(environ.get("SERVER_PORT", 8081)))
