
resource "aws_iam_policy" "ssm_access" {
  name        = "RenderRig2SSMReadAccess"
  description = "Allow ECS tasks to read secrets from SSM Parameter Store"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "ssm:GetParameters",
          "ssm:GetParameter",
          "ssm:GetParametersByPath"
        ],
        Resource = "*"
      }
    ]
  })
}


resource "aws_iam_policy" "s3_access" {
  name = "RenderRig2S3Access"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ],
        Resource = [
          "arn:aws:s3:::flight-px4-logs",
          "arn:aws:s3:::flight-px4-logs/*"
        ]
      },
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ],
        Resource = [
          "arn:aws:s3:::flight-render-rig",
          "arn:aws:s3:::flight-render-rig/*"
        ]
      }
    ]
  })
}
