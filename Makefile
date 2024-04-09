.DEFAULT_GOAL=help
.PHONY: build help
TARGET = src/sample.php


build: $(TARGET) ## Build the test case
	php -l '$(TARGET)'

help: ## Show this help
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'