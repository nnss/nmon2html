About:
------

This this program takes a raw nmon file and makes some graphics for each metric.

For the one time metrics (AAA and BBBP), this generates just info pages. For other
sections draws a graphic using HighCart. For the network, the write packages are
negative, so it's easier to see the reads and writes in the same graphic (there
is a red line in the 0)

By now, I have some ideas how to make a graphic of the TOP, but I need to work
a bit more on that idea and do some tests to see if I can manage to [re]present
the information correctly.

ToDo
----

* make a template having "all in one" template file so no external links are used
* do the TOP section
* I should also redo the debug info, so them are more usable for others
* for the template, double-check the behaviour in more browsers


Background:
-----------

The idea of this program was originated while I was working at a previous job
I did something like this, but as I did not have that code, and I needed this
I made this again.


Author
------

Matias 'nnss' Palomec


Bugs and issues
---------------

Please, use the issue tracking on github