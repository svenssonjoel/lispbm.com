
MD = $(wildcard *.md)

HTML = $(patsubst %.md,%.html,$(MD))

DIR   = $(notdir $(CURDIR))
TITLE = Defunctionalization of a continuation-passing style evaluator
DESCRIPTION = Learn defunctionalization and continuation passing style (CPS) with a walkthrough of transforming a higher-order evaluator to first-order C code in LispBM.
KEYWORDS = lisp, lispbm, scheme, defunctionalization, defunctionalize, continuation passing style, CPS, evaluation, evaluator, higher order functions 
YEAR  = 2022
LINK  = https://www.lispbm.com/pages/$(DIR)/


all: $(HTML)

%.html: %.md

	(sed "s/###123###/$(TITLE)/g;s/###456###/$(DESCRIPTION)/g;s/###789###/$(KEYWORDS)/g;s'###LINK###'$(LINK)'g" ../pre.html; cat  $<; sed "s/###YEAR###/$(YEAR)/g" ../post.html) | pandoc -f gfm -o $@ 

	mkdir -p ../../$(DIR)
	mkdir -p ../../$(DIR)/media
	cp *.html ../../$(DIR) 
	cp ./media/* ../../$(DIR)/media || true

clean:
	rm *.html
