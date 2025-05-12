# Makefile

AWS_REGION=us-east-1
ACCOUNT_ID=183295432811
REPO_NAME=render-rig2
IMAGE_TAG=latest
ECR_URL=$(ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(REPO_NAME)

.PHONY: all login build tag push

# Run the full flow: build → tag → push
all: build tag push

# Authenticate Docker to ECR
login:
	aws ecr get-login-password --region $(AWS_REGION) | \
	docker login --username AWS --password-stdin $(ECR_URL)

# Build the Docker image
build:
	docker build -t $(REPO_NAME) .

# Tag the Docker image for ECR
tag:
	docker tag $(REPO_NAME):$(IMAGE_TAG) $(ECR_URL):$(IMAGE_TAG)

# Push to ECR
push: login
	docker push $(ECR_URL):$(IMAGE_TAG)
