.PHONY: install clean build publish

# Config
PACKAGE = skyhawk
DOMAIN = ypr-dockyard
REPOSITORY = pypi-cargo
REGION = us-east-1   # <-- set your region
DIST_DIR = dist

# Dynamic version from skyhawk/__init__.py
PACKAGE_VERSION = $(shell grep '__version__' skyhawk/__init__.py | sed -E 's/__version__ = ["'\''](.*)["'\'']/\1/')

# Artifact path
ASSET_FILE = $(DIST_DIR)/$(PACKAGE)-$(PACKAGE_VERSION).tar.gz

# Install editable
install:
	pip install -e .

# Clean build artifacts
clean:
	rm -rf build/ dist/ *.egg-info
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name ".pytest_cache" -type d -exec rm -rf {} +
	find . -name ".mypy_cache" -type d -exec rm -rf {} +

# Build distribution
build: clean
	python3 -m build

# Publish using twine with live token injection
publish: build
	@echo "Publishing to CodeArtifact using live token..."
	$(eval AUTH_TOKEN := $(shell aws codeartifact get-authorization-token --domain $(DOMAIN) --region $(REGION) --query authorizationToken --output text))
	$(eval REPO_ENDPOINT := $(shell aws codeartifact get-repository-endpoint --domain $(DOMAIN) --repository $(REPOSITORY) --format pypi --region $(REGION) --query repositoryEndpoint --output text))
	twine upload \
		--repository-url $(REPO_ENDPOINT) \
		-u aws \
		-p $(AUTH_TOKEN) \
		$(DIST_DIR)/*
