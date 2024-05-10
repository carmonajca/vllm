.PHONY: docker-build

docker-build:
	export $$(cat .env | xargs) && \
		DOCKER_BUILDKIT=1 docker build . --target $${DOCKER_TARGET} --tag vllm/$${DOCKER_TARGET}


docker-run:
	export $$(cat .env | xargs) && \
		docker run -d --runtime nvidia --gpus all \
			--ipc=host \
			--env-file $${WORKING_DIR}/.env \
			-v $${HUGGING_FACE_DIR}:/root/.cache/huggingface \
			-v $${HUGGING_FACE_HUB_DIR}:/root/.cache/huggingface/hub \
			-v $${WORKING_DIR}:/vllm-workspace \
			-p 8000:8000 \
			vllm/$${DOCKER_TARGET}