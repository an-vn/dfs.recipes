import logging
from dfs_recipes.database.sqlite_client import SQLiteClient
from dfs_recipes.database.in_memory_client import InMemoryClient

log = logging.getLogger(__name__)

# db_client = SQLiteClient('checkpoints.db')
db_client = InMemoryClient()
