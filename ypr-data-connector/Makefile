.PHONY: install clean build publish

# Basic Config
PACKAGE = ypr-data-connector	# Pip installable package name
INTERNAL_PACKAGE = ypr_data_connector	# Python folder name (underscored)
DOMAIN = ypr-dockyard
REPOSITORY = pypi-cargo
REGION = us-east-1
DIST_DIR = dist

# Read version dynamically from __init__.py
PACKAGE_VERSION = $(shell grep '__version__' $(INTERNAL_PACKAGE)/__init__.py | sed -E 's/__version__ = ["'\''](.*)["'\'']/\1/')

# Artifact path
ASSET_FILE = $(DIST_DIR)/$(PACKAGE)-$(PACKAGE_VERSION).tar.gz

# Install editable locally
install:
	@echo "Installing package in editable mode..."
	pip install -e .

# Clean old artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/ dist/ *.egg-info
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name ".pytest_cache" -type d -exec rm -rf {} +
	find . -name ".mypy_cache" -type d -exec rm -rf {} +

# Build distribution
build: clean
	@echo "Building distribution artifacts..."
	python3 -m build

# Publish package to CodeArtifact using twine with live auth token
publish: build
	@echo "Checking tools..."
	@command -v aws >/dev/null 2>&1 || { echo >&2 "AWS CLI is not installed. Aborting."; exit 1; }
	@command -v twine >/dev/null 2>&1 || { echo >&2 "Twine is not installed. Aborting."; exit 1; }
	@echo "Fetching AWS CodeArtifact token..."
	$(eval AUTH_TOKEN := $(shell aws codeartifact get-authorization-token --domain $(DOMAIN) --region $(REGION) --duration-seconds 1800 --query authorizationToken --output text))
	$(eval REPO_ENDPOINT := $(shell aws codeartifact get-repository-endpoint --domain $(DOMAIN) --repository $(REPOSITORY) --format pypi --region $(REGION) --query repositoryEndpoint --output text))
	@echo "Publishing to CodeArtifact..."
	twine upload \
		--repository-url $(REPO_ENDPOINT) \
		-u aws \
		-p $(AUTH_TOKEN) \
		$(DIST_DIR)/*
