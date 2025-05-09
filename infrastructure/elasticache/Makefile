# Set defaults
TF_DIR := .
TFVARS := terraform.tfvars

init:
	cd $(TF_DIR) && terraform init

plan:
	cd $(TF_DIR) && terraform plan -var-file=$(TFVARS)

apply:
	cd $(TF_DIR) && terraform apply -var-file=$(TFVARS) -auto-approve

destroy:
	cd $(TF_DIR) && terraform destroy -var-file=$(TFVARS) -auto-approve

output:
	cd $(TF_DIR) && terraform output

# New: Plan what destroy will do (dry-run)
plan-destroy:
	cd $(TF_DIR) && terraform plan -destroy -var-file=$(TFVARS)

# New: Targeted destroy for Redis only
destroy-redis:
	cd $(TF_DIR) && terraform destroy \
	-target=aws_elasticache_cluster.redis \
	-target=aws_elasticache_subnet_group.redis_subnet_group \
	-var-file=$(TFVARS) -auto-approve

# Optional: Show outputs after plan-destroy
plan-destroy-output:
	cd $(TF_DIR) && terraform plan -destroy -var-file=$(TFVARS) && terraform output
