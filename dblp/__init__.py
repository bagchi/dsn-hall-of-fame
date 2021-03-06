import json
import requests
from lxml import etree
from collections import namedtuple

DBLP_BASE_URL = 'http://dblp.uni-trier.de/'
DBLP_AUTHOR_SEARCH_URL = DBLP_BASE_URL + 'search/author'
DBLP_AUTHOR_SEARCH_URL2 = DBLP_BASE_URL + 'search/author/api'
DBLP_PUBL_SEARCH_URL = DBLP_BASE_URL + 'search/publ/api'

DBLP_PERSON_URL = DBLP_BASE_URL + 'pers/xk/{urlpt}'
DBLP_PERSON_URL2 = DBLP_BASE_URL + 'pers/xx/{urlpt}'
# per DBLP staff, rec/conf/... instead of rec/bibtex/conf/... is the "new" format
DBLP_PUBLICATION_URL = DBLP_BASE_URL + 'rec/{key}.xml'

class LazyAPIData(object):
    def __init__(self, lazy_attrs):
        self.lazy_attrs = set(lazy_attrs)
        self.data = None

    def __getattr__(self, key):
        if key in self.lazy_attrs:
            if self.data is None:
                self.load_data()
            return self.data[key]
        raise AttributeError(key)

    def load_data(self):
        pass

class Author(LazyAPIData):
    """
    Represents a DBLP author. All data but the author's key is lazily loaded.
    Fields that aren't provided by the underlying XML are None.

    Attributes:
    name - the author's primary name record
    publications - a list of lazy-loaded Publications results by this author
    homepages - a list of author homepage URLs
    homonyms - a list of author aliases
    """
    def __init__(self, urlpt):
        self.urlpt = urlpt
        self.xml = None
        super(Author, self).__init__(['name','publications','homepages',
                                      'homonyms'])

    def load_data(self):
        timeoutCount = 0
        passFail = 0
        while (passFail == 0):
            try:
                resp = requests.get(DBLP_PERSON_URL.format(urlpt=self.urlpt))
                # TODO error handling
                xml = resp.content
                root = etree.fromstring(xml)
                data = {
                    'name':root.attrib['name'],
                    'publications':[Publication(k) for k in
                                    root.xpath('/dblpperson/dblpkey[not(@type)]/text()')],
                    'homepages':root.xpath(
                        '/dblpperson/dblpkey[@type="person record"]/text()'),
                    'homonyms':root.xpath('/dblpperson/homonym/text()')
                }

                self.data = data

                passFail = 1
            # if connection times out or string is empty, try again until it works or failed 5 times
            except:
                if (timeoutCount < 5):
                    passFail = 0
                    timeoutCount = timeoutCount + 1
                else:
                    print("ERROR: failed to connect to DBLP 5+ times for"+str(self.urlpt)+", skipping")
                    passFail = 1

def first_or_none(seq):
    try:
        return next(iter(seq))
    except StopIteration:
        pass

Publisher = namedtuple('Publisher', ['name', 'href'])
Series = namedtuple('Series', ['text','href'])
Citation = namedtuple('Citation', ['reference','label'])

