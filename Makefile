PI_IP_ADDRESS=192.168.12.42
PI_USERNAME=pi
SUBFOLDER="/projects"



.PHONY: copy
copy:
	@rsync -a $(shell pwd) --exclude env $(PI_USERNAME)@$(PI_IP_ADDRESS):/home/$(PI_USERNAME)$(SUBFOLDER)

.PHONY: shell
shell:
	@ssh $(PI_USERNAME)@$(PI_IP_ADDRESS)

.PHONY: install
install:
	@cd scripts && bash install.sh

.PHONY: build
build:
	@docker compose build

.PHONY: run
run:
	@docker compose up -d
