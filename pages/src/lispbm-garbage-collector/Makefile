
MD = $(wildcard *.md)

HTML = $(patsubst %.md,%.html,$(MD))

DIR   = $(notdir $(CURDIR))
TITLE = Garbage Collection in LispBM
DESCRIPTION = A Walkthrough of the implementation of the garbage collector in lispBM
KEYWORDS = garbage collection, mark and sweep, memory management, lisp, lispbm, microcontroller, embedded gc, stm32, mcu 
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
