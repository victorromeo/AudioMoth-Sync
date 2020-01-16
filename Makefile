init:
	sudo apt-get update -y
	sudo apt-get upgrade -y
	sudo apt-get install python3 python3-pip -y
	sudo apt-get install pijuice-base -y
	sudo pip3 install -r requirements.txt

test:
	nose2 -v

.PHONY: init test