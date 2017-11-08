# Antminer Monitor

Lite Python based Antminer Monitor !!!

  - Add as many miners as you want
  - Supports miners S7, S9, L3+ and D3
  - Check their hashrate, temperatures, fan speed, chip condition, HW Error Rate, Uptime
  - Get in-app notifications about miner errors (needs refresh)
  - Log errors to file
  - Display total hashrate grouped by Model

### Screenshot

![Alt text](/app/static/images/screenshot_v0.1.1.png?raw=true "Screenshot v0.1.1")

### Requirements

  - Antminer Monitor requires Python2 to run
  - Mac and Linux users have Python2 installed by default on their system
  - Windows users can download Python2 from https://www.python.org/ftp/python/2.7.14/python-2.7.14.msi
  - Mac users must additionally download and install `get-pip.py` from https://bootstrap.pypa.io/get-pip.py

### Installation

Antminer Monitor requires Flask to run.

Install the requirements and start the app.

```sh
$ pip install -r requirements.txt
$ python create_db.py
$ python run.py
```

### Donations

  - BTC: `1HYCBovF6mqqKMyG4m2DQxXpdKmogK4Wuw`
  - LTC: `LLrjq6nRokS74yPMspitHkXv4nLtEyebNW`
  - DASH: `XuEnZtsCmWcDwKVe82wQddsfwUifXyeRoQ`