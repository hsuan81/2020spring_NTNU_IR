import os

def split_searchfile(_file) -> list:
    """split the file and store different terms in a list and return the list. """
    answer = []
    dump = []
    for i in _file:
        print(i)
        term = i.split("\n")
        #print("trimfile: {name}".format(name=term))
        if len(dump) == 3:
            text = term[0].split(" ")
            text.remove("-1")
            #print(text)
            answer.extend(text)
        else:
            dump.append(term)
    return answer

# with open("SPLIT_DOC_WDID_NEW/VOM19980220.0700.0166") as d:
#     f = split_searchfile(d)

for root, dirs, files in os.walk("./SPLIT_DOC_WDID_NEW", topdown=False):
    for name in files:
        if name[0] == "V":
            with open(os.path.join(root, name), "r") as doc:
                f = split_searchfile(doc) 

    #         filename = folder + name
        #print(filename)
        # with open(filename, "r") as doc:
        #     f = split_searchfile(doc)
#         with open(os.path.join(root, name), "r", errors = "ignore") as doc:
#             f = split_searchfile(doc)
#             print(f)
    #for name in dirs:
        #print(os.path.join(root, name))
