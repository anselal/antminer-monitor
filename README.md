# Antminer Monitor [![follow on twitter][twitter]](https://twitter.com/intent/follow?screen_name=AntminerMonitor)

Lite Python based Antminer Monitor !!!

- Add as many miners as you want
- Supports miners A3, B3, D3, E3, L3, L3+, L3++, R4, S7, S9, S17, S17 Pro, T9, T9+, T17, V9, X3, Z9 mini, Z11
- Check their hashrate, temperatures, fan speed, chip condition, HW Error Rate, Uptime
- Get in-app notifications about miner errors (needs refresh)
- Log errors to file
- Display total hashrate grouped by Model
- Password protected login page

## Screenshot

![Alt text](/antminermonitor/static/images/screenshot_v0.5.0.png?raw=true "Screenshot v0.5.0")

### Requirements

- Antminer Monitor requires Python to run. Both Python2 and Python3 are supported !!!
- Mac and Linux users have Python installed by default on their system
- Windows users can download Python from <https://www.python.org>
`** ATTENTION **` While installing Python be sure to check `Add python.exe to Path` in the step `Customize Python`
If you don't select this option you will probably face some errors while installing the requirements

## Fresh Installation

1. Download the latest official release of #AntminerMonitor from <https://github.com/anselal/antminer-monitor/releases>
or the latest unofficial release from <https://github.com/anselal/antminer-monitor/archive/master.zip>
2. Unzip the downloaded file in a folder of your preference
3. Open a windows command prompt or a terminal and navigate to the folder where you unzipped the file using the `cd` command

   e.g. If you unzipped the file in the folder `C:\Users\foo\Downloads\antminer-monitor-master` type the following command and press \<Enter\>

   ```sh
   cd C:\Users\foo\Downloads\antminer-monitor-master
   ```

   > Your command prompt or terminal should now look like  `C:\Users\foo\Downloads\antminer-monitor-master>`

4. **This step apply only to *Mac* users**. If you are a Windows or Linux user continue to step 5.

   > Mac users should run all the commands with sudo eg. `sudo python get_pip.py`

   Install `pip` using __**one**__ of the following methods:

   4.1 Download `get-pip.py` from <https://bootstrap.pypa.io/get-pip.py> and save it inside `antminer-monitor-master`. Run the following command to install it:

      > It will ask for the administrator password. Type it and press \<Enter\>. While typing your password you won't see the characters on your screen. This is only for security measures.

      ```sh
      sudo python get_pip.py
      ```

   4.2 Install pip using `easy_install`. Again it may ask for the administrator password.

      ```sh
      sudo easy_install pip
      ```

5. Install requirements (Mac users don't forget `sudo`)

```sh
python -m pip install -r requirements.txt
python manage.py create-db
```

## Login Page

  1. Create admin user

```sh
python manage.py create-admin
```

Default creadentials are `username: admin` - `password: antminermonitor`. You can change the password from the settings menu.

## Run the app

 (Mac users don't forget `sudo`)

```sh
python manage.py run -h 0.0.0.0 -p 5000
```

Fire up a browser and point it to `http://localhost:5000` if you are running the app on the same machine OR `http://<ip>:5000` if you are accesing the app from another machine on the same network, by replacing `<ip>` with the machine's ip running AntminerMonitor.

Feel free to change the host (-h) and port (-p) parameters as needed by your setup.

You can set the host `(-h)` and port `(-p)` parameters in your .flaskenv file to avoid typing them when starting the app.

## Development vs. Production mode

AntminerMonitor runs by default in development mode, using Flask's development server. In development mode, this server provides an interactive debugger and will reload when code is changed.

To switch to production mode, edit `.flaskenv` and set `FLASK_ENV="production"`

## Run AntminerMonitor as a service (systemd)

Edit `antminermonitor.service` and adjust it properly to your environment

As root, run the following:

```sh
# Copy file service file to systemd's system folder
cp antminermonitor.service /etc/systemd/system/
# That’s it. We can now start the service:
systemctl start antminermonitor
# And automatically get it to start on boot
systemctl enable antminermonitor
```

## Donations

- BTC: `1HYCBovF6mqqKMyG4m2DQxXpdKmogK4Wuw`
- LTC: `LLrjq6nRokS74yPMspitHkXv4nLtEyebNW`
- DASH: `XuEnZtsCmWcDwKVe82wQddsfwUifXyeRoQ`
- ETH: `0x5bD8813Da5148fbc841bB18b9411fF72EdC8e10a`

[![paypal]](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=2AQ5RDGB5JVLW&source=url)

## Referral

- Get a Ledger Nano S and protect your cryptocurrencies

[![ledger]](https://www.ledgerwallet.com/r/3bf5?path=/products/ledger-nano-s&tracker=AntminerMonitor)

- Listen to your favorite radio stations and earn BRO cryptocurrency !!!

[![bitradio]](http://bitrad.io/?ref=59452)

- Get paid to search

[![presearch]](https://www.presearch.org/signup?rid=113267)

[twitter]: https://img.shields.io/twitter/follow/AntminerMonitor.svg?style=social
[paypal]: https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif
[ledger]: https://www.ledgerwallet.com/images/promo/nano-s/ledger_nano-s_7-2-8x9-0.jpg
[bitradio]: https://bitrad.io/images/BRO728x90.gif
[presearch]: https://www.presearch.org/images/rf/ban-4.jpg
