resource "aws_ecs_cluster" "render_rig2_cluster" {
  name = "render-rig2-cluster"

  tags = {
    service = "render_rig2"
  }
}

resource "aws_ecs_task_definition" "api_task" {
  family                   = "render-rig2-api"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  network_mode             = "awsvpc"
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "ARM64"
  }

  container_definitions = jsonencode([
  {
    name      = "api",
    image     = var.image_uri,
    portMappings = [
      {
        containerPort = 8000,
        protocol      = "tcp"
      }
    ],
    command = [
      "uvicorn",
      "render_rig2.api.main:app",
      "--host", "0.0.0.0",
      "--port", "8000",
      "--reload"
    ],
    logConfiguration = {
      logDriver = "awslogs",
      options = {
        awslogs-group         = "/ecs/render-rig2-api",
        awslogs-region        = "us-east-1",
        awslogs-stream-prefix = "api"
      }
    },
    secrets = [
      { name = "AWS_DEFAULT_REGION", valueFrom = "/render_rig2/AWS_DEFAULT_REGION" },
      { name = "AWS_SECRET_ACCESS_KEY", valueFrom = "/render_rig2/AWS_SECRET_ACCESS_KEY" },
      { name = "LOG_REGISTRY_DB_HOST", valueFrom = "/render_rig2/LOG_REGISTRY_DB_HOST" },
      { name = "LOG_REGISTRY_DB_NAME", valueFrom = "/render_rig2/LOG_REGISTRY_DB_NAME" },
      { name = "LOG_REGISTRY_DB_PASS", valueFrom = "/render_rig2/LOG_REGISTRY_DB_PASS" },
      { name = "LOG_REGISTRY_DB_PORT", valueFrom = "/render_rig2/LOG_REGISTRY_DB_PORT" },
      { name = "LOG_REGISTRY_DB_SCMA", valueFrom = "/render_rig2/LOG_REGISTRY_DB_SCMA" },
      { name = "LOG_REGISTRY_DB_USER", valueFrom = "/render_rig2/LOG_REGISTRY_DB_USER" },
      { name = "REDIS_AWS_EP", valueFrom = "/render_rig2/REDIS_AWS_EP" },
      { name = "REDIS_DB_BACKEND", valueFrom = "/render_rig2/REDIS_DB_BACKEND" },
      { name = "REDIS_DB_BROKER", valueFrom = "/render_rig2/REDIS_DB_BROKER" },
      { name = "REDIS_HOST", valueFrom = "/render_rig2/REDIS_HOST" },
      { name = "REDIS_PORT", valueFrom = "/render_rig2/REDIS_PORT" },
      { name = "RENDER_RIG_CHARTS_BUCKET_NAME", valueFrom = "/render_rig2/RENDER_RIG_CHARTS_BUCKET_NAME" },
      { name = "RENDER_RIG_DB_HOST", valueFrom = "/render_rig2/RENDER_RIG_DB_HOST" },
      { name = "RENDER_RIG_DB_NAME", valueFrom = "/render_rig2/RENDER_RIG_DB_NAME" },
      { name = "RENDER_RIG_DB_PASS", valueFrom = "/render_rig2/RENDER_RIG_DB_PASS" },
      { name = "RENDER_RIG_DB_PORT", valueFrom = "/render_rig2/RENDER_RIG_DB_PORT" },
      { name = "RENDER_RIG_DB_USER", valueFrom = "/render_rig2/RENDER_RIG_DB_USER" }
    ],
    essential = true
  }
])

  tags = {
    service = "render_rig2"
  }
}

