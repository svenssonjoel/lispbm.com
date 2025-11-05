
# searchable documentation based on the mark down files.

uses pandoc to generate HTML from md
uses pagefind to create an index of the HTML files.


## Custom filters

Add custom filters to the md documentation like this.
The html tags can be added verbatim into the md and pandoc will
just copy them over as is into the target html.

```
<div data-pagefind-filter="Section">List Operations</div>
<div>

### car
Returns the first element...

### cdr
Returns the rest...

</div>
```

