# ElastiCache Redis (Dev) — Terraform Module

This module provisions a single-node Redis ElastiCache cluster in private subnets within your VPC for development use.

---

## ✅ Requirements

- Terraform >= 1.3
- AWS CLI configured with credentials
- VPC, 2 private subnets, and security group already created

---

## 📦 Files

| File              | Purpose                                       |
|-------------------|-----------------------------------------------|
| `main.tf`         | Resources: Redis cluster, subnet group        |
| `variables.tf`    | Input variables                                |
| `outputs.tf`      | Outputs: Redis endpoint & port                |
| `terraform.tfvars`| Your input values for dev environment         |
| `backend.tf`      | Local backend configuration                   |

---

## ⚙️ Usage

```bash
cd infrastructure/elasticache/

# Initialize providers & modules
terraform init

# Check the plan
terraform plan

# Apply the infrastructure
terraform apply