# lookup-chart-registry
resource "aws_ecs_task_definition" "worker_task_lookup_chart_registry" {
  family                   = "render-rig2-worker-lookup-chart-registry"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  network_mode             = "awsvpc"
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "ARM64"
  }

  container_definitions = jsonencode([
    {
      name      = "worker"
      image     = var.image_uri
      command = [
                  "celery", "-A", "render_rig2.app", "worker",
                  "-Q", "lookup_chart_registry",
                  "-c", "1",
                  "--loglevel=info"
                ]
      environment = []
      secrets = [
        { name = "AWS_DEFAULT_REGION", valueFrom = "/render_rig2/AWS_DEFAULT_REGION" },
        { name = "AWS_SECRET_ACCESS_KEY", valueFrom = "/render_rig2/AWS_SECRET_ACCESS_KEY" },
        { name = "LOG_REGISTRY_DB_HOST", valueFrom = "/render_rig2/LOG_REGISTRY_DB_HOST" },
        { name = "LOG_REGISTRY_DB_NAME", valueFrom = "/render_rig2/LOG_REGISTRY_DB_NAME" },
        { name = "LOG_REGISTRY_DB_PASS", valueFrom = "/render_rig2/LOG_REGISTRY_DB_PASS" },
        { name = "LOG_REGISTRY_DB_PORT", valueFrom = "/render_rig2/LOG_REGISTRY_DB_PORT" },
        { name = "LOG_REGISTRY_DB_SCMA", valueFrom = "/render_rig2/LOG_REGISTRY_DB_SCMA" },
        { name = "LOG_REGISTRY_DB_USER", valueFrom = "/render_rig2/LOG_REGISTRY_DB_USER" },
        { name = "REDIS_AWS_EP", valueFrom = "/render_rig2/REDIS_AWS_EP" },
        { name = "REDIS_DB_BACKEND", valueFrom = "/render_rig2/REDIS_DB_BACKEND" },
        { name = "REDIS_DB_BROKER", valueFrom = "/render_rig2/REDIS_DB_BROKER" },
        { name = "REDIS_HOST", valueFrom = "/render_rig2/REDIS_HOST" },
        { name = "REDIS_PORT", valueFrom = "/render_rig2/REDIS_PORT" },
        { name = "RENDER_RIG_CHARTS_BUCKET_NAME", valueFrom = "/render_rig2/RENDER_RIG_CHARTS_BUCKET_NAME" },
        { name = "RENDER_RIG_DB_HOST", valueFrom = "/render_rig2/RENDER_RIG_DB_HOST" },
        { name = "RENDER_RIG_DB_NAME", valueFrom = "/render_rig2/RENDER_RIG_DB_NAME" },
        { name = "RENDER_RIG_DB_PASS", valueFrom = "/render_rig2/RENDER_RIG_DB_PASS" },
        { name = "RENDER_RIG_DB_PORT", valueFrom = "/render_rig2/RENDER_RIG_DB_PORT" },
        { name = "RENDER_RIG_DB_USER", valueFrom = "/render_rig2/RENDER_RIG_DB_USER" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/render-rig2-worker"
          awslogs-region        = "us-east-1"
          awslogs-stream-prefix = "worker"
        }
      }
      essential = true
    }
  ])

  tags = {
    service = "render_rig2"
  }
}

