
resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_policy_attachment" "ssm_policy_attach" {
  name       = "attach-ssm-to-render-task-role"
  roles      = [aws_iam_role.render_rig2_task_role.name]
  policy_arn = aws_iam_policy.ssm_access.arn
}

resource "aws_iam_policy_attachment" "s3_policy_attach" {
  name       = "attach-s3-to-render-task-role"
  roles      = [aws_iam_role.render_rig2_task_role.name]
  policy_arn = aws_iam_policy.s3_access.arn
}
