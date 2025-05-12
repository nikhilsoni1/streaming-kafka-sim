output "api_service_name" {
  description = "Name of the API ECS service"
  value       = aws_ecs_service.api_service.name
}

output "worker_service_name" {
  description = "Name of the worker ECS service"
  value       = aws_ecs_service.worker_service.name
}
