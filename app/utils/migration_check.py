import os
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext


def ensure_db_is_up_to_date(db_engine, migrations_path: str):
    """
    Raises RuntimeError if the database's current revision does not match
    the latest (head) revision in the migrations directory.
    """
    # 1) Load Alembic config from your project root (alembic.ini)
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), '..', '..', 'alembic.ini'))

    # 2) Point to the versions folder
    alembic_cfg.set_main_option('script_location', migrations_path)
    script = ScriptDirectory.from_config(alembic_cfg)
    head_rev = script.get_current_head()

    # 3) Inspect the DB's current revision
    with db_engine.connect() as conn:
        context = MigrationContext.configure(conn)
        current_rev = context.get_current_revision() or 'base'

    if current_rev != head_rev:
        raise RuntimeError(
            f"Database migration mismatch: current={current_rev}, head={head_rev}. "
            f"Please run 'flask db upgrade' before starting the app."
        )
