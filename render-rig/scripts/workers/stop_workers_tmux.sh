#!/bin/bash

SESSION="celery-workers"

echo "🛑 Killing tmux session: $SESSION"
tmux kill-session -t "$SESSION"
echo "✅ All workers and FastAPI server stopped"
