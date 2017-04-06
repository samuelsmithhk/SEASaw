[![Build Status](https://travis-ci.org/samuelsmithhk/SEASaw.svg?branch=master)](https://travis-ci.org/samuelsmithhk/SEASaw)

# SEASaw
SEASaw provides users the ability to textually-search for video based on the visual contents of the video.
## How to run
The project is designed to be easily deployable anywhere.
#### Prerequisites

- git - https://git-scm.com/downloads
- hashicorp vagrant - https://www.vagrantup.com/
#### Steps

- clone this repo
- cd into the root directory of the repo
- run command "vagrant up"

If this is your first time running the project, it may take some time, as it will be downloading dependencies

**When finished, be sure to tear everything down with "vagrant halt", your battery will thank you.**

## How to use

Once SEASaw is up and running, there are three modes of use:

#### Searching our indexes
The simplest way to use SEASaw is to just search our indexes, to do this
navigate on your browser to *insert url when done* and begin searching

#### Expanding indexes
We have a limited set of data, you may wish to use our tools to expand the dataset. How to do this is available in the docs directory.

#### Creating a new data source
We are currently using Youtube as a datasource. You can create your own datasource by implementing a simple API. Description in the docs directory.