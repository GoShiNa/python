"""     5/25/2017, 3:37 PM    """
__author__ = "Motti Javare Gowda G H"

import json, sys


def jsonRead(jsonFilename):
    try:
        with open(jsonFilename, 'r') as read:
            jsonData = json.load(read)
            return jsonData
    except IOError:
        print "Could not read a file:", jsonFilename
        sys.exit()


def jsonWrite(jsonFilename, data):
    try:
        with open(jsonFilename, 'w') as w:
            json.dump(data, w, sort_keys=False, indent=4,
                      ensure_ascii=False)
    except IOError:
        print "Could not write to a file:", jsonFilename
        sys.exit()


def deleteDictionaryKeys(adict, k):
    for key in adict.keys():
        try:
            if key == k:
                map(adict.pop, [k])
            elif type(adict[key]) is dict:
                deleteDictionaryKeys(adict[key], k)
            elif type(adict[key]) is list:
                for elm in adict[key]:
                    if k in elm:
                        del elm[k]
                        # map(adict.pop, [k])
                        #   final_dict = {key: t[key] for key in t if key not in [key1, key2]}
        except IOError as ex:
            print ex


if __name__ == '__main__':
    print 'Delete a Key-Value pair from a JSON Dictionary'
    adict = jsonRead('tenentInput.json')
    deleteKeys = ['county', 'tenants', 'id']
    for i in range(deleteKeys.__len__()):
        deleteDictionaryKeys(adict, deleteKeys[i])
    jsonWrite('tenentOutput.json', adict)
