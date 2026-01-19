"""
Validate Decision model structure without database connection.
This script checks the model definition is correct.
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock database modules to avoid installation issues
class MockDBAPI:
    __version__ = "2.9.9"
    
    def __getattr__(self, name):
        return lambda *args, **kwargs: None

class MockModule:
    def __getattr__(self, name):
        if name == '__version__':
            return "0.29.0"
        return MockModule()
    
    def __call__(self, *args, **kwargs):
        return MockModule()
    
    def import_dbapi(self):
        return MockDBAPI()

sys.modules['asyncpg'] = MockModule()
sys.modules['psycopg2'] = MockDBAPI()

# Mock settings to avoid database connection
os.environ['DATABASE_URL'] = 'postgresql://user:pass@localhost/test'
os.environ['DEBUG'] = 'false'
os.environ['OPENROUTER_API_KEY'] = 'test-key'

# Now we can import without database drivers
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql
from app.models.decision import Decision

def validate_model():
    """Validate the Decision model structure."""
    print("="*70)
    print("VALIDATING DECISION MODEL STRUCTURE")
    print("="*70)
    
    # Check table name
    print(f"\n✓ Table name: {Decision.__tablename__}")
    assert Decision.__tablename__ == "decisions", "Table name should be 'decisions'"
    
    # Get all columns
    columns = {col.name: col for col in Decision.__table__.columns}
    print(f"✓ Total columns: {len(columns)}")
    
    # Check required columns exist
    required_columns = {
        'id': 'UUID',
        'created_at': 'TIMESTAMP',
        'updated_at': 'TIMESTAMP',
        'title': 'VARCHAR',
        'context': 'TEXT',
        'constraints': 'ARRAY',
        'options': 'ARRAY',
        'structured_decision': 'JSONB',
        'bias_report': 'JSONB',
        'outcome_simulations': 'JSONB',
        'reflection_insight': 'JSONB',
        'actual_outcome': 'TEXT',
        'actual_outcome_date': 'TIMESTAMP',
        'execution_log': 'JSONB'
    }
    
    print("\n" + "="*70)
    print("COLUMN VALIDATION")
    print("="*70)
    
    for col_name, expected_type in required_columns.items():
        assert col_name in columns, f"Missing column: {col_name}"
        col = columns[col_name]
        col_type = type(col.type).__name__
        print(f"✓ {col_name:25} {col_type:20} (expected: {expected_type})")
    
    # Check primary key
    pk_columns = [col.name for col in Decision.__table__.primary_key.columns]
    print("\n" + "="*70)
    print("PRIMARY KEY")
    print("="*70)
    print(f"✓ Primary key columns: {pk_columns}")
    assert pk_columns == ['id'], "Primary key should be 'id'"
    
    # Check indexes
    indexes = list(Decision.__table__.indexes)
    print("\n" + "="*70)
    print("INDEXES")
    print("="*70)
    print(f"✓ Number of indexes: {len(indexes)}")
    for idx in indexes:
        cols = [col.name for col in idx.columns]
        print(f"  - {idx.name}: {cols}")
    
    assert len(indexes) >= 1, "Should have at least one index"
    
    # Check JSONB columns
    jsonb_columns = ['structured_decision', 'bias_report', 'outcome_simulations', 
                     'reflection_insight', 'execution_log']
    print("\n" + "="*70)
    print("JSONB COLUMNS")
    print("="*70)
    for col_name in jsonb_columns:
        col = columns[col_name]
        is_jsonb = isinstance(col.type, postgresql.JSONB)
        status = "✓" if is_jsonb else "✗"
        print(f"{status} {col_name:25} {type(col.type).__name__}")
        assert is_jsonb, f"{col_name} should be JSONB type"
    
    # Check UUID column
    print("\n" + "="*70)
    print("UUID COLUMN")
    print("="*70)
    id_col = columns['id']
    is_uuid = isinstance(id_col.type, postgresql.UUID)
    status = "✓" if is_uuid else "✗"
    print(f"{status} id column is UUID type: {type(id_col.type).__name__}")
    assert is_uuid, "id should be UUID type"
    
    # Check ARRAY columns
    array_columns = ['constraints', 'options']
    print("\n" + "="*70)
    print("ARRAY COLUMNS")
    print("="*70)
    for col_name in array_columns:
        col = columns[col_name]
        # Check if it's an ARRAY type (could be ARRAY from sqlalchemy.types or postgresql.ARRAY)
        from sqlalchemy.types import ARRAY as GenericARRAY
        is_array = isinstance(col.type, (postgresql.ARRAY, GenericARRAY))
        status = "✓" if is_array else "✗"
        print(f"{status} {col_name:25} {type(col.type).__name__}")
        assert is_array, f"{col_name} should be ARRAY type"
    
    # Check nullable constraints
    print("\n" + "="*70)
    print("NULLABLE CONSTRAINTS")
    print("="*70)
    not_nullable = ['id', 'created_at', 'updated_at', 'title', 'context']
    for col_name in not_nullable:
        col = columns[col_name]
        status = "✓" if not col.nullable else "✗"
        print(f"{status} {col_name:25} NOT NULL: {not col.nullable}")
        assert not col.nullable, f"{col_name} should be NOT NULL"
    
    # Test model methods
    print("\n" + "="*70)
    print("MODEL METHODS")
    print("="*70)
    assert hasattr(Decision, 'to_dict'), "Missing to_dict method"
    print("✓ to_dict method exists")
    assert hasattr(Decision, 'has_reflection'), "Missing has_reflection property"
    print("✓ has_reflection property exists")
    assert hasattr(Decision, '__repr__'), "Missing __repr__ method"
    print("✓ __repr__ method exists")
    
    # Generate CREATE TABLE statement
    print("\n" + "="*70)
    print("GENERATED SQL (CREATE TABLE)")
    print("="*70)
    from sqlalchemy.schema import CreateTable
    create_table = CreateTable(Decision.__table__).compile(dialect=postgresql.dialect())
    sql = str(create_table)
    
    # Print formatted SQL
    for line in sql.split('\n'):
        print(line)
    
    print("\n" + "="*70)
    print("✅ ALL VALIDATIONS PASSED!")
    print("="*70)
    print("\nThe Decision model is correctly defined with:")
    print("  - UUID primary key")
    print("  - Timestamp fields (created_at, updated_at)")
    print("  - User input fields (title, context, constraints, options)")
    print("  - JSONB fields for agent outputs")
    print("  - ARRAY fields for lists")
    print("  - Proper indexes")
    print("  - Helper methods (to_dict, has_reflection)")
    print("\nReady for database migration!")
    print("="*70)

if __name__ == "__main__":
    try:
        validate_model()
    except AssertionError as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
