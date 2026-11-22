import asyncio
from typing import Any

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from bot.core import setup_logging
from bot.core.config import settings
from bot.database.base import Base

# Imported so every model registers its table on Base.metadata for autogenerate.
from bot.database.download.models import Download  # noqa: F401
from bot.database.job.models import Job  # noqa: F401
from bot.database.user.models import User  # noqa: F401

config = context.config

setup_logging()

target_metadata = Base.metadata

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.get_secret_value())


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Any) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
