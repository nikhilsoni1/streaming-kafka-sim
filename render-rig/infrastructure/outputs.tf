output "render_rig2_api_subnet_id" {
  value = module.networking.render_rig2_api_subnet_id
}

output "render_rig2_worker_subnet_id" {
  description = "ID of the private subnet used by the worker"
  value       = module.networking.render_rig2_worker_subnet_id
}

output "render_rig2_alb_sg_id" {
  value = module.networking.render_rig2_alb_sg_id
}
