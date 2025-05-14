output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.render_rig2_cluster.name
}

output "api_task_definition_arn" {
  description = "ARN of the FastAPI ECS task definition"
  value       = aws_ecs_task_definition.api_task.arn
}

output "worker_task_lookup_chart_registry_arn" {
  description = "ARN of the Celery worker ECS task definition"
  value       = aws_ecs_task_definition.worker_task_lookup_chart_registry.arn
}

output "worker_task_get_existing_chart_arn" {
  description = "ARN of the Celery worker ECS task definition"
  value       = aws_ecs_task_definition.worker_task_get_existing_chart.arn
}

output "worker_task_lookup_log_registry_arn" {
  description = "ARN of the Celery worker ECS task definition"
  value       = aws_ecs_task_definition.worker_task_lookup_log_registry.arn
}

output "worker_task_get_log_dispatch_chart_arn" {
  description = "ARN of the Celery worker ECS task definition"
  value       = aws_ecs_task_definition.worker_task_get_log_dispatch_chart.arn
}

output "worker_task_store_log_chart_arn" {
  description = "ARN of the Celery worker ECS task definition"
  value       = aws_ecs_task_definition.worker_task_store_log_chart.arn
}
