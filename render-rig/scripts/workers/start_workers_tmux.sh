#!/bin/bash

SESSION="celery-workers"
APP_PATH="render_rig2.app.celery_app"
CONCURRENCY=2
SET_ENV_CMD="source ./scripts/set-env.sh .env"
API_CMD="uvicorn render_rig2.api.main:app --reload"

# Queue names
QUEUES=(
  "lookup_chart_registry"
  "get_existing_chart"
  "lookup_log_registry"
  "get_log_dispatch_chart"
  "store_log_chart"
)

# Start a new tmux session
tmux new-session -d -s "$SESSION"

# Create a window for each Celery queue
for i in "${!QUEUES[@]}"; do
  QUEUE="${QUEUES[$i]}"
  WINDOW="worker_$QUEUE"

  if [ "$i" -eq 0 ]; then
    tmux rename-window -t "$SESSION:0" "$WINDOW"
  else
    tmux new-window -t "$SESSION:$i" -n "$WINDOW"
  fi

  CMD="$SET_ENV_CMD && celery -A $APP_PATH worker -Q $QUEUE --concurrency=$CONCURRENCY --loglevel=info"
  tmux send-keys -t "$SESSION:$i" "$CMD" C-m
done

# Add uvicorn server window
API_WINDOW="uvicorn"
tmux new-window -t "$SESSION:${#QUEUES[@]}" -n "$API_WINDOW"
tmux send-keys -t "$SESSION:$API_WINDOW" "$SET_ENV_CMD && $API_CMD" C-m

echo "✅ Celery workers and FastAPI started in tmux session: $SESSION"
echo "👉 Run this to attach: tmux attach-session -t $SESSION"
