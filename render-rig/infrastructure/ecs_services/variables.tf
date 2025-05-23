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

variable "worker_task_all_arn" {
  type = string
}

variable "num_worker_store_log_chart" {
    description = "Number of worker containers to store log chart"
    type        = number
    default     = 1
}

variable "num_worker_get_log_dispatch_chart" {
    description = "Number of worker containers to get log dispatch chart"
    type        = number
    default     = 1
}

variable "num_worker_lookup_log_registry" {
    description = "Number of worker containers to lookup log registry"
    type        = number
    default     = 1
}

variable "num_worker_get_existing_chart" {
    description = "Number of worker containers to get existing chart"
    type        = number
    default     = 1
}

variable "num_worker_lookup_chart_registry" {
    description = "Number of worker containers to lookup chart registry"
    type        = number
    default     = 1
}

variable "num_worker_all" {
    description = "Number of worker containers listening to all queues"
    type        = number
    default     = 1
}