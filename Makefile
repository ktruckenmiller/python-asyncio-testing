develop:
	docker run -it --rm \
	-v ${PWD}:/work \
	-w /work \
	-e IAM_ROLE \
	-e AWS_DEFAULT_REGION=us-west-2 \
	python bash
