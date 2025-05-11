
resource "aws_iam_policy" "ssm_access" {
  name = "RenderRig2SSMReadAccess"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath"
        ],
        Resource = "arn:aws:ssm:us-east-1:*:parameter/render_rig2/*"
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
