# Raspberry, what's your IP?

This little Python script allows your Raspberry to communicate with you using a Telegram bot or by tweeting you its IP. (Working for Windows and Linux in Python 2.7, not tested with >3.X)

 * Ability to use Telegram bot, Twitter bot or both at the same time (by command line)
 * Save your preferences in a config file


After using this, you won't need anymore to look into your DHCP leases or connecting a screen to get the IP.

```
python rpiwhatsyourip.py --help
usage: rpiwhatsyourip.py [-h] [-d] [--telegram] [--twitter] [--nrt]

optional arguments:
  -h, --help   show this help message and exit
  -d, --debug  Increase verbosity level
  --nrt        Do not tweet the current IP if it's the same as the one in the
               last tweet. Will be saved in the config file -> Recommended to avoid Twitter limits problems

Bots:
  Parameters required for bots to activate. Each bot needs specific
  configuration

  --telegram   Enable Telegram bot
  --twitter    Enable Twitter bot

```

## Set up
1. Upload the script to any folder (I uploaded it to /root)
2. You need to install `tweepy` and `pyTelegramBotAPI` libraries. Execute ```sudo pip install tweepy pyTelegramBotAPI```
3. Edit your /etc/rc.local file. You should place a line like: ` nohup python /path/to/rpiwhatsyourip.py [params...] & ` **Be careful**, you should place that before `exit 0`.
4. Execute `sudo chmod +x /path/to/rpiwhatsyourip.py`
5. If you reboot your system and the configuration file is correct, you should be able to communicate with your RPi using Telegram or Twitter.

## How to configure Telegram
1. In Telegram (you can do it in PC or in your phone) open a conversation with @Botfather
2. Create a /newbot (execute that command) and follow the steps
3. Copy the token you've received into rpiwhatsyourip.cfg
4. Open a conversation with your bot (for example, @my_rpi_bot)
5. Execute /yourip command (after turning on, you might need to send the command twice)

## How to configure Twitter
1. Create a new Twitter app (or use one if you have created it previously)
2. Access to your app desktop and click in 'Keys and Access tokens'
3. Copy the consumer keys and generate your access token by pressing the button at the bottom of the page
4. Paste them in your config file

Under MIT's License. Enjoy :P