# get-existing-chart
resource "aws_ecs_task_definition" "worker_task_get_existing_chart" {
  family                   = "render-rig2-worker-get-existing-chart"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  network_mode             = "awsvpc"
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "ARM64"
  }

  container_definitions = jsonencode([
    {
      name      = "worker"
      image     = var.image_uri
      command = [
        "celery", "-A", "render_rig2.app", "worker",
        "-Q", "get_existing_chart",
        "-c", "1",
        "--loglevel=info"
      ]
      environment = []
      secrets = [
        { name = "AWS_DEFAULT_REGION", valueFrom = "/render_rig2/AWS_DEFAULT_REGION" },
        { name = "AWS_SECRET_ACCESS_KEY", valueFrom = "/render_rig2/AWS_SECRET_ACCESS_KEY" },
        { name = "LOG_REGISTRY_DB_HOST", valueFrom = "/render_rig2/LOG_REGISTRY_DB_HOST" },
        { name = "LOG_REGISTRY_DB_NAME", valueFrom = "/render_rig2/LOG_REGISTRY_DB_NAME" },
        { name = "LOG_REGISTRY_DB_PASS", valueFrom = "/render_rig2/LOG_REGISTRY_DB_PASS" },
        { name = "LOG_REGISTRY_DB_PORT", valueFrom = "/render_rig2/LOG_REGISTRY_DB_PORT" },
        { name = "LOG_REGISTRY_DB_SCMA", valueFrom = "/render_rig2/LOG_REGISTRY_DB_SCMA" },
        { name = "LOG_REGISTRY_DB_USER", valueFrom = "/render_rig2/LOG_REGISTRY_DB_USER" },
        { name = "REDIS_AWS_EP", valueFrom = "/render_rig2/REDIS_AWS_EP" },
        { name = "REDIS_DB_BACKEND", valueFrom = "/render_rig2/REDIS_DB_BACKEND" },
        { name = "REDIS_DB_BROKER", valueFrom = "/render_rig2/REDIS_DB_BROKER" },
        { name = "REDIS_HOST", valueFrom = "/render_rig2/REDIS_HOST" },
        { name = "REDIS_PORT", valueFrom = "/render_rig2/REDIS_PORT" },
        { name = "RENDER_RIG_CHARTS_BUCKET_NAME", valueFrom = "/render_rig2/RENDER_RIG_CHARTS_BUCKET_NAME" },
        { name = "RENDER_RIG_DB_HOST", valueFrom = "/render_rig2/RENDER_RIG_DB_HOST" },
        { name = "RENDER_RIG_DB_NAME", valueFrom = "/render_rig2/RENDER_RIG_DB_NAME" },
        { name = "RENDER_RIG_DB_PASS", valueFrom = "/render_rig2/RENDER_RIG_DB_PASS" },
        { name = "RENDER_RIG_DB_PORT", valueFrom = "/render_rig2/RENDER_RIG_DB_PORT" },
        { name = "RENDER_RIG_DB_USER", valueFrom = "/render_rig2/RENDER_RIG_DB_USER" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/render-rig2-worker"
          awslogs-region        = "us-east-1"
          awslogs-stream-prefix = "worker"
        }
      }
      essential = true
    }
  ])

  tags = {
    service = "render_rig2"
  }
}

