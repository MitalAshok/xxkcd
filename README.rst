xxkcd
=====

An (unofficial) Python wrapper around xkcd APIs

Examples
--------

For full usage, see the
`wiki <https://github.com/mitalashok/xxkcd/wiki>`__.

.. code:: python

    >>> from xxkcd import xkcd
    >>> x = xkcd(353)
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
