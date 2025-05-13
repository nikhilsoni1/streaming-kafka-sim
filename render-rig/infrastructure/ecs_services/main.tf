resource "aws_ecs_service" "api_service" {
  name            = "render-rig2-api-service"
  cluster         = var.cluster_name
  task_definition = var.api_task_definition_arn
  desired_count   = var.api_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = [var.subnet_ids[0]]
    security_groups = [var.api_security_group_id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = "api"
    container_port   = 8000
  }

  depends_on = [aws_ecs_service.worker_service]

  tags = {
    service = "render_rig2"
  }
}

resource "aws_ecs_service" "worker_service" {
  name            = "render-rig2-worker-service"
  cluster         = var.cluster_name
  task_definition = var.worker_task_definition_arn
  desired_count   = var.worker_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [var.subnet_ids[1]]
    assign_public_ip = false
  }

  tags = {
    service = "render_rig2"
  }
}
