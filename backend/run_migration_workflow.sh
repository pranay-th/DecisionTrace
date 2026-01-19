#!/bin/bash

# Database Migration Workflow Script
# This script demonstrates the complete migration workflow for Task 2.3

set -e  # Exit on error

echo "=========================================="
echo "DecisionTrace - Migration Workflow"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check if Docker is running
echo "Step 1: Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running${NC}"
    echo "Please start Docker Desktop and try again"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"
echo ""

# Step 2: Start PostgreSQL
echo "Step 2: Starting PostgreSQL..."
docker-compose up -d
echo -e "${YELLOW}⏳ Waiting for PostgreSQL to be ready...${NC}"
sleep 10

# Check if PostgreSQL is ready
if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL is ready${NC}"
else
    echo -e "${RED}✗ PostgreSQL failed to start${NC}"
    echo "Check logs with: docker-compose logs postgres"
    exit 1
fi
echo ""

# Step 3: Test connection
echo "Step 3: Testing database connection..."
if python test_pg_connection.py; then
    echo -e "${GREEN}✓ Connection successful${NC}"
else
    echo -e "${RED}✗ Connection failed${NC}"
    exit 1
fi
echo ""

# Step 4: Check migration status
echo "Step 4: Checking migration status..."
python -m alembic current
echo ""

# Step 5: Apply migration
echo "Step 5: Applying migration..."
if python -m alembic upgrade head; then
    echo -e "${GREEN}✓ Migration applied successfully${NC}"
else
    echo -e "${RED}✗ Migration failed${NC}"
    exit 1
fi
echo ""

# Step 6: Verify migration
echo "Step 6: Verifying migration..."
python test_migrations.py
echo ""

# Step 7: Test rollback
echo "Step 7: Testing rollback..."
echo -e "${YELLOW}Rolling back migration...${NC}"
if python -m alembic downgrade -1; then
    echo -e "${GREEN}✓ Rollback successful${NC}"
else
    echo -e "${RED}✗ Rollback failed${NC}"
    exit 1
fi
echo ""

# Step 8: Re-apply migration
echo "Step 8: Re-applying migration..."
if python -m alembic upgrade head; then
    echo -e "${GREEN}✓ Migration re-applied successfully${NC}"
else
    echo -e "${RED}✗ Re-apply failed${NC}"
    exit 1
fi
echo ""

# Step 9: Final verification
echo "Step 9: Final verification..."
python test_migrations.py
echo ""

# Summary
echo "=========================================="
echo -e "${GREEN}✓ All migration tests passed!${NC}"
echo "=========================================="
echo ""
echo "Migration Details:"
echo "  - Revision: 6425a63343f6"
echo "  - Description: Initial schema with decisions table"
echo "  - Table: decisions"
echo "  - Indexes: 2 (created_at, updated_at)"
echo ""
echo "Next Steps:"
echo "  1. Review migration file: alembic/versions/6425a63343f6_*.py"
echo "  2. Check database: psql decisiontrace"
echo "  3. Continue with Task 3.1: LLM Client Implementation"
echo ""
echo "To stop PostgreSQL:"
echo "  docker-compose down"
echo ""
