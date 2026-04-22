from config import (
    APP_HOST,
    APP_PORT
)

import uvicorn

if __name__ == "__main__":
    uvicorn.run("entrypoints.app:app", host=APP_HOST, port=int(APP_PORT))