# lookup-log-registry
resource "aws_ecs_task_definition" "worker_task_lookup_log_registry" {
  family                   = "render-rig2-worker-lookup-log-registry"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  network_mode             = "awsvpc"
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "ARM64"
  }

  container_definitions = jsonencode([
    {
      name      = "worker"
      image     = var.image_uri
      command = [
        "celery", "-A", "render_rig2.app", "worker",
        "-Q", "lookup_log_registry",
        "-c", "1",
        "--loglevel=info"
      ]
      environment = []
      secrets = [
        { name = "AWS_DEFAULT_REGION", valueFrom = "/render_rig2/AWS_DEFAULT_REGION" },
        { name = "AWS_SECRET_ACCESS_KEY", valueFrom = "/render_rig2/AWS_SECRET_ACCESS_KEY" },
        { name = "LOG_REGISTRY_DB_HOST", valueFrom = "/render_rig2/LOG_REGISTRY_DB_HOST" },
        { name = "LOG_REGISTRY_DB_NAME", valueFrom = "/render_rig2/LOG_REGISTRY_DB_NAME" },
        { name = "LOG_REGISTRY_DB_PASS", valueFrom = "/render_rig2/LOG_REGISTRY_DB_PASS" },
        { name = "LOG_REGISTRY_DB_PORT", valueFrom = "/render_rig2/LOG_REGISTRY_DB_PORT" },
        { name = "LOG_REGISTRY_DB_SCMA", valueFrom = "/render_rig2/LOG_REGISTRY_DB_SCMA" },
        { name = "LOG_REGISTRY_DB_USER", valueFrom = "/render_rig2/LOG_REGISTRY_DB_USER" },
        { name = "REDIS_AWS_EP", valueFrom = "/render_rig2/REDIS_AWS_EP" },
        { name = "REDIS_DB_BACKEND", valueFrom = "/render_rig2/REDIS_DB_BACKEND" },
        { name = "REDIS_DB_BROKER", valueFrom = "/render_rig2/REDIS_DB_BROKER" },
        { name = "REDIS_HOST", valueFrom = "/render_rig2/REDIS_HOST" },
        { name = "REDIS_PORT", valueFrom = "/render_rig2/REDIS_PORT" },
        { name = "RENDER_RIG_CHARTS_BUCKET_NAME", valueFrom = "/render_rig2/RENDER_RIG_CHARTS_BUCKET_NAME" },
        { name = "RENDER_RIG_DB_HOST", valueFrom = "/render_rig2/RENDER_RIG_DB_HOST" },
        { name = "RENDER_RIG_DB_NAME", valueFrom = "/render_rig2/RENDER_RIG_DB_NAME" },
        { name = "RENDER_RIG_DB_PASS", valueFrom = "/render_rig2/RENDER_RIG_DB_PASS" },
        { name = "RENDER_RIG_DB_PORT", valueFrom = "/render_rig2/RENDER_RIG_DB_PORT" },
        { name = "RENDER_RIG_DB_USER", valueFrom = "/render_rig2/RENDER_RIG_DB_USER" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/render-rig2-worker"
          awslogs-region        = "us-east-1"
          awslogs-stream-prefix = "worker"
        }
      }
      essential = true
    }
  ])

  tags = {
    service = "render_rig2"
  }
}

# get-log-dispatch-chart
resource "aws_ecs_task_definition" "worker_task_get_log_dispatch_chart" {
  family                   = "render-rig2-worker-get-log-dispatch-chart"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "2048"
  memory                   = "4096"
  network_mode             = "awsvpc"
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "ARM64"
  }

  container_definitions = jsonencode([
    {
      name      = "worker"
      image     = var.image_uri
      command = [
        "celery", "-A", "render_rig2.app", "worker",
        "-Q", "get_log_dispatch_chart",
        "-c", "2",
        "--loglevel=info"
      ]
      environment = []
      secrets = [
        { name = "AWS_DEFAULT_REGION", valueFrom = "/render_rig2/AWS_DEFAULT_REGION" },
        { name = "AWS_SECRET_ACCESS_KEY", valueFrom = "/render_rig2/AWS_SECRET_ACCESS_KEY" },
        { name = "LOG_REGISTRY_DB_HOST", valueFrom = "/render_rig2/LOG_REGISTRY_DB_HOST" },
        { name = "LOG_REGISTRY_DB_NAME", valueFrom = "/render_rig2/LOG_REGISTRY_DB_NAME" },
        { name = "LOG_REGISTRY_DB_PASS", valueFrom = "/render_rig2/LOG_REGISTRY_DB_PASS" },
        { name = "LOG_REGISTRY_DB_PORT", valueFrom = "/render_rig2/LOG_REGISTRY_DB_PORT" },
        { name = "LOG_REGISTRY_DB_SCMA", valueFrom = "/render_rig2/LOG_REGISTRY_DB_SCMA" },
        { name = "LOG_REGISTRY_DB_USER", valueFrom = "/render_rig2/LOG_REGISTRY_DB_USER" },
        { name = "REDIS_AWS_EP", valueFrom = "/render_rig2/REDIS_AWS_EP" },
        { name = "REDIS_DB_BACKEND", valueFrom = "/render_rig2/REDIS_DB_BACKEND" },
        { name = "REDIS_DB_BROKER", valueFrom = "/render_rig2/REDIS_DB_BROKER" },
        { name = "REDIS_HOST", valueFrom = "/render_rig2/REDIS_HOST" },
        { name = "REDIS_PORT", valueFrom = "/render_rig2/REDIS_PORT" },
        { name = "RENDER_RIG_CHARTS_BUCKET_NAME", valueFrom = "/render_rig2/RENDER_RIG_CHARTS_BUCKET_NAME" },
        { name = "RENDER_RIG_DB_HOST", valueFrom = "/render_rig2/RENDER_RIG_DB_HOST" },
        { name = "RENDER_RIG_DB_NAME", valueFrom = "/render_rig2/RENDER_RIG_DB_NAME" },
        { name = "RENDER_RIG_DB_PASS", valueFrom = "/render_rig2/RENDER_RIG_DB_PASS" },
        { name = "RENDER_RIG_DB_PORT", valueFrom = "/render_rig2/RENDER_RIG_DB_PORT" },
        { name = "RENDER_RIG_DB_USER", valueFrom = "/render_rig2/RENDER_RIG_DB_USER" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/render-rig2-worker"
          awslogs-region        = "us-east-1"
          awslogs-stream-prefix = "worker"
        }
      }
      essential = true
    }
  ])

  tags = {
    service = "render_rig2"
  }
}

