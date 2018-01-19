# Homucifer

Homucifer is a bot that idles in a channel, checks the NickServ registration
time of each person that joins, and kicks those who have accounts newer than
a certain number of days.

## Installation

* Make sure you have Python 3 installed, as well as a C compiler for dateparser.

1. Create a virtualenv with e.g. `virtualenv --python=python3 venv`
2. Activate the virtualenv with e.g. `source venv/bin/activate`
3. Install the required python modules with `pip install -r requirements.txt`
4. Copy `config_example.json` to `config.json` and modify it

## License

The contents of this repository are licensed under the terms of the Apache 2
license, unless explicitly stated otherwise. See the `LICENSE` file in this
repository to learn more.
