import uvicorn

from src.create_app import create_app

app = create_app()


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8080, log_level="info")
