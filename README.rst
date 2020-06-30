DSN Hall of Fame Python scripts
================================
This repo contains the scripts needed to run and calculate the number of publications for the DSN Hall of Fame. Currently, this script has only been tested with Python 3.5. To run this script:

`python3.5 dsn-ranking.py`


About this Version
==============

This script is based on ISCA Hall of Fame Python scripts. The script queries DBLP for the authors of accepted papers from DSN (2000-2019) and FTCS (1988-1999) Conferences. Then, the script counts the number of publications for each author. However, abstracts (posters), keynotes, workshop papers, industry tracks papers are not included in the final count. The count is kept in a list, `authorList`, which is then sorted by the number of publications. The script generates two outputs: 1) a CSV file with the author details including a key identifying each publication counted (dsnHoF-YYYYMMDD-HHMMSS.csv);2) a JSON file with the final ranking (ranking.json).

Missing Features
================

- This version does not have support for authors with the same/similar names ("homonyms"). In the current version of the script, the number of publications are tally up according to the name of the author registered on DBLP. The script does not attempt to merge the number of publications across people with the same/similar names. In some cases, this leads to under-counting, because certain authors have multiple DBLP pages that should be merged (certain authors also sometimes have duplicate DBLP pages where the counts are identical across each variation). However, since there are legitimate cases of different authors with the same/similar name, merging their counts has the effect of misidentifying their contributions.

---------------------------------------------------------------------------------

The original dblp-python README is included below, for reference, since the ISCA Hall of Fame scripts build on it.

dblp-python
===========

A simple Python wrapper around the DBLP API, currently supporting author search and author and publication lookup.

Example
=======

Let's search for `Michael Ley`_, DBLP maintainer. Try ::

    >>> import dblp
    >>> #do a simple author search for michael ley
    >>> authors = dblp.search('michael ley')
    >>> michael = authors[0]
    >>> print michael.name
    Michael Ley
    >>> print len(michael.publications)
    31

If you'd like to learn more about Michael's work, you can explore his publications. All publication results are lazy-loaded, so have at it ::

   >>> print michael.publications[0].title
   DBLP - Some Lessons Learned.
   >>> print michael.publications[0].journal
   PVLDB
   >>> print michael.publications[0].year
   2009

More information about a publication can often be found at its `ee` URL - in this case, a link to the PDF ::

   >>> print michael.publications[0].ee
   http://www.vldb.org/pvldb/2/vldb09-98.pdf

Other publication and author attributes are documented with their respective classes- just use `help()`. Enjoy!

.. _Michael Ley: http://www.informatik.uni-trier.de/~ley/

Contributing
============

Contributions are very welcome! Feel free to fork the repo and request a pull, or open an issue if you find a bug or would like to request a feature.
