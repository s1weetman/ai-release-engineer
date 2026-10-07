.PHONY: demo-build demo-success demo-failure

DEMO_IMAGE ?= ai-release-engineer-demo:local

demo-build:
	docker build -f docker/mvp-demo.Dockerfile -t $(DEMO_IMAGE) .

demo-success: demo-build
	python -m ai_release_engineer.demo --scenario success --image $(DEMO_IMAGE)

demo-failure: demo-build
	python -m ai_release_engineer.demo --scenario validation-failure --image $(DEMO_IMAGE)
