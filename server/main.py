import sqlalchemy

from dotenv import dotenv_values
from fastapi import FastAPI
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

from api.routers import auth, users, campaigns, prospects, prospects_files

from loguru import logger
import logging
import os
import sys

## custom logging based on: https://pawamoy.github.io/posts/unify-logging-for-a-gunicorn-uvicorn-app/
LOG_LEVEL = logging.getLevelName(os.environ.get("LOG_LEVEL", "DEBUG"))
JSON_LOGS = True if os.environ.get("JSON_LOGS", "0") == "1" else False


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage())


def setup_logging():
    # intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(LOG_LEVEL)

    # remove every other logger's handlers
    # and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # configure loguru
    logger.configure(handlers=[{"sink": sys.stdout, "serialize": JSON_LOGS}])


config = dotenv_values(".env")

app = FastAPI(
    title="Sales Automation - Python (FastAPI)",
    description="Sales Automation Work Simulation",
    version="0.0.1",
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(campaigns.router)
app.include_router(prospects.router)
app.include_router(prospects_files.router)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(_, exc):
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)


if __name__ == "__main__":
    from uvicorn import Config, Server
    from api.database import Base

    server = Server(
        Config(
            "main:app",
            host="0.0.0.0",
            reload=True,
            port=3001,
            log_level=LOG_LEVEL,
        ),
    )

    engine = sqlalchemy.create_engine(config.get("DATABASE_URL"))
    Base.metadata.create_all(engine)

    setup_logging()

    server.run()
