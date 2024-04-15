import uuid

from fastapi import Depends, APIRouter, HTTPException, Response, Request, Query, status

from agnostic.core import crud
from agnostic.core.schemas import v2 as s

router = APIRouter(tags=["Metrics Over Time"], prefix="/metrics-ot")


@router.post(
    "",
    responses={
        status.HTTP_201_CREATED: {
            "headers": {
                "Location": {"description": "URL of the created metric over time", "type": "string"}
            }
        },
        status.HTTP_404_NOT_FOUND: {},
        status.HTTP_409_CONFLICT: {},
    },
    status_code=status.HTTP_201_CREATED,
)
async def create_metric_over_time(
    metric_ot: s.MetricOverTimeCreate,
    request: Request,
    response: Response,
    metrics_ot: crud.MetricsOverTime = Depends(crud.get_metrics_over_time),
):
    try:
        metric_ot_id = await metrics_ot.create(metric_ot)
        response.headers.append("Location", f"{request.url.path}/{metric_ot_id}")
    except crud.DuplicateError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))
    except crud.ForeignKeyError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.put(
    "/{metric_ot_id}",
    responses={
        status.HTTP_201_CREATED: {
            "headers": {
                "Location": {"description": "URL of the created metric over time", "type": "string"}
            }
        },
        status.HTTP_204_NO_CONTENT: {},
        status.HTTP_409_CONFLICT: {},
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
async def update_metric_over_tim(
    metric_ot: s.MetricOverTimeUpdate,
    metric_ot_id: uuid.UUID,
    request: Request,
    response: Response,
    metrics_ot: crud.MetricsOverTime = Depends(crud.get_metrics_over_time),
):
    try:
        await metrics_ot.update(metric_ot_id, metric_ot)
    except crud.NotFoundError:
        try:
            await metrics_ot.create(
                s.MetricOverTime(id=metric_ot_id, **metric_ot.model_dump(exclude_unset=True))
            )
            response.status_code = status.HTTP_201_CREATED
            response.headers.append("Location", f"{request.url.path}/{metric_ot_id}")
        except (crud.DuplicateError, crud.ForeignKeyError) as e:
            raise HTTPException(status.HTTP_409_CONFLICT, str(e))


@router.patch(
    "/{metric_ot_id}",
    responses={
        status.HTTP_204_NO_CONTENT: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
async def patch_metric_over_time(
    metric_ot: s.MetricOverTimePatch,
    metric_ot_id: uuid.UUID,
    metrics: crud.MetricsOverTime = Depends(crud.get_metrics_over_time),
):
    try:
        await metrics.update(metric_ot_id, metric_ot, exclude_unset=True)
    except crud.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.get(
    "/{metric_ot_id}",
    responses={
        status.HTTP_200_OK: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    status_code=status.HTTP_200_OK,
)
async def get_metric_over_time(
    metric_ot_id: uuid.UUID, metrics_ot: crud.MetricsOverTime = Depends(crud.get_metrics_over_time)
) -> s.MetricOverTime:
    try:
        return await metrics_ot.get(metric_ot_id)
    except crud.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.get(
    "",
    responses={
        status.HTTP_200_OK: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    status_code=status.HTTP_200_OK,
)
async def get_metrics_over_time(
    response: Response,
    test_run_id: uuid.UUID | None = Query(None),
    test_id: uuid.UUID | None = Query(None),
    page: int = Query(1),
    page_size: int = Query(100),
    metrics: crud.MetricsOverTime = Depends(crud.get_metrics_over_time),
) -> s.MetricsOverTime:
    result = await metrics.get_all(test_run_id, test_id, page, page_size)
    response.headers.append("X-Total-Count", str(result.count))
    return result.items
