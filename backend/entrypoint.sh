#!/bin/sh
echo "Setting PYTHONPATH=/app"
export PYTHONPATH=/app
echo "PYTHONPATH=$PYTHONPATH"
echo "Python path:"
python -c "import sys; print('\n'.join(sys.path))"
echo "Attempting import..."
python -c "from backend.agents.system import AgentContext, orchestrate; print('Import OK')"
export PORT="${PORT:-8000}"
echo "Starting uvicorn with app object on port $PORT..."
exec python -c "
import os
import sys
sys.path.insert(0, '/app')
from backend.main import app
import uvicorn
uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
"