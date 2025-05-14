#!/bin/bash

set -e

# Taint ECS resources to force recreation on next apply
RESOURCES=(
  "module.ecs.aws_ecs_task_definition.api_task"
  "module.ecs.aws_ecs_task_definition.worker_task"
  "module.ecs_services.aws_ecs_service.api_service"
  "module.ecs_services.aws_ecs_service.worker_service"
)

echo "Tainting ECS-related Terraform resources..."

for resource in "${RESOURCES[@]}"; do
  echo "Tainting $resource..."
  terraform taint "$resource" || echo "⚠️  Could not taint $resource (may not exist or already tainted)"
done

echo "Done."
