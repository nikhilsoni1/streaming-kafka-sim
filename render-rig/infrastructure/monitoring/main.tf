resource "aws_cloudwatch_log_group" "api_log_group" {
  name              = "/ecs/render-rig2-api"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "worker_log_group" {
  name              = "/ecs/render-rig2-worker"
  retention_in_days = 14
}
