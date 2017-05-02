
ports = [
    25280,  # datasource
    25281,  # datasource
    25282,  # index server
    25283,  # index server
    25284,  # frontend
    25285,  # indexer
]

search_terms = [
    "puppy",
    "panda",
    "penguin",
    "polar bear",
    "kitten",
    "bunny",
    "elephant",
    "lion",
    "whale",
    "shark",
    "tortoise",
    "giraffe",
    "tiger",
    "monkey",
    "hippo",
    "badger",
    "bee",
    "ant",
    "fox",
    "dolphin",
    "koala",
    "snake",
    "pig",
    "cow",
    "sheep",
    "horse"
]

DATA_PARTITIONS = 2
DATA_SERVERS = []


INDEX_PARTITION = 2
INDEX_SERVERS = []


FRONTEND_PARTITION = 2
FRONTEND_SERVERS = []

WEBAPP_PATH = "webapp/"


def set_local():
    for i in range(0, DATA_PARTITIONS):
        DATA_SERVERS.append('http://192.168.33.10:' + str(ports[i]))

    for i in range(0, INDEX_PARTITION):
        INDEX_SERVERS.append('http://192.168.33.10:' + str(ports[DATA_PARTITIONS + i]))

    for i in range(0, FRONTEND_PARTITION):
        FRONTEND_SERVERS.append('http://192.168.33.10:' + str(ports[DATA_PARTITIONS + INDEX_PARTITION + i]))


def set_linserv():
    for i in range(0, DATA_PARTITIONS):
        DATA_SERVERS.append('http://linserv2.cims.nyu.edu:' + str(ports[i]))

    for i in range(0, INDEX_PARTITION):
        INDEX_SERVERS.append('http://linserv2.cims.nyu.edu:' + str(ports[DATA_PARTITIONS + i]))

    for i in range(0, FRONTEND_PARTITION):
        FRONTEND_SERVERS.append('http://linserv2.cims.nyu.edu:' + str(ports[DATA_PARTITIONS + INDEX_PARTITION + i]))