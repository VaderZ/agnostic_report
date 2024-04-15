import datetime
import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select, update, and_, func

from agnostic.core import models as m
from agnostic.core.schemas import v2 as s
from .exceptions import DuplicateError, ForeignKeyError, NotFoundError


class MetricsOverTime:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id_: uuid.UUID) -> s.MetricOverTime:
        metric_ot = (
            await self.session.execute(select(m.MetricOverTime).where(m.MetricOverTime.id == id_))
        ).scalar()

        if not metric_ot:
            raise NotFoundError(f"Metric Over Time {id_} does not exist")

        return s.MetricOverTime.model_validate(metric_ot)

    async def get_all(
        self,
        test_run_id: uuid.UUID | None,
        test_id: uuid.UUID | None,
        page: int = 1,
        page_size: int = 100,
    ) -> s.CRUDCollection:
        where = []
        if test_run_id:
            where.append(m.MetricOverTime.test_run_id == test_run_id)
        if test_id:
            where.append(m.MetricOverTime.test_id == test_id)
        count = (
            await self.session.execute(select(func.count(m.MetricOverTime.id)).where(and_(*where)))
        ).scalar()
        metrics_ot = (
            (
                await self.session.execute(
                    select(m.MetricOverTime)
                    .where(and_(*where))
                    .order_by(m.MetricOverTime.timestamp.desc())
                    .offset(page_size * (page - 1))
                    .limit(page_size)
                )
            )
            .scalars()
            .all()
        )

        return s.CRUDCollection(items=s.MetricsOverTime.model_validate(metrics_ot), count=count)

    async def create(self, metric_ot: s.MetricOverTimeCreate) -> uuid.UUID:
        metric_ot.id = metric_ot.id or uuid.uuid4()
        metric_ot.timestamp = metric_ot.timestamp or datetime.datetime.now(datetime.UTC)
        self.session.add(m.MetricOverTime(**metric_ot.model_dump()))

        try:
            await self.session.commit()
        except IntegrityError as e:
            if "foreign key constraint" in e.orig.args[0]:
                raise ForeignKeyError(
                    f"Test Run {metric_ot.test_run_id} or Test {metric_ot.test_id} does not exist"
                )
            else:
                raise DuplicateError(f"Metric Over Time {metric_ot.id} already exists")

        return metric_ot.id

    async def update(
        self,
        id_: uuid.UUID,
        metric_ot: s.MetricOverTimeUpdate | s.MetricOverTimePatch,
        exclude_unset: bool = False,
    ) -> uuid.UUID:
        try:
            result = await self.session.execute(
                update(m.MetricOverTime)
                .where(m.MetricOverTime.id == id_)
                .values(**metric_ot.model_dump(exclude_unset=exclude_unset))
            )
        except IntegrityError:
            raise NotFoundError(f"Test Run {metric_ot.test_run_id} does not exist")

        if result.rowcount < 1:
            raise NotFoundError(f"Metric Over Time {metric_ot.id} does not exist")

        await self.session.commit()

        return id_
