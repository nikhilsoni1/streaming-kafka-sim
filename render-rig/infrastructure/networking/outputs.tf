output "render_rig2_api_subnet_id" {
  description = "ID of the public subnet used by the API"
  value       = aws_subnet.render_rig2_api_subnet.id
}

output "render_rig2_worker_subnet_id" {
  description = "ID of the private subnet used by the worker"
  value       = aws_subnet.render_rig2_worker_subnet.id
}

output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = aws_internet_gateway.render_rig2_igw.id
}

output "api_sg_id" {
  description = "Security Group ID for the API service"
  value       = aws_security_group.render_rig2_alb_sg.id
}