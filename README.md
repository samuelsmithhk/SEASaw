[![Build Status](https://travis-ci.org/samuelsmithhk/SEASaw.svg?branch=master)](https://travis-ci.org/samuelsmithhk/SEASaw)

# SEASaw
SEASaw provides users the ability to textually-search for video based on the visual contents of the video.
## How to run
The project is designed to be easily deployable anywhere.
#### Prerequisites

- git - https://git-scm.com/downloads
- virtualbox - https://www.virtualbox.org/wiki/VirtualBox
- hashicorp vagrant - https://www.vagrantup.com/
#### Steps

- clone this repo
- cd into the root directory of the repo
- run command "vagrant up"
- run command "vagrant ssh"
- cd into /vagrant
- run command: 
	python3 -m seasaw.start
	python3 -m seasaw.Indexer

If this is your first time running the project, vagrant up may take some time, as it will be downloading dependencies

**When finished, be sure to tear everything down with "vagrant halt", your battery will thank you.**

## Look at the APIs

With a running environment, you can hit one of the three provided interfaces:

Datasource API Doc - http://192.168.33.10:25280/doc

Index API Doc - http://192.168.33.10:25282/doc

Frontend API Doc - http://192.168.33.10:25284/doc