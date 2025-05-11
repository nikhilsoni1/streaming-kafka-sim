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