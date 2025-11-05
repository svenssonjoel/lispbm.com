
MD = $(wildcard *.md)
HTML = $(patsubst %.md,%.html,$(MD))

# Get current year for copyright
YEAR = $(shell date +%Y)

all: $(HTML) copy index

%.html: %.md
	@echo "Converting $< to HTML..."
	@# Extract title from first # heading in the markdown file
	@TITLE=$$(head -1 $< | sed 's/^# //'); \
	DESCRIPTION="LispBM Reference Documentation - $$TITLE"; \
	KEYWORDS="lispbm, lisp, reference, documentation, embedded lisp, microcontroller, $$TITLE"; \
	LINK="https://www.lispbm.com/lispbm-reference-manual/$$(basename $@ .html)/"; \
	(sed "s/###123###/$$TITLE/g;s/###456###/$$DESCRIPTION/g;s/###789###/$$KEYWORDS/g;s'###LINK###'$$LINK'g" pre.html; \
	 cat $<; \
	 sed "s/###YEAR###/$(YEAR)/g" post.html) | pandoc -f gfm -o $@
	@# Add pagefind filter attributes based on filename
	@BASENAME=$$(basename $< .md); \
	DOCNAME=$$(echo $$BASENAME | sed 's/-/ /g' | sed 's/\b\(.\)/\u\1/g'); \
	if echo "$<" | grep -q "vesc"; then \
	  sed -i "s|<div id=\"pagefind-platform\"></div>|<div data-pagefind-filter=\"Platform\">VESC</div>|" $@; \
	else \
	  sed -i "s|<div id=\"pagefind-platform\"></div>|<div data-pagefind-filter=\"Platform\">Core LispBM</div>|" $@; \
	fi; \
	sed -i "s|<div id=\"pagefind-document\"></div>|<div data-pagefind-filter=\"Document\">$$DOCNAME</div>|" $@

copy: $(HTML)
	@echo "Copying HTML files and CSS to output directory..."
	@mkdir -p ../html
	@cp $(HTML) ../html/
	@cp index.html ../html/
	@cp reference.css ../html/

index: copy
	@echo "Building search index with Pagefind..."
	@cd ../.. && npx -y pagefind --site lispbm-reference-manual/html

clean:
	rm -f $(HTML)
	rm -rf ../html

.PHONY: all clean copy index
