# Torchlight3 by [Botox](https://botox.bz/)

### Cs:source Server Requirements

* [custom sourcemod](https://github.com/Supreme-Elite/sourcemod/releases/tag/1.11.0.6512)
* [sm-ext-AsyncSocket](https://git.botox.bz/CSSZombieEscape/sm-ext-AsyncSocket) extension
* [smjansson extension](https://forums.alliedmods.net/showthread.php?t=184604)
* SMJSONAPI plugin (Private Blyat)
* [sm-ext-Voice](https://git.botox.bz/CSSZombieEscape/sm-ext-Voice) extension


## 1) Docker for PC Master Race🚀

## GeoIP2 if you build your custom docker image

### Installation
1. Download latest release version of GeoLite2 City.
2. Extract all files from the archive with replacement to your game server.
3. [Register on maxmind.com](https://www.maxmind.com/en/geolite2/signup) to be able to download databases or you can use alternative databases of mmdb format from [DB-API](https://db-ip.com/db).
4. Put database file to path to directory.

**Build**:

```docker build --rm --tag torchlight .```

### Start ready-to-use 💃

```docker run --net=host -d -v {your-torchlight-installation-files-blyat}:/home/torchlight --name torchlight supremeelite/torchlight3:latest```



 ##  2) Manual installation for boomer 👨‍🦳


### 0. Requirements

* Python3.6
* FFMPEG
* youtube-dl
* On game server:
* A brain 😁



  

## 1. Install

* Install python3 and python-virtualenv
* Create a virtualenv: `virtualenv venv`
* Activate the virtualenv: `. venv/bin/activate`
* Install all dependencies: `pip install -r requirements.txt`

  

## 2. Usage

Set up game server stuff.
Adapt config.json.

##### Make sure you are in the virtualenv! (`. venv/bin/activate`)

Run: `python main.py`
