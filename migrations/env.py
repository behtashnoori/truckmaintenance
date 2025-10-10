import sys
import os
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from logging.config import fileConfig

from flask import current_app

from alembic import context
from backend.app import create_app

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# Create a Flask app context for Alembic
app = create_app()
with app.app_context():
    # add your model's MetaData object here
    # for 'autogenerate' support
    # from myapp import mymodel
    # target_metadata = mymodel.Base.metadata
    target_metadata = current_app.extensions['migrate'].db.metadata
    
    def get_engine_url():
        try:
            return current_app.extensions['migrate'].db.engine.url.render_as_string(hide_password=False).replace(
                '%', '%%')
        except AttributeError:
            return str(current_app.extensions['migrate'].db.engine.url).replace('%', '%%')
    
    config.set_main_option('sqlalchemy.url', get_engine_url())
    
    def get_metadata():
        if hasattr(current_app.extensions['migrate'].db, 'metadatas'):
            return current_app.extensions['migrate'].db.metadatas[None]
        return current_app.extensions['migrate'].db.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=get_metadata(), literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Force PostgreSQL connection string to override any environment variables
    import os
    os.environ['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:bagheri13@localhost:5432/Marketplace'
    
    # Create a Flask app context for Alembic
    app = create_app()
    with app.app_context():
        # this is the Alembic Config object, which provides
        # access to the values within the .ini file in use.
        config = context.config

        # Interpret the config file for Python logging.
        # This line sets up loggers basically.
        fileConfig(config.config_file_name)
        logger = logging.getLogger('alembic.env')

        # Force the correct database URL
        config.set_main_option('sqlalchemy.url', 'postgresql+psycopg2://postgres:bagheri13@localhost:5432/Marketplace')

        # add your model's MetaData object here
        # for 'autogenerate' support
        target_metadata = current_app.extensions['migrate'].db.metadata

        connectable = current_app.extensions['migrate'].db.get_engine()

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                **current_app.extensions['migrate'].configure_args
            )

            with context.begin_transaction():
                context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
