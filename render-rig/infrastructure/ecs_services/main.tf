resource "aws_ecs_service" "api_service" {
  name            = "render-rig2-api-service"
  cluster         = var.cluster_name
  task_definition = var.api_task_definition_arn
  desired_count   = var.api_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.subnet_ids
    security_groups = [var.api_security_group_id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = "api"
    container_port   = 8000
  }

  depends_on = [aws_ecs_service.worker_store_log_chart,
  aws_ecs_service.worker_get_log_dispatch_chart,
  aws_ecs_service.worker_lookup_log_registry,
  aws_ecs_service.worker_get_existing_chart,
  aws_ecs_service.worker_lookup_chart_registry
  ]

  tags = {
    service = "render_rig2"
  }
}

resource "aws_ecs_service" "worker_store_log_chart" {
  name            = "render-rig2-worker-store-log-chart"
  cluster         = var.cluster_name
  task_definition = var.worker_task_store_log_chart_arn
  desired_count   = var.num_worker_store_log_chart
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [var.subnet_ids[1]]
    assign_public_ip = true
  }

  tags = {
    service = "render_rig2"
  }
}

resource "aws_ecs_service" "worker_get_log_dispatch_chart" {
  name            = "render-rig2-worker-get-log-dispatch-chart"
  cluster         = var.cluster_name
  task_definition = var.worker_task_get_log_dispatch_chart_arn
  desired_count   = var.num_worker_get_log_dispatch_chart
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [var.subnet_ids[1]]
    assign_public_ip = true
  }

  tags = {
    service = "render_rig2"
  }
}

resource "aws_ecs_service" "worker_lookup_log_registry" {
  name            = "render-rig2-worker-lookup-log-registry"
  cluster         = var.cluster_name
  task_definition = var.worker_task_lookup_log_registry_arn
  desired_count   = var.num_worker_lookup_log_registry
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [var.subnet_ids[1]]
    assign_public_ip = true
  }

  tags = {
    service = "render_rig2"
  }
}

resource "aws_ecs_service" "worker_get_existing_chart" {
  name            = "render-rig2-worker-get-existing-chart"
  cluster         = var.cluster_name
  task_definition = var.worker_task_get_existing_chart_arn
  desired_count   = var.num_worker_get_existing_chart
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [var.subnet_ids[1]]
    assign_public_ip = true
  }

  tags = {
    service = "render_rig2"
  }
}

resource "aws_ecs_service" "worker_lookup_chart_registry" {
  name            = "render-rig2-worker-lookup-chart-registry"
  cluster         = var.cluster_name
  task_definition = var.worker_task_lookup_chart_registry_arn
  desired_count   = var.num_worker_lookup_chart_registry
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [var.subnet_ids[1]]
    assign_public_ip = true
  }

  tags = {
    service = "render_rig2"
  }
}

resource "aws_ecs_service" "worker_all" {
  name            = "render-rig2-worker-all"
  cluster         = var.cluster_name
  task_definition = var.worker_task_all_arn
  desired_count   = var.num_worker_all
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [var.subnet_ids[1]]
    assign_public_ip = true
  }

  tags = {
    service = "render_rig2"
  }
}
