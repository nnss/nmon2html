About:
------

This program takes a raw nmon file and makes some graphics for each metric/section,
but for AAA and BBBP, that are shown as text.

For the one time metrics (AAA and BBBP), this generates just info pages. For other
sections draws a graphic using HighCart. For the network, the write packages are
negative, so it's easier to see the reads and writes in the same graphic (there
is a red line in the 0)

By now, I have some ideas how to make a graphic of the TOP, but I need to work
a bit more on that idea and do some tests to see if I can manage to [re]present
the information correctly.

There are other alternatives, but for what I saw are a Excel macro, or some
other programs that need to be running. Parsing this file does not take too much
time or resources, and viewing this is also simple (any browser should work fine).


Background:
-----------

The idea of this program was originated while I was working at a previous job
I did something like this, but as I did not have that code, and I needed this
I made this again.


Author
------

Matias 'nnss' Palomec

ToDo
----

* make a template having "all in one" template file so no external links are used
* do the TOP section
* I should also redo the debug info, so them are more usable for others
* for the template, double-check the behaviour in more browsers

Known problems
----------------------

For the file systems metrics, I saw if there is something
new, the nmon will show it, but without redefining the 
headers, so new lines had more info, but are unknown.
There is no validation for that, but the JS part on the
html fails to make the chart.

Bugs and issues
---------------

Please, use the issue tracking on github