# Raspberry, what's your IP?

This little Python script allows your Raspberry to communicate with you using a Telegram bot or by tweeting you its IP.

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
               last tweet. Will be saved in the config file

Bots:
  Parameters required for bots to activate. Each bot needs specific
  configuration

  --telegram   Enable Telegram bot
  --twitter    Enable Twitter bot

```

...

### WORK IN PROGRESS...