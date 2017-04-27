
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
for i in range(0,DATA_PARTITIONS):
    DATA_SERVERS.append('http://192.168.33.10:' + str(ports[i]))

INDEX_PARTITION = 2
INDEX_SERVERS = []
for i in range(0,INDEX_PARTITION):
    DATA_SERVERS.append('http://192.168.33.10:' + str(ports[DATA_PARTITIONS + i]))

FRONTEND_PARTITION = 2
FRONTEND_SERVERS = []
for i in range(0,FRONTEND_PARTITION):
    DATA_SERVERS.append('http://192.168.33.10:' + str(ports[DATA_PARTITIONS + INDEX_PARTITION + i]))

WEBAPP_PATH = "webapp/"