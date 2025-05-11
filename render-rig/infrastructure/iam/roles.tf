
resource "aws_iam_role" "ecs_task_execution" {
  name = "ecsTaskExecutionRole-render_rig2"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    service = "render_rig2"
  }
}

resource "aws_iam_role" "render_rig2_task_role" {
  name = "renderRig2TaskRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    service = "render_rig2"
  }
}
