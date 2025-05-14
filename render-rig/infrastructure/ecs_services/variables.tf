variable "cluster_name" {
  description = "Name of the ECS cluster to run services in"
  type        = string
}

variable "api_task_definition_arn" {
  description = "ARN of the FastAPI ECS task definition"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs to run ECS tasks in"
  type        = list(string)
}

variable "api_security_group_id" {
  description = "Security group ID for FastAPI container"
  type        = string
}

variable "target_group_arn" {
  description = "Target group ARN for registering API service with ALB"
  type        = string
}

variable "api_desired_count" {
  description = "Number of API containers to run"
  type        = number
  default     = 2
}

variable "worker_desired_count" {
  description = "Number of worker containers to run"
  type        = number
  default     = 4
}

variable "worker_task_lookup_chart_registry_arn" {
  type = string
}

variable "worker_task_get_log_dispatch_chart_arn" {
  type = string
}

variable "worker_task_lookup_log_registry_arn" {
  type = string
}

variable "worker_task_get_existing_chart_arn" {
  type = string
}

variable "worker_task_store_log_chart_arn" {
  type = string
}