# store-log-chart
resource "aws_ecs_task_definition" "worker_task_store_log_chart" {
  family                   = "render-rig2-worker-store-log-chart"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  network_mode             = "awsvpc"
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "ARM64"
  }

  container_definitions = jsonencode([
    {
      name      = "worker"
      image     = var.image_uri
      command = [
        "celery", "-A", "render_rig2.app", "worker",
        "-Q", "store_log_chart",
        "-c", "1",
        "--loglevel=info"
      ]
      environment = []
      secrets = [
        { name = "AWS_DEFAULT_REGION", valueFrom = "/render_rig2/AWS_DEFAULT_REGION" },
        { name = "AWS_SECRET_ACCESS_KEY", valueFrom = "/render_rig2/AWS_SECRET_ACCESS_KEY" },
        { name = "LOG_REGISTRY_DB_HOST", valueFrom = "/render_rig2/LOG_REGISTRY_DB_HOST" },
        { name = "LOG_REGISTRY_DB_NAME", valueFrom = "/render_rig2/LOG_REGISTRY_DB_NAME" },
        { name = "LOG_REGISTRY_DB_PASS", valueFrom = "/render_rig2/LOG_REGISTRY_DB_PASS" },
        { name = "LOG_REGISTRY_DB_PORT", valueFrom = "/render_rig2/LOG_REGISTRY_DB_PORT" },
        { name = "LOG_REGISTRY_DB_SCMA", valueFrom = "/render_rig2/LOG_REGISTRY_DB_SCMA" },
        { name = "LOG_REGISTRY_DB_USER", valueFrom = "/render_rig2/LOG_REGISTRY_DB_USER" },
        { name = "REDIS_AWS_EP", valueFrom = "/render_rig2/REDIS_AWS_EP" },
        { name = "REDIS_DB_BACKEND", valueFrom = "/render_rig2/REDIS_DB_BACKEND" },
        { name = "REDIS_DB_BROKER", valueFrom = "/render_rig2/REDIS_DB_BROKER" },
        { name = "REDIS_HOST", valueFrom = "/render_rig2/REDIS_HOST" },
        { name = "REDIS_PORT", valueFrom = "/render_rig2/REDIS_PORT" },
        { name = "RENDER_RIG_CHARTS_BUCKET_NAME", valueFrom = "/render_rig2/RENDER_RIG_CHARTS_BUCKET_NAME" },
        { name = "RENDER_RIG_DB_HOST", valueFrom = "/render_rig2/RENDER_RIG_DB_HOST" },
        { name = "RENDER_RIG_DB_NAME", valueFrom = "/render_rig2/RENDER_RIG_DB_NAME" },
        { name = "RENDER_RIG_DB_PASS", valueFrom = "/render_rig2/RENDER_RIG_DB_PASS" },
        { name = "RENDER_RIG_DB_PORT", valueFrom = "/render_rig2/RENDER_RIG_DB_PORT" },
        { name = "RENDER_RIG_DB_USER", valueFrom = "/render_rig2/RENDER_RIG_DB_USER" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/render-rig2-worker"
          awslogs-region        = "us-east-1"
          awslogs-stream-prefix = "worker"
        }
      }
      essential = true
    }
  ])

  tags = {
    service = "render_rig2"
  }
}

