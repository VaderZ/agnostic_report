import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette import concurrency

from agnostic.core import config
from agnostic.core.migrations import upgrade
from .routers import v1, v2
from .utils import SPA, simplify_operation_ids

base_dir = Path(__file__).parent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

api_v1 = FastAPI(ptitle="Agnostic Report", default_response_class=ORJSONResponse)
api_v1.include_router(v1.projects.router)
api_v1.include_router(v1.test_runs.router)
api_v1.include_router(v1.tests.router)
api_v1.include_router(v1.logs.router)
api_v1.include_router(v1.metrics.router)
api_v1.include_router(v1.metrics_ot.router)
api_v1.include_router(v1.progress.router)
api_v1.include_router(v1.requests.router)
api_v1.include_router(v1.attachments.router)
api_v1.include_router(v1.reporting.router)
api_v1.include_router(v1.system.router)

simplify_operation_ids(api_v1)

api_v2 = FastAPI(ptitle="Agnostic Report", default_response_class=ORJSONResponse)
api_v2.include_router(v2.projects.router)
api_v2.include_router(v2.test_runs.router)
api_v2.include_router(v2.tests.router)
api_v2.include_router(v2.metrics.router)
api_v2.include_router(v2.metrics_ot.router)
api_v2.include_router(v2.progress.router)
api_v2.include_router(v2.logs.router)
api_v2.include_router(v2.attachments.router)

simplify_operation_ids(api_v2)

app = FastAPI(title="Agnostic Report", version="1.0")
app.mount("/api/v1", api_v1)
app.mount("/api/v2", api_v2)
app.mount("/", SPA(directory=base_dir / ".." / "ui", html=True), name="ui")


@app.on_event("startup")
async def startup():
    log.info(
        f'Connecting to the "{config.options.db_database}" database '
        f"at {config.options.db_host}:{config.options.db_port}"
    )
    log.info("Migrating Agnostic database")
    await concurrency.run_in_threadpool(upgrade.run)
    log.info("Agnostic database migration finished")
