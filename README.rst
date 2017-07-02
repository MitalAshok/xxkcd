xxkcd
=====

An (unofficial) Python wrapper around xkcd APIs

Python 2 and 3 compatible. Requires an internet connection.

Examples
--------

For full usage, see the
`wiki <https://github.com/mitalashok/xxkcd/wiki>`__.

.. code:: python

    >>> from xxkcd import xkcd, WhatIf
    >>> x = xkcd(353)
    >>> x
    xkcd(353)
    >>> print(x.transcript)
    [[ Guy 1 is talking to Guy 2, who is floating in the sky ]]
    Guy 1: You're flying! How?
    Guy 2: Python!
    Guy 2: I learned it last night! Everything is so simple!
    Guy 2: Hello world is just 'print "Hello, World!" '
    Guy 1: I dunno... Dynamic typing? Whitespace?
    Guy 2: Come join us! Programming is fun again! It's a whole new world up here!
    Guy 1: But how are you flying?
    Guy 2: I just typed 'import antigravity'
    Guy 1: That's it?
    Guy 2: ...I also sampled everything in the medicine cabinet for comparison.
    Guy 2: But i think this is the python.
    {{ I wrote 20 short programs in Python yesterday.  It was wonderful.  Perl, I'm leaving you. }}
    >>> print(x.title)
    Python
    >>> print(x.alt)
    I wrote 20 short programs in Python yesterday.  It was wonderful.  Perl, I'm leaving you.
    >>> what_if = WhatIf(1)
    >>> print(what_if.title)
    Relativistic Baseball
    >>> print(what_if.question)
    What would happen if you tried to hit a baseball pitched at 90% the speed of light?
    >>> print(what_if.attribute)
    - Ellen McManis

.. code:: python

    from xxkcd import xkcd, WhatIf
    # Get random comic
    xkcd.random()
     
    # Get number of latest comic
    xkcd.latest()
     
    # Get random What If? article
    WhatIf.random()
     
    # Get number of latest What If? article
    WhatIf.latest()

Installing
----------

From `PyPI <https://pypi.org/project/xxkcd/>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    $ pip install xxkcd

From source
~~~~~~~~~~~

.. code:: bash

    $ git clone 'https://github.com/MitalAshok/xxkcd.git'
    $ python ./xxkcd/setup.py install