# worker_all
resource "aws_ecs_task_definition" "worker_task_all" {
  family                   = "render-rig2-worker-all"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "2048"
  memory                   = "4096"
  network_mode             = "awsvpc"
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "ARM64"
  }

  container_definitions = jsonencode([
    {
      name      = "worker"
      image     = var.image_uri
      command = [
        "celery", "-A", "render_rig2.app", "worker",
        "-Q", "lookup_chart_registry,get_existing_chart,lookup_log_registry,get_log_dispatch_chart,store_log_chart",
        "-c", "4",
        "--loglevel=info"
      ]

      environment = []
      secrets = [
        { name = "AWS_DEFAULT_REGION", valueFrom = "/render_rig2/AWS_DEFAULT_REGION" },
        { name = "AWS_SECRET_ACCESS_KEY", valueFrom = "/render_rig2/AWS_SECRET_ACCESS_KEY" },
        { name = "LOG_REGISTRY_DB_HOST", valueFrom = "/render_rig2/LOG_REGISTRY_DB_HOST" },
        { name = "LOG_REGISTRY_DB_NAME", valueFrom = "/render_rig2/LOG_REGISTRY_DB_NAME" },
        { name = "LOG_REGISTRY_DB_PASS", valueFrom = "/render_rig2/LOG_REGISTRY_DB_PASS" },
        { name = "LOG_REGISTRY_DB_PORT", valueFrom = "/render_rig2/LOG_REGISTRY_DB_PORT" },
        { name = "LOG_REGISTRY_DB_SCMA", valueFrom = "/render_rig2/LOG_REGISTRY_DB_SCMA" },
        { name = "LOG_REGISTRY_DB_USER", valueFrom = "/render_rig2/LOG_REGISTRY_DB_USER" },
        { name = "REDIS_AWS_EP", valueFrom = "/render_rig2/REDIS_AWS_EP" },
        { name = "REDIS_DB_BACKEND", valueFrom = "/render_rig2/REDIS_DB_BACKEND" },
        { name = "REDIS_DB_BROKER", valueFrom = "/render_rig2/REDIS_DB_BROKER" },
        { name = "REDIS_HOST", valueFrom = "/render_rig2/REDIS_HOST" },
        { name = "REDIS_PORT", valueFrom = "/render_rig2/REDIS_PORT" },
        { name = "RENDER_RIG_CHARTS_BUCKET_NAME", valueFrom = "/render_rig2/RENDER_RIG_CHARTS_BUCKET_NAME" },
        { name = "RENDER_RIG_DB_HOST", valueFrom = "/render_rig2/RENDER_RIG_DB_HOST" },
        { name = "RENDER_RIG_DB_NAME", valueFrom = "/render_rig2/RENDER_RIG_DB_NAME" },
        { name = "RENDER_RIG_DB_PASS", valueFrom = "/render_rig2/RENDER_RIG_DB_PASS" },
        { name = "RENDER_RIG_DB_PORT", valueFrom = "/render_rig2/RENDER_RIG_DB_PORT" },
        { name = "RENDER_RIG_DB_USER", valueFrom = "/render_rig2/RENDER_RIG_DB_USER" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/render-rig2-worker"
          awslogs-region        = "us-east-1"
          awslogs-stream-prefix = "worker"
        }
      }
      essential = true
    }
  ])

  tags = {
    service = "render_rig2"
  }
}