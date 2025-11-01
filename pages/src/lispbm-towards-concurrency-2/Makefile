
MD = $(wildcard *.md)

HTML = $(patsubst %.md,%.html,$(MD))

DIR   = $(notdir $(CURDIR))
TITLE = Concurrent Tasks - Part 2 - Spawn an
DESCRIPTION = Implementation of spawn and wait for lispBM task
KEYWORDS = lisp concurrency, message passing, concurrent tasks, erlang style, actor model, lispbm, microcontrollers, stm32, esp32 
YEAR  = 2020
LINK  = https://www.lispbm.com/pages/$(DIR)/

all: $(HTML)

%.html: %.md

#(sed "s/###123###/$(TITLE)/g;s/###456###/$(DESCRIPTION)/g;s/###789###/$(KEYWORDS)/g" ../pre.html; cat  $<; sed "s/###YEAR###/$(YEAR)/g" ../post.html) | pandoc -f gfm -o $@ 
	(sed "s/###123###/$(TITLE)/g;s/###456###/$(DESCRIPTION)/g;s/###789###/$(KEYWORDS)/g;s'###LINK###'$(LINK)'g" ../pre.html; cat  $<; sed "s/###YEAR###/$(YEAR)/g" ../post.html) | pandoc -f gfm -o $@

	mkdir -p ../../$(DIR)
	mkdir -p ../../$(DIR)/media
	cp *.html ../../$(DIR) 
	cp ./media/* ../../$(DIR)/media || true

clean:
	rm *.html
