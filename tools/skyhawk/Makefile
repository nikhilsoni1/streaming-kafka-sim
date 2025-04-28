.PHONY: install build clean publish

# CodeArtifact settings
DOMAIN = ypr-dockyard
REPOSITORY = pypi-cargo
NAMESPACE = tools
PACKAGE = skyhawk

# Read version dynamically from skyhawk/__init__.py
PACKAGE_VERSION = $(shell grep '__version__' skyhawk/__init__.py | sed -E 's/__version__ = ["'\''](.*)["'\'']/\1/')

# Build artifact path
ASSET_FILE = dist/$(PACKAGE)-$(PACKAGE_VERSION).tar.gz

# Install skyhawk in editable mode
install:
	pip install -e .

# Clean build artifacts and cache
clean:
	rm -rf build/ dist/
	find . -name "*.egg-info" -type d -exec rm -rf {} +
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name ".pytest_cache" -type d -exec rm -rf {} +
	find . -name ".mypy_cache" -type d -exec rm -rf {} +

# Build fresh dist/ artifacts
build: clean
	python3 -m build

# Publish to AWS CodeArtifact
publish: build
	@echo "Calculating SHA256..."
	export ASSET_SHA256=$$(sha256sum $(ASSET_FILE) | awk '{print $$1;}') && \
	echo "Publishing package to AWS CodeArtifact..." && \
	aws codeartifact publish-package-version \
		--domain $(DOMAIN) \
		--repository $(REPOSITORY) \
		--format generic \
		--namespace $(NAMESPACE) \
		--package $(PACKAGE) \
		--package-version $(PACKAGE_VERSION) \
		--asset-content $(ASSET_FILE) \
		--asset-name $(notdir $(ASSET_FILE)) \
		--asset-sha256 $$ASSET_SHA256
