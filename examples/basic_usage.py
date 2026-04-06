from sqlalchemy import Column, Integer, String, MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase
from schema_evolver.parser import parse_sqlalchemy, parse_database
from schema_evolver.diff.engine import DiffEngine
from schema_evolver.planner import Planner
from schema_evolver.executor import SQLExecutor

# 1. Define current Models in code
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100)) # New column

# 2. Mocking a database connection
# In a real scenario, you'd use your actual DB URL
engine = create_engine("sqlite:///:memory:")

# 3. Analyze DB state and Code state
db_schema = parse_database(engine)
code_schema = parse_sqlalchemy(Base)

# 4. Compute Diffs
diff_engine = DiffEngine()
operations = diff_engine.diff(db_schema, code_schema)

print(f"Detected {len(operations)} schema changes:")
for op in operations:
    print(f"- {op.type.upper()}: {op}")

# 5. Generate Plan
planner = Planner()
plan = planner.plan(operations)

# 6. Generate SQL
executor = SQLExecutor(engine)
sql_statements = executor.generate_sql(plan)

print("\nPlanned SQL:")
for sql in sql_statements:
    print(f"  {sql};")

# 7. Apply (optional)
# executor.execute(plan)
