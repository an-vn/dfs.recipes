import os
import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from dfs_recipes.config import settings, limiter
from dfs_recipes.database.checkpoints import db_client
from dfs_recipes.api import health, charts, history, auth
from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_client.init()
    app.include_router(auth.router, prefix='/api', tags=['Auth'])
    app.include_router(health.router, prefix='/api', tags=['Health'])
    app.include_router(charts.router, prefix='/api', tags=['Charts'])
    app.include_router(history.router, prefix='/api', tags=['History'])
    # app.mount('/', StaticFiles(directory=_static_dir, html=True), name='static')
    yield


app = FastAPI(
    title='DFS Recipes',
    description='Recipes for Daily Fantasy Sports',
    version='1.0.0',
    lifespan=lifespan,
    middleware=[
        Middleware(
            SessionMiddleware,
            secret_key=settings.session_encryption_key,
            session_cookie=settings.session_cookie_key,
            max_age=86400,
            path='/api',
            same_site='none',
            https_only=True,
            domain='dfs-recipes.com' if os.getenv('ENV') == 'PROD' else 'localhost',
        ),
        Middleware(
            CORSMiddleware,
            allow_origins=['https://localhost:3000', 'https://dfs-recipes.com'],
            allow_methods=['OPTIONS', 'HEAD', 'GET', 'POST', 'PUT', 'DELETE'],
            allow_headers=['Accept', 'Authorization', 'Content-Type'],
            allow_credentials=True,
            max_age=86400
        ),
        Middleware(
            SlowAPIMiddleware
        )
    ]
)

app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

if __name__ == '__main__':
    import uvicorn

    cert_path = Path(__file__).parent.parent.parent / 'local.cer'
    key_path = Path(__file__).parent.parent.parent / 'local.key'

    uvicorn.run(
        app,
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', '8000')),
        access_log=True,
        timeout_keep_alive=300,
        ssl_certfile=cert_path,
        ssl_keyfile=key_path,
    )