class Publication(LazyAPIData):
    """
    Represents a DBLP publication- eg, article, inproceedings, etc. All data but
    the key is lazily loaded. Fields that aren't provided by the underlying XML
    are None.

    Attributes:
    type - the publication type, eg "article", "inproceedings", "proceedings",
    "incollection", "book", "phdthesis", "mastersthessis"
    sub_type - further type information, if provided- eg, "encyclopedia entry",
    "informal publication", "survey"
    title - the title of the work
    authors - a list of author names
    journal - the journal the work was published in, if applicable
    volume - the volume, if applicable
    number - the number, if applicable
    chapter - the chapter, if this work is part of a book or otherwise
    applicable
    pages - the page numbers of the work, if applicable
    isbn - the ISBN for works that have them
    ee - an ee URL
    crossref - a crossrel relative URL
    publisher - the publisher, returned as a (name, href) named tuple
    citations - a list of (text, label) named tuples representing cited works
    series - a (text, href) named tuple describing the containing series, if
    applicable
    """
    def __init__(self, key):
        self.key = key
        self.xml = None
        super(Publication, self).__init__( ['type', 'sub_type', 'mdate',
                'authors', 'editors', 'title', 'year', 'month', 'journal',
                'volume', 'number', 'chapter', 'pages', 'ee', 'isbn', 'url',
                'booktitle', 'crossref', 'publisher', 'school', 'citations',
                'series'])

    def load_data(self):
        timeoutCount2 = 0
        passFail2 = 0
        while (passFail2 == 0):
            try:
                resp = requests.get(DBLP_PUBLICATION_URL.format(key=self.key))

                xml = resp.content
                self.xml = xml
                root = etree.fromstring(xml)
                publication = first_or_none(root.xpath('/dblp/*[1]'))
                if publication is None:
                    raise ValueError
                data = {
                    'type':publication.tag,
                    'sub_type':publication.attrib.get('publtype', None),
                    'mdate':publication.attrib.get('mdate', None),
                    'authors':publication.xpath('author/text()'),
                    'editors':publication.xpath('editor/text()'),
                    'title':first_or_none(publication.xpath('title/text()')),
                    'year':int(first_or_none(publication.xpath('year/text()'))),
                    'month':first_or_none(publication.xpath('month/text()')),
                    'journal':first_or_none(publication.xpath('journal/text()')),
                    'volume':first_or_none(publication.xpath('volume/text()')),
                    'number':first_or_none(publication.xpath('number/text()')),
                    'chapter':first_or_none(publication.xpath('chapter/text()')),
                    'pages':first_or_none(publication.xpath('pages/text()')),
                    'ee':first_or_none(publication.xpath('ee/text()')),
                    'isbn':first_or_none(publication.xpath('isbn/text()')),
                    'url':first_or_none(publication.xpath('url/text()')),
                    'booktitle':first_or_none(publication.xpath('booktitle/text()')),
                    'crossref':first_or_none(publication.xpath('crossref/text()')),
                    'publisher':first_or_none(publication.xpath('publisher/text()')),
                    'school':first_or_none(publication.xpath('school/text()')),
                    'citations':[Citation(c.text, c.attrib.get('label',None))
                                 for c in publication.xpath('cite') if c.text != '...'],
                    'series':first_or_none(Series(s.text, s.attrib.get('href', None))
                                           for s in publication.xpath('series'))
                }

                self.data = data

                passFail2 = 1
            # if connection times out or string is empty, try again until it works or failed 5 times
            except:
                if (timeoutCount2 < 5):
                    passFail2 = 0
                    timeoutCount2 = timeoutCount2 + 1
                else:
                    print("ERROR: failed to connect to DBLP 5+ times for"+str(self.key)+", skipping")
                    passFail2 = 1

def search_pub(pub_str):
    timeOutCount3 = 0
    passFail3 = 0
    while (passFail3 == 0):
        try:
            resp = requests.get(DBLP_PUBL_SEARCH_URL, params={'q':pub_str, 'format': 'json', 'h': 1000})
            passFail3 = 1
        # if connection times out, try again until it works or failed 5 times
        except:
            if (timeoutCount3 < 5):
                passFail3 = 0
                timeoutCount3 = timeoutCount3 + 1
            else:
                print("ERROR: failed to connect to DBLP 5+ times for"+str(pub_str)+", skipping")
                passFail3 = 1

    return resp.text

def search(author_str):
    timeoutCount3 = 0
    passFail3 = 0
    while (passFail3 == 0):
        try:
            resp = requests.get(DBLP_AUTHOR_SEARCH_URL, params={'xauthor':author_str})
            passFail3 = 1
        # if connection times out, try again until it works or failed 5 times
        except:
            if (timeoutCount3 < 5):
                passFail3 = 0
                timeoutCount3 = timeoutCount3 + 1
            else:
                print("ERROR: failed to connect to DBLP 5+ times for"+str(author_str)+", skipping")
                passFail3 = 1

    #TODO: Does this need to be a nested try-catch above with the resp?
    #TODO: error handling
    root = etree.fromstring(resp.content)
    arr_of_authors = []
    for urlpt in root.xpath('/authors/author/@urlpt'):
        timeoutCount4 = 0
        passFail4 = 0
        while (passFail4 == 0):
            try:
                resp1 = requests.get(DBLP_PERSON_URL.format(urlpt=urlpt))

                xml = resp1.content
                root1 = etree.fromstring(xml)
                if root1.xpath('/dblpperson/homonym/text()'):
                    for hom_urlpt in root1.xpath('/dblpperson/homonym/text()'):
                        arr_of_authors.append(Author(hom_urlpt))
                else:
                    arr_of_authors.append(Author(urlpt))

                passFail4 = 1

            # if connection times out or string is empty, try again until it works or failed 5 times
            except:
                if (timeoutCount4 < 5):
                    passFail4 = 0
                    timeoutCount4 = timeoutCount4 + 1
                else:
                    print("ERROR: failed to connect to DBLP 5+ times for"+str(urlpt)+", skipping")
                    passFail4 = 1

    return arr_of_authors

