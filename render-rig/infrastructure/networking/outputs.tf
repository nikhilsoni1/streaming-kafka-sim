output "render_rig2_api_subnet_id" {
  description = "ID of the public subnet used by the API"
  value       = aws_subnet.render_rig2_api_subnet.id
}

output "render_rig2_worker_subnet_id" {
  description = "ID of the private subnet used by the worker"
  value       = aws_subnet.render_rig2_worker_subnet.id
}
