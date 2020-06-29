**Clean Needed**

ISCA Hall of Fame Python scripts
================================
This repo contains the scripts needed to run and calculate the number of publications, and years someone was a General/Program Chair, for the ISCA Hall of Fame.  Currently, this script has only been tested with Python 3.5.

To run the serial version of this script:

`python3.5 isca.py`

To run the parallel version of this script:

`python3.5 isca-parallel.py`

Serial Version
==============

This version of the script queries DBLP for each author, and counts how many of the author's papers on DBLP are ISCA papers.  However, abstracts ("posters"), keynote talks, and PC/GC Welcome papers (all of which DBLP counts as ISCA publications) are not included in the final counts.  Currently, the input list of authors is based on a deduplicated list of authors from the first 47 versions of ISCA (based on information provided by Mark Hill).  Moving forward, extensions are needed to this script to come up with a better, more automated list of authors.  This script could also easily be extended to check for other conferences, by changing the conference being checked for, or by adding an input argument to express this information.

After getting a count of the number of ISCA publications for each author, the script adds the <person, count> tuple to a list.  This list is sorted, then prints all authors with 8 or more ISCA publications, starting with the author with the most ISCA publications.

Since the DBLP website is not updated immediately when the conference proceedings are announced, there is a lag each year until DBLP has been updated.  Moreover, any issues with the data on DBLP should be fixed with the DBLP staff directly: https://dblp.dagstuhl.de/faq/1474623.html

In addition to counting the number of ISCA publications, this script also checks for ISCA publications that were written by the Program/General Chairs (PC/GC).  These publications are tracked separately and printed out separately.

Prior versions of dblp-python have added support for authors with the same/similar names ("homonyms").  In the current version of this script, I account for this by iterating over all authors with the same name and adding them separately to the list of authors with ISCA publications.  See "Missing Features" for some details about ways this part could be improved in the future.

I have also added support for handling errors due to timeouts when accessing the DBLP database.  Specifically, instead of throwing an error and failing immediately, if DBLP's database times out, the request will be retried 5 times before printing an error message and continuing.  This greatly improves the robustness of the script.

Parallel Version
================

I have also created a parallel version of this script (`isca-parallel.py`).  The main differences between the parallel version of the script and the serial version is that the parallel version runs one thread per core on the machine it is invoked on.  Moreover, to avoid races and have clean data output, each thread writes its results to a separate file.  This significantly reduces the runtime of the script, although it does require the use of locks in a few places because the underlying classes throw errors when multiple threads are populating their fields.  Some errors do occasionally happen with this version, where the string returned from DBLP is empty.  I suspect are related to additional accesses needing locks to avoid races, but I have not yet diagnosed the culprit.

Missing Features
================

Currently, there are several important features that are missing in this version of the script:

- Right now, the script does not attempt to merge the number of publications across people with the same/similar name.  In some cases, this leads to under-counting, because certain authors have multiple DBLP pages that should be merged (certain authors also sometimes have duplicate DBLP pages where the counts are identical across each variation).  I chose not to implement this feature, for now, because there are legitimately some authors with the same/similar name, and merging their counts has the effect of misidentifying their contributions.  However, in theory adding this feature is straightforward: search for authors in the list with the same name, then update that count instead of adding another entry.
- Support is needed to convert the total publication count into a list of numbers per year, which is how the Hall of Fame website displays the information.  For now, since the number of people in the Hall of Fame are small, I am doing this manually, but this is undesirable as it may introduce errors (and is more time intensive).
- It would likely improve the performance of the parallel version if the locking mechanism was moved into the __init__.py file, specifically around the calls that fetch information from DBLP and populate the fields.
- Although it would take up a lot of memory, it would likely make it simpler to produce per year paper counts if each author had a per-year array or list to populate, where index [0] was ISCA 1, [1] was ISCA 2, and so on.
- Alternatively, if changes to the underlying mechanism for lazily loading the DBLP database were added, this would remove the need for locks in some cases (and thus improve performance).

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
