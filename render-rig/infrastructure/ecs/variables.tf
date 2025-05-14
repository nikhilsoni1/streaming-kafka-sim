variable "image_uri" {
  description = "The ECR image URI"
  type        = string
}

variable "execution_role_arn" {
  description = "IAM role ARN for ECS task execution"
  type        = string
}

variable "task_role_arn" {
  description = "IAM role ARN for ECS task runtime permissions"
  type        = string
}

variable "env_ssm_path" {
  description = "SSM path to load environment variables from"
  type        = string
}
