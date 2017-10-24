# Antminer Monitor

Lite Python based Antminer Monitor !!!

  - Add as many miners as you want
  - Supports miners S7, S9, L3+ and D3
  - Check their hashrate, temperatures, fan speed, chip condition
  - Get in-app notifications about miner errors (needs refresh)
  - Log errors to file
  - Display total hashrate grouped by Model

### Screenshot

![Alt text](/app/static/images/screenshot_v0.0.3.png?raw=true "Screenshot v0.0.3")

### Installation

Antminer Monitor requires Flask to run.

Install the requirements and start the app.

```sh
$ pip install -r requirements.txt
$ python create_db.py
$ python run.py
```

