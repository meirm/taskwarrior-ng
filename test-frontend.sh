#!/bin/bash

# Frontend test script
echo "🧪 Testing TaskWarrior Frontend Application"
echo "==========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if servers are running
echo "1. Checking server health..."
API_HEALTH=$(curl -s http://localhost:8085/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} API Bridge is running on port 8085"
else
    echo -e "${RED}✗${NC} API Bridge is not responding"
    exit 1
fi

FRONTEND_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3033 2>/dev/null)
if [ "$FRONTEND_CHECK" == "200" ]; then
    echo -e "${GREEN}✓${NC} Frontend is running on port 3033"
else
    echo -e "${RED}✗${NC} Frontend is not responding"
    exit 1
fi

echo ""
echo "2. Testing API endpoints..."

# Test getting tasks
echo -n "   - GET /api/tasks: "
TASKS=$(curl -s http://localhost:8085/api/tasks | python3 -c "import sys, json; data=json.load(sys.stdin); print('OK' if data.get('success') else 'FAIL')" 2>/dev/null)
if [ "$TASKS" == "OK" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Test getting projects
echo -n "   - GET /api/projects: "
PROJECTS=$(curl -s http://localhost:8085/api/projects | python3 -c "import sys, json; data=json.load(sys.stdin); print('OK' if data.get('success') else 'FAIL')" 2>/dev/null)
if [ "$PROJECTS" == "OK" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Test getting tags
echo -n "   - GET /api/tags: "
TAGS=$(curl -s http://localhost:8085/api/tags | python3 -c "import sys, json; data=json.load(sys.stdin); print('OK' if data.get('success') else 'FAIL')" 2>/dev/null)
if [ "$TAGS" == "OK" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Test getting summary
echo -n "   - GET /api/summary: "
SUMMARY=$(curl -s http://localhost:8085/api/summary | python3 -c "import sys, json; data=json.load(sys.stdin); print('OK' if data.get('success') else 'FAIL')" 2>/dev/null)
if [ "$SUMMARY" == "OK" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

echo ""
echo "3. Testing task operations..."

# Create a test task
echo -n "   - Creating test task: "
TASK_ID=$(curl -s -X POST http://localhost:8085/api/tasks \
    -H "Content-Type: application/json" \
    -d '{"description": "Frontend test task", "priority": "M", "tags": ["test"]}' \
    | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['task']['id'] if data.get('success') and data.get('task') else 'FAIL')" 2>/dev/null)

if [ "$TASK_ID" != "FAIL" ] && [ ! -z "$TASK_ID" ]; then
    echo -e "${GREEN}✓${NC} (ID: $TASK_ID)"
    
    # Test completing the task
    echo -n "   - Completing task: "
    COMPLETE=$(curl -s -X POST http://localhost:8085/api/tasks/$TASK_ID/complete \
        | python3 -c "import sys, json; data=json.load(sys.stdin); print('OK' if data.get('success') else 'FAIL')" 2>/dev/null)
    if [ "$COMPLETE" == "OK" ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
    fi
else
    echo -e "${RED}✗${NC}"
fi

echo ""
echo "==========================================="
echo -e "${GREEN}Frontend testing complete!${NC}"
echo ""
echo "📝 Manual testing checklist:"
echo "   [ ] Visit http://localhost:3033"
echo "   [ ] Click 'Quick Add' button - should open task form"
echo "   [ ] Create a new task using the form"
echo "   [ ] Click on dashboard stat cards - should navigate to tasks with filters"
echo "   [ ] Edit an existing task"
echo "   [ ] Mark tasks as complete"
echo "   [ ] Use batch operations (select multiple tasks)"
echo "   [ ] Filter tasks by project or status"
echo "   [ ] Search for tasks"