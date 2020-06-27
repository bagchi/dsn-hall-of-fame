import dblp
import json
import time

match = ['DSN', 'DSN Workshop', 'FTCS']
authorList = {}
recent = 2014


def get_recent_pubs(pubs):
    cc = 0
    for key in pubs:
        # in case the year has a suffix (e.g., LeeL17a)
        try:
            yyy = int(key[len(key) - 2:])
        except:
            yyy = int(key[len(key) - 3:len(key) - 1])
        yyy = yyy + 1900 if yyy > 50 else yyy + 2000
        if yyy >= recent:
            cc += 1
    return cc

def update_authors(pid, name, key):
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


def get_authors(venue):
    papers=0
    results = dblp.search_pub(venue)

    hits = json.loads(results)["result"]["hits"]
    for i in hits["hit"]:
        info = i["info"]
        if info["venue"] in match:
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

def main():
    outFile = open('./output/dsnHOF-' + time.strftime("%Y%m%d-%H%M%S"), mode='a', encoding='utf-8')

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

def test():
    # person = "57/95, Saurabh Bagchi"
    print (dblp.get_affiliation("57/95", "Saurabh Bagchi"))
    #
    # if (len(currAuthors) > 1):
    #     print("    WARNING: " + person + " has multiple matches (" + str(len(currAuthors)) + ") in DBLP")
    #
    # for currAuthor in currAuthors:
    #     homepages = str(currAuthor.homepages)
    #     print("{} {} == {}".format(currAuthor.homepages, homepages[12:], person))
    #     print(currAuthor.affiliation)
    #     print(currAuthor.publications[0].school)


if __name__ == '__main__':
    main()
    # test()