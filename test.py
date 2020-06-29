import os
import dblp
import json
import time

## Constants
OUTPUT_DIR = './output'               # Output directory
MIN_PAGES = 3                         # Min pages for a paper
MATCH = ['DSN', 'FTCS']               # Venues considered
MATCH_DOI = ['DSN.{}', 'FTCS.{}']     # DOI considered (to filter out workshops)
RECENT = 2014                         # Year for recent papers

## Global Variables
authorList = {}


def get_recent_pubs(pubs):
    """
    Get the number of recent publications (using the `RECENT` constant as reference.
    Args:
        pubs: List of publications for the author.

    Returns:
        The number of publications that qualify as recent.
    """
    cc = 0
    for key in pubs:
        # in case the year has a suffix (e.g., LeeL17a)
        try:
            yyy = int(key[len(key) - 2:])
        except:
            yyy = int(key[len(key) - 3:len(key) - 1])
        yyy = yyy + 1900 if yyy > 50 else yyy + 2000
        if yyy >= RECENT:
            cc += 1
    return cc

def update_authors(pid, name, key):
    """
    Update the author list (`authorList`)
    Args:
        pid: Identifier of the author.
        name: Name of the author
        key: Key of the publication

    Returns:
        None
    """
    if pid in authorList:
        author = authorList[pid]
        author["pubs"].add(key)
        authorList[pid] = author
    else:
        author = {
            'name': name,
            'pubs': {key}
        }
        authorList[pid] = author


def filter_papers(pub, venue):
    """
    Filter out papers from the count (e.g., Industrial Track, Workshop papers, etc)
    Returns:
        True if the paper should be considered. False otherwise.
    """
    year = int(venue[len(venue)-4:])
    pags = 0

    # Check number of pages. Discard keynotes or abstract
    if 'pages' in pub:
        if '-' not in pub['pages']:
            pags = 1
        else:
            try:
                pages = pub['pages'].split('-')
                pags = int(pages[1]) - int(pages[0]) + 1
            except:
                # For some papers, pages does not include the finish page of the publication.
                pags = 99
    if pags < MIN_PAGES:
        return False

    # Filter out workshops, industry track, supplemental volume, etc
    if pub["venue"] in MATCH:
        # Papers from main conference can be distinguished by the doi. For example, a paper from a workshop has a doi
        # with DSN-W.YYYY, while the papers from the main conference has a doi with DSN.YYYY.
        # For some papers the doi is not available (e.g., https://dblp.uni-trier.de/rec/xml/conf/ftcs/HuangK93.xml)
        for doi in MATCH_DOI:
            try:
                if doi.format(year) in pub["doi"]:
                    return True
            except:
                return True

    return False

def get_authors(venue):
    """
    Save the author list (in `authorList`) who had accepted papers in the conference.
    Args:
        venue: venue to search. The venue follows this format /conf/XXX/YYYY, where XXX is the abbrev of the conf and
        YYYY correspond to the year of the conf.

    Returns:
        The number of publications (main conference) for the venue
    """
    papers=0
    results = dblp.search_pub(venue)

    hits = json.loads(results)["result"]["hits"]
    for i in hits["hit"]:
        info = i["info"]
        if  filter_papers(info, venue):
            papers+=1
            # print(info)
            if 'authors' in info:
                if isinstance(info["authors"]["author"], list):
                    for author in info["authors"]["author"]:
                        update_authors(author["@pid"], author["text"], info["key"])
                else:
                    author = info["authors"]["author"]
                    update_authors(author["@pid"], author["text"], info["key"])

    return papers

def usage():
    if not os.path.isdir(OUTPUT_DIR):
        if OUTPUT_DIR[0:2] == './':
            dir = OUTPUT_DIR[2:]
        else:
            dir = OUTPUT_DIR
        print("'{}' does not exists. Please create the directory.".format(dir))
        return False

    return True



def main():
    """
    Main Function
    Returns:

    """

    if not usage():
        exit(1)

    outFile = open(OUTPUT_DIR + '/dsnHOF-' + time.strftime("%Y%m%d-%H%M%S"), mode='a', encoding='utf-8')

    # FTCS (1988-1999)
    for year in range(1988,2000):
        print("Processing year {}: {}".format(year, get_authors("conf/ftcs/{}".format(year))))

    # DSN (2000-2019)
    for year in range(2000,2020):
        print("Processing year {}: {}".format(year, get_authors("conf/dsn/{}".format(year))))

    # get_authors("conf/ftcs/{}".format(1999))
    # get_authors("conf/ftcs/{}".format(1998))
    # get_authors("conf/ftcs/{}".format(1998))

    for pid in authorList:
        author = authorList[pid]
        author['total'] = len (author["pubs"])
        author['recent'] = get_recent_pubs(author["pubs"])
        authorList[pid] = author

        outFile.write("{}\t{}\t{}\t{}\n".format(author["name"], author["total"], author["recent"], author["pubs"]))

    outFile.flush()

    # Sort by total publications
    rank=1
    last_total=0
    i=1
    data = []
    for key, value in sorted(authorList.items(), key=lambda x : x[1]['total'], reverse=True):

        if i > 100 and last_total != value['total']:
            break

        if last_total != value['total']: rank = i
        print ('{} {} {} {} {} {}'.format(i, rank, value['name'], value['total'], value['recent'], dblp.get_affiliation(key, value['name'])))
        data.append({
            "anchor": "ranking",
            "num": i,
            "rank": rank,
            "author": value['name'],
            'total': value['total'],
            'recent': value['recent'],
            'affiliation': dblp.get_affiliation(key, value['name'])
        })

        i+=1
        last_total = value['total']

    with open('./ranking.json', mode='w', encoding='utf-8') as jsonFile:
        json.dump(data, jsonFile, indent=4)

if __name__ == '__main__':
    main()
