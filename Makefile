# learn-codex-harness — task runner
# All demos are pure Python 3.8+ stdlib: no deps, no API key, no network.

PY ?= python3
DEMOS := $(sort $(wildcard lessons/s*/code.py))

.PHONY: help demo test list slides clean

help: ## Show this help
	@echo "Targets:"
	@grep -hE '^[a-z]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-8s\033[0m %s\n", $$1, $$2}'

demo: ## Run every lesson code.py in order, with headers
	@for f in $(DEMOS); do \
		echo ""; \
		echo "════════════════════════════════════════════════════════════"; \
		echo "  $$f"; \
		echo "════════════════════════════════════════════════════════════"; \
		$(PY) $$f || exit 1; \
	done
	@echo ""; echo "All demos ran. ✓"

test: ## Smoke-test that every demo exits 0 (no output)
	@fail=0; for f in $(DEMOS); do \
		$(PY) $$f >/dev/null 2>&1 && echo "  ok   $$f" || { echo "  FAIL $$f"; fail=1; }; \
	done; \
	[ $$fail -eq 0 ] && echo "All $(words $(DEMOS)) demos pass. ✓" || exit 1

list: ## List the lesson folders (the curriculum)
	@ls -d lessons/s*/ | sed 's#lessons/##; s#/##'

slides: ## Render the Marp deck to HTML (needs npx)
	npx @marp-team/marp-cli@latest slides/codex-harness.md -o slides/codex-harness.html

clean: ## Remove generated artifacts
	@rm -rf $$(find . -name __pycache__) slides/codex-harness.html slides/codex-harness.pdf
	@echo "cleaned"
