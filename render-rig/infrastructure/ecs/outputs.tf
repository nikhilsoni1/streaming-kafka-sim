output "api_task_definition_arn" {
  description = "ARN of the FastAPI ECS task definition"
  value       = aws_ecs_task_definition.api_task.arn
}

output "worker_task_definition_arn" {
  description = "ARN of the Celery worker ECS task definition"
  value       = aws_ecs_task_definition.worker_task.arn
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.render_rig2_cluster.name
}
