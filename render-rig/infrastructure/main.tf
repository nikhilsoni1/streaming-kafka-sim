module "iam" {
  source = "./iam"
}

module "networking" {
  source = "./networking"
  vpc_id = var.vpc_id
}

module "alb" {
  source                       = "./alb"
  vpc_id                       = var.vpc_id
  render_rig2_api_subnet_id    = module.networking.render_rig2_api_subnet_id
  render_rig2_worker_subnet_id = module.networking.render_rig2_worker_subnet_id
  alb_sg_id                    = module.networking.render_rig2_alb_sg_id
}

module "ecs" {
  source             = "./ecs"
  image_uri          = "183295432811.dkr.ecr.us-east-1.amazonaws.com/render-rig2:latest"
  execution_role_arn = module.iam.ecs_task_execution_role_arn
  task_role_arn      = module.iam.render_rig2_task_role_arn
  env_ssm_path       = "/render_rig2/"
}

module "ecs_services" {
  source                                 = "./ecs_services"
  cluster_name                           = module.ecs.ecs_cluster_name
  api_task_definition_arn                = module.ecs.api_task_definition_arn
  worker_task_lookup_chart_registry_arn  = module.ecs.worker_task_lookup_chart_registry_arn
  worker_task_get_existing_chart_arn     = module.ecs.worker_task_get_existing_chart_arn
  worker_task_lookup_log_registry_arn    = module.ecs.worker_task_lookup_log_registry_arn
  worker_task_get_log_dispatch_chart_arn = module.ecs.worker_task_get_log_dispatch_chart_arn
  worker_task_store_log_chart_arn        = module.ecs.worker_task_store_log_chart_arn
  worker_task_all_arn                    = module.ecs.worker_task_all_arn

  subnet_ids = [
    module.networking.render_rig2_api_subnet_id,
    module.networking.render_rig2_worker_subnet_id
  ]

  api_security_group_id = module.networking.render_rig2_task_sg_id
  target_group_arn      = module.alb.target_group_arn

  api_desired_count = 1

  num_worker_store_log_chart        = 0
  num_worker_get_log_dispatch_chart = 0
  num_worker_lookup_log_registry    = 0
  num_worker_get_existing_chart     = 0
  num_worker_lookup_chart_registry  = 0

  num_worker_all = 1
}
