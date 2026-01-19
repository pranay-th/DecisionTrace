"""
Test script to validate Decision model structure without database connection.
"""

import sys
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

# Mock the asyncpg import to avoid installation issues
sys.modules['asyncpg'] = type(sys)('asyncpg')

from app.models.decision import Decision

def test_decision_model():
    """Test Decision model structure."""
    print("Testing Decision model structure...\n")
    
    # Check table name
    print(f"✓ Table name: {Decision.__tablename__}")
    assert Decision.__tablename__ == "decisions"
    
    # Get all columns
    columns = {col.name: col for col in Decision.__table__.columns}
    print(f"\n✓ Total columns: {len(columns)}")
    
    # Check required columns
    required_columns = [
        'id', 'created_at', 'updated_at', 'title', 'context',
        'constraints', 'options', 'structured_decision', 'bias_report',
        'outcome_simulations', 'reflection_insight', 'actual_outcome',
        'actual_outcome_date', 'execution_log'
    ]
    
    print("\nChecking required columns:")
    for col_name in required_columns:
        assert col_name in columns, f"Missing column: {col_name}"
        col = columns[col_name]
        print(f"  ✓ {col_name}: {col.type}")
    
    # Check primary key
    pk_columns = [col.name for col in Decision.__table__.primary_key.columns]
    print(f"\n✓ Primary key: {pk_columns}")
    assert pk_columns == ['id']
    
    # Check indexes
    indexes = Decision.__table__.indexes
    print(f"\n✓ Indexes: {len(indexes)}")
    for idx in indexes:
        print(f"  - {idx.name}: {[col.name for col in idx.columns]}")
    
    # Check JSONB columns
    jsonb_columns = ['structured_decision', 'bias_report', 'outcome_simulations', 
                     'reflection_insight', 'execution_log']
    print("\nChecking JSONB columns:")
    for col_name in jsonb_columns:
        col = columns[col_name]
        print(f"  ✓ {col_name}: {type(col.type).__name__}")
        assert isinstance(col.type, postgresql.JSONB), f"{col_name} should be JSONB"
    
    # Check UUID column
    print("\nChecking UUID column:")
    id_col = columns['id']
    print(f"  ✓ id: {type(id_col.type).__name__}")
    assert isinstance(id_col.type, postgresql.UUID), "id should be UUID"
    
    # Check ARRAY columns
    array_columns = ['constraints', 'options']
    print("\nChecking ARRAY columns:")
    for col_name in array_columns:
        col = columns[col_name]
        print(f"  ✓ {col_name}: {type(col.type).__name__}")
        assert hasattr(col.type, 'item_type'), f"{col_name} should be ARRAY"
    
    # Test model methods
    print("\nChecking model methods:")
    assert hasattr(Decision, 'to_dict'), "Missing to_dict method"
    print("  ✓ to_dict method exists")
    assert hasattr(Decision, 'has_reflection'), "Missing has_reflection property"
    print("  ✓ has_reflection property exists")
    
    # Generate CREATE TABLE statement
    print("\n" + "="*60)
    print("Generated CREATE TABLE statement:")
    print("="*60)
    from sqlalchemy.schema import CreateTable
    create_table = CreateTable(Decision.__table__).compile(dialect=postgresql.dialect())
    print(str(create_table))
    
    print("\n" + "="*60)
    print("✅ All tests passed! Decision model is correctly defined.")
    print("="*60)

if __name__ == "__main__":
    test_decision_model()
