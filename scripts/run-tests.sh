#!/bin/bash
# =============================================================================
# Habit Tracker - Test Runner
# =============================================================================
# Usage:
#   ./scripts/run-tests.sh          # Run all tests
#   ./scripts/run-tests.sh -v       # Verbose output
#   ./scripts/run-tests.sh --fast   # Skip slow tests
#   ./scripts/run-tests.sh --clean  # Clean up test containers after
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
VERBOSE=""
FAST=""
CLEAN=false
PYTEST_ARGS=""

for arg in "$@"; do
    case $arg in
        -v|--verbose)
            VERBOSE="-v"
            ;;
        --fast)
            FAST="-m 'not slow'"
            ;;
        --clean)
            CLEAN=true
            ;;
        *)
            PYTEST_ARGS="$PYTEST_ARGS $arg"
            ;;
    esac
done

cd "$PROJECT_DIR"

echo -e "${BLUE}🧪 Habit Tracker Test Runner${NC}"
echo "================================"

# Step 1: Start test containers
echo -e "\n${YELLOW}📦 Starting test containers...${NC}"
docker compose -f docker-compose.test.yml up -d --build

# Step 2: Wait for health checks
echo -e "\n${YELLOW}⏳ Waiting for services to be healthy...${NC}"
MAX_WAIT=60
WAITED=0

until docker compose -f docker-compose.test.yml exec -T backend-test curl -sf http://localhost:8000/api/health > /dev/null 2>&1; do
    if [ $WAITED -ge $MAX_WAIT ]; then
        echo -e "${RED}❌ Timeout waiting for backend to be healthy${NC}"
        docker compose -f docker-compose.test.yml logs backend-test
        exit 1
    fi
    echo -n "."
    sleep 2
    WAITED=$((WAITED + 2))
done

echo -e "\n${GREEN}✅ All services healthy${NC}"

# Step 3: Run migrations on test DB
echo -e "\n${YELLOW}🔄 Running migrations on test database...${NC}"
docker compose -f docker-compose.test.yml exec -T backend-test alembic upgrade head

# Step 4: Run tests
echo -e "\n${YELLOW}🚀 Running tests...${NC}"
echo "================================"

# Build pytest command
PYTEST_CMD="python -m pytest tests/ $VERBOSE $FAST $PYTEST_ARGS --tb=short"

if docker compose -f docker-compose.test.yml exec -T backend-test $PYTEST_CMD; then
    echo -e "\n${GREEN}✅ All tests passed!${NC}"
    EXIT_CODE=0
else
    echo -e "\n${RED}❌ Some tests failed${NC}"
    EXIT_CODE=1
fi

# Step 5: Cleanup (optional)
if [ "$CLEAN" = true ]; then
    echo -e "\n${YELLOW}🧹 Cleaning up test containers...${NC}"
    docker compose -f docker-compose.test.yml down -v
    echo -e "${GREEN}✅ Cleanup complete${NC}"
else
    echo -e "\n${BLUE}ℹ️  Test containers still running. Stop with:${NC}"
    echo "   docker compose -f docker-compose.test.yml down -v"
fi

exit $EXIT_CODE
