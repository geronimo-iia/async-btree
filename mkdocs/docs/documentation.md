# Documentation 

Note on documentation generation.

## Tooling

- mkdocs to generate web site
- pydocmd (based on mkdocs) to generate API doc from docstyle
- pyreverse to generate uml diagram

## Documentation folder

under mkdocs folder:

- 'docs' which keep handle writed doc file,
- 'docs/api' api generated files folder
- 'docs/uml' uml gererated diagrams folder
-  'mkdocs.yaml': configuration file for mkdocs tool

## Makefile targets


Main target: 'docs'

- call 'mkdocs-github-page'
    - call 'mkdocs-site':
        - call 'mkdocs-uml': Generate UML Diagram
        - call 'mkdocs-api': Generate API documentation
        - call 'mkdocs-md': Copy standard document
        - Build web site with mkdocs tool
    - move generated website content into '/docs' folder in order to expose with guthub page project
- call '.clean-docs' (Remove all temp files)
    

## Extract from Makefile

```

DOCS_PATH = "mkdocs/docs"

mkdocs-uml: # Generate UML Diagram
	@mkdir -p $(DOCS_PATH)/uml
	@$(RUN) pyreverse $(PACKAGE) -p $(PACKAGE) -a 1 -f ALL -o png --ignore tests
	- mv -f classes_$(PACKAGE).png $(DOCS_PATH)/uml/classes.png
	- mv -f packages_$(PACKAGE).png $(DOCS_PATH)/uml/packages.png

mkdocs-api: # Generate API documentation
	@mkdir -p $(DOCS_PATH)/api
	@cd $(DOCS_PATH)/api && \
		$(RUN) pydocmd simple async_btree.definition+ > definition.md && \
		$(RUN) pydocmd simple async_btree.analyze async_btree.stringify_analyze async_btree.Node > analyze.md && \
		$(RUN) pydocmd simple async_btree.analyze async_btree.control+ > control.md && \
		$(RUN) pydocmd simple async_btree.analyze async_btree.decorator+ > decorator.md  && \
		$(RUN) pydocmd simple async_btree.analyze async_btree.leaf+ > leaf.md && \
		$(RUN) pydocmd simple async_btree.analyze async_btree.parallele+ > parallele.md && \
		$(RUN) pydocmd simple async_btree.analyze async_btree.utils+ > utils.md

mkdocs-md: # Copy standard document
	@cp -f README.md $(DOCS_PATH)/index.md
	@cp -f LICENSE.md $(DOCS_PATH)/license.md
	@cp -f CHANGELOG.md $(DOCS_PATH)/changelog.md
	@cp -f CODE_OF_CONDUCT.md $(DOCS_PATH)/code_of_conduct.md

mkdocs-site: mkdocs-uml mkdocs-api mkdocs-md # Build Documentation Site
	@cd mkdocs && $(RUN) mkdocs build

mkdocs-github-page: mkdocs-site # Move generated docs under /docs
	@rm -rf docs/
	@mv mkdocs/site docs/

.clean-docs: # remove all generated files
	@rm -rf mkdocs/site
	@rm -rf $(DOCS_PATH)/uml
	@rm -rf $(DOCS_PATH)/api
	@rm -rf $(DOCS_PATH)/index.md
	@rm -rf $(DOCS_PATH)/license.md
	@rm -rf $(DOCS_PATH)/changelog.md
	@rm -rf $(DOCS_PATH)/code_of_conduct.md

.PHONY: docs
docs: mkdocs-github-page .clean-docs ## Generate documentation and UML

```
