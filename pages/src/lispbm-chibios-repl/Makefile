
MD = $(wildcard *.md)

HTML = $(patsubst %.md,%.html,$(MD))

DIR   = $(notdir $(CURDIR))
TITLE = Implement a LispBM REPL in a ChibiOs Thread
DESCRIPTION = Example code on how to set up a REPL running in a ChibiOs Thread
KEYWORDS = chibios, stm32f4, stm32, repl, lisp, lispbm, microcontroller, embedded lisp, real time, threads, mcu 
YEAR  = 2020
LINK  = https://www.lispbm.com/pages/$(DIR)/

all: $(HTML)

%.html: %.md

#(sed "s/###123###/$(TITLE)/g;s/###456###/$(DESCRIPTION)/g;s/###789###/$(KEYWORDS)/g" ../pre.html; cat  $<; sed "s/###YEAR###/$(YEAR)/g" ../post.html) | pandoc -f gfm -o $@
	(sed "s/###123###/$(TITLE)/g;s/###456###/$(DESCRIPTION)/g;s/###789###/$(KEYWORDS)/g;s'###LINK###'$(LINK)'g" ../pre.html; cat  $<; sed "s/###YEAR###/$(YEAR)/g" ../post.html) | pandoc -f gfm -o $@ 

	mkdir -p ../../$(DIR)
	mkdir -p ../../$(DIR)/media
	cp *.html ../../$(DIR) 
	cp ./media/* ../../$(DIR)media || true

clean:
	rm *.html
