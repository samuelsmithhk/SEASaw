[![Build Status](https://travis-ci.org/samuelsmithhk/SEASaw.svg?branch=master)](https://travis-ci.org/samuelsmithhk/SEASaw)

# SEASaw
SEASaw provides users the ability to textually-search for video based on the visual contents of the video.
## How to run

### Run without Scraper

#### Prerequisites

- clone of this repo
- (for database access) a valid credential file from us
- (for database access) a valid database password from us
- python 3.5, pip
- linux
- current working directory at root of repo
- chmod -x cloud_sql_proxy.amd64
- pip3 install -r requirements.txt --user
- nltk's tokenizer, stopwords, punctuations
    import nltk
    nltk.download('stopwords', '/home/vagrant/nltk_data')
    nltk.download('punkt', '/home/vagrant/nltk_data')

#### Command 1

python3 -m seasaw.start

This will launch the application in its simplest mode, allowing for you to use the frontend to search through existing data. Will require the below args to function fully.
##### Args

- --gca_credentials_path will need to be a path to the credential file
- --database_password for the database password

#### Command 2

python3 -m seasaw.scheduler

This command requires the previous one to be running, this will run the indexer.

##### Args

- --gca_credentials_path will need to be a path to the credential file
- --database_password for the database password

### Run with Scraper (can not run on linserv)

#### Prerequisites

- all previous prerequisites for running without scraper (except OS requirement), plus
- (for scraper to run) a valid imgur password from us
- hashicorp vagrant (to make life easier) - https://www.vagrantup.com/
- virtualbox (for vagrant)


#### Commands

- vagrant up
- vagrant ssh
- cd /vagrant
- python3 -m seasaw.start

Run the start with the following args:

##### Args

- --gca_credentials_path will need to be a path to the credential file
- --database_password for the database password
- --imgur_password with the imgur password
- -s to enable the scraper
- -l known as "local mode", ie, set all internal urls to work on the vagrant box.

**Commands (cont...)**

- python3 -m seasaw.scheduler

##### Args

- --gca_credentials_path will need to be a path to the credential file
- --database_password for the database password


If this is your first time running the project, vagrant up may take some time, as it will be downloading dependencies

**When finished, be sure to tear everything down with "vagrant halt", your battery will thank you.**

## View the front end

Once spinning, you will be able to access the frontend through port 25285 ("/")

## View the API docs

The API for the datasource can be found at port 25280 or 25281 ("/doc")