def get_affiliation(pid, author_str):
    timeoutCount3 = 0
    passFail3 = 0
    # find all alias for the author
    while (passFail3 == 0):
        try:
            resp = requests.get(DBLP_AUTHOR_SEARCH_URL2, params={'q': author_str, 'format': 'json', 'h': 1000})
            passFail3 = 1
        # if connection times out, try again until it works or failed 5 times
        except:
            if (timeoutCount3 < 5):
                passFail3 = 0
                timeoutCount3 = timeoutCount3 + 1
            else:
                print("ERROR: failed to connect to DBLP 5+ times for" + str(author_str) + ", skipping")
                passFail3 = 1

    affiliation = None
    hits = json.loads(resp.text)["result"]["hits"]
    for hit in hits["hit"]:
        if "info" in hit:
            if "author" in hit["info"]:
                if "aliases" in hit["info"]:
                    for alias in hit["info"]["aliases"]["alias"]:
                        # print(alias)
                        pass

                # find pid -- which is on the url
                if "url" in hit["info"]:
                    if "https://dblp.org/pid" in hit["info"]["url"]:
                        xx = hit["info"]["url"][21:]
                        # print(xx)

                        if xx == pid:
                            if "notes" in hit["info"]:
                                note = hit["info"]["notes"]["note"]
                                # if the author has multiple notes
                                if isinstance(note, list):
                                    for text in note:
                                        if text["@type"] == "affiliation":
                                            affiliation = text["text"]
                                        # if there is more than one entry, we choose the first one
                                        if affiliation is not None: break

                                if "@type" in note:
                                    if note["@type"] == "affiliation":
                                        affiliation = note["text"]

                if affiliation is not None:
                    break

    return "" if affiliation is None else affiliation

def __get_affiliation(pid, author_str):
    timeoutCount3 = 0
    passFail3 = 0
    while (passFail3 == 0):
        try:
            resp = requests.get(DBLP_AUTHOR_SEARCH_URL, params={'xauthor':author_str})
            passFail3 = 1
        # if connection times out, try again until it works or failed 5 times
        except:
            if (timeoutCount3 < 5):
                passFail3 = 0
                timeoutCount3 = timeoutCount3 + 1
            else:
                print("ERROR: failed to connect to DBLP 5+ times for"+str(author_str)+", skipping")
                passFail3 = 1

    affiliation = None
    root = etree.fromstring(resp.content)
    for urlpt in root.xpath('/authors/author/@urlpt'):
        timeoutCount4 = 0
        passFail4 = 0

        # if we found an affiliation, break the cycle
        if affiliation is not None:
            break

        while (passFail4 == 0):
            try:
                resp = requests.get(DBLP_PERSON_URL2.format(urlpt=urlpt))
                if resp.status_code != 404:
                    # print(resp.text)
                    root2=etree.fromstring(resp.text)
                    xx = root2.attrib['pid']
                    if xx == pid:
                        affiliation = first_or_none(root2.xpath('/dblpperson/person/note[@type="affiliation"]/text()'))

                passFail4 = 1

            # if connection times out or string is empty, try again until it works or failed 5 times
            except:
                if (timeoutCount4 < 5):
                    passFail4 = 0
                    timeoutCount4 = timeoutCount4 + 1
                else:
                    print("ERROR: failed to connect to DBLP 5+ times for" + str(urlpt) + ", skipping")
                    passFail4 = 1

    return "" if affiliation is None else affiliation
    #
    #
    # affiliation = None
    # resp = requests.get(DBLP_PERSON_URL2.format(urlpt=pid))
    # if resp.status_code != 404:
    #     # print(resp.text)
    #     root = etree.fromstring(resp.text)
    #     affiliation = first_or_none(root.xpath('/dblpperson/person/note[@type="affiliation"]/text()'))
    #
    # return "" if affiliation is None else affiliation