# pandoc cheatsheet.md -o cheatsheet.pdf \
#     --pdf-engine=xelatex \
#     --variable=geometry:margin=0.5in \
#     --variable=fontsize:8pt \
#     --variable=classoption:twocolumn \
#     --highlight-style=kate

pandoc cheatsheet.md -o cheatsheet.pdf \
    --pdf-engine=xelatex \
    --variable=geometry:margin=0.6in \
    --variable=fontsize:9pt \
    --highlight-style=tango \
    --variable=colorlinks:true
