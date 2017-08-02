#!/usr/bin/python3
# -*- coding: utf-8 -*-
import asyncio
import os
import sys
import logging
import math
from .Utils import Utils, DataHolder
import traceback

class BaseCommand():
	Order = 0
	def __init__(self, torchlight):
		self.Logger = logging.getLogger(__class__.__name__)
		self.Torchlight = torchlight
		self.Triggers = []
		self.Level = 0

	async def _func(self, message, player):
		self.Logger.debug(sys._getframe().f_code.co_name)

### FILTER COMMANDS ###
class URLFilter(BaseCommand):
	Order = 1
	import re
	import aiohttp
	import magic
	import datetime
	import json
	import io
	from bs4 import BeautifulSoup
	from PIL import Image
	def __init__(self, torchlight):
		super().__init__(torchlight)
		self.Triggers = [self.re.compile(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''', self.re.IGNORECASE)]
		self.Level = -1
		self.re_youtube = self.re.compile(r'.*?(?:youtube\.com\/\S*(?:(?:\/e(?:mbed))?\/|watch\?(?:\S*?&?v\=))|youtu\.be\/)([a-zA-Z0-9_-]{6,11}).*?')

	async def URLInfo(self, url, yt = False):
		Info = None
		match = self.re_youtube.search(url)
		if match or yt:
			Temp = DataHolder()
			Time = None

			if Temp(url.find("&t=")) != -1 or Temp(url.find("?t=")) != -1 or Temp(url.find("#t=")) != -1:
				TimeStr = url[Temp.value + 3:].split('&')[0].split('?')[0].split('#')[0]
				if TimeStr:
					Time = Utils.ParseTime(TimeStr)

			Proc = await asyncio.create_subprocess_exec("youtube-dl", "--dump-json", "-xg", url,
				stdout = asyncio.subprocess.PIPE)
			Out, _ = await Proc.communicate()

			url, Info = Out.split(b'\n', maxsplit = 1)
			url = url.strip().decode("ascii")
			Info = self.json.loads(Info)

			if Info["extractor_key"] == "Youtube":
				self.Torchlight().SayChat("\x07E52D27[YouTube]\x01 {0} | {1} | {2}/5.00 | {3:,}".format(
					Info["title"], str(self.datetime.timedelta(seconds = Info["duration"])), round(Info["average_rating"], 2), int(Info["view_count"])))
			else:
				match = None

			url += "#t={0}".format(Time)

		else:
			try:
				async with self.aiohttp.ClientSession() as session:
					Response = await asyncio.wait_for(session.get(url), 5)
					if Response:
						ContentType = Response.headers.get("Content-Type")
						ContentLength = Response.headers.get("Content-Length")
						Content = await asyncio.wait_for(Response.content.read(65536), 5)

						if not ContentLength:
							ContentLength = -1

						if ContentType.startswith("text") and not ContentType.startswith("text/plain"):
							Soup = self.BeautifulSoup(Content.decode("utf-8", errors = "ignore"), "lxml")
							if Soup.title:
								self.Torchlight().SayChat("[URL] {0}".format(Soup.title.string))
						elif ContentType.startswith("image"):
							fp = self.io.BytesIO(Content)
							im = self.Image.open(fp)
							self.Torchlight().SayChat("[IMAGE] {0} | Width: {1} | Height: {2} | Size: {3}".format(im.format, im.size[0], im.size[1], Utils.HumanSize(ContentLength)))
							fp.close()
						else:
							Filetype = self.magic.from_buffer(bytes(Content))
							self.Torchlight().SayChat("[FILE] {0} | Size: {1}".format(Filetype, Utils.HumanSize(ContentLength)))

						Response.close()
			except Exception as e:
				self.Torchlight().SayChat("Error: {0}".format(str(e)))
				self.Logger.error(traceback.format_exc())

		self.Torchlight().LastUrl = url
		return url

	async def _rfunc(self, line, match, player):
		Url = match.groups()[0]
		if not Url.startswith("http") and not Url.startswith("ftp"):
			Url = "http://" + Url

		if line.startswith("!yt "):
			URL = await self.URLInfo(Url, True)
			return "!yt " + URL

		asyncio.ensure_future(self.URLInfo(Url))
		return -1

### FILTER COMMANDS ###

### LEVEL 0 COMMANDS ###
class Access(BaseCommand):
	def __init__(self, torchlight):
		super().__init__(torchlight)
		self.Triggers = ["!access", "!who", "!whois"]
		self.Level = 0

	def FormatAccess(self, player):
		Answer = "#{0} \"{1}\"({2}) is ".format(player.UserID, player.Name, player.UniqueID)
		Level = str(0)
		if player.Access:
			Level = str(player.Access["level"])
			Answer += "level {0!s} as {1}.".format(Level, player.Access["name"])
		else:
			Answer += "not authenticated."

		if Level in self.Torchlight().Config["AudioLimits"]:
			Uses = self.Torchlight().Config["AudioLimits"][Level]["Uses"]
			TotalTime = self.Torchlight().Config["AudioLimits"][Level]["TotalTime"]

			if Uses >= 0:
				Answer += " Uses: {0}/{1}".format(player.Storage["Audio"]["Uses"], Uses)
			if TotalTime >= 0:
				Answer += " Time: {0}/{1}".format(round(player.Storage["Audio"]["TimeUsed"], 2), round(TotalTime, 2))

		return Answer

	async def _func(self, message, player):
		self.Logger.debug(sys._getframe().f_code.co_name + ' ' + str(message))

		Count = 0
		if message[0] == "!access":
			if message[1]:
				return -1

			self.Torchlight().SayChat(self.FormatAccess(player))

		elif message[0] == "!who":
			for Player in self.Torchlight().Players:
				if Player.Name.lower().find(message[1].lower()) != -1:
					self.Torchlight().SayChat(self.FormatAccess(Player))

					Count += 1
					if Count >= 3:
						break

		elif message[0] == "!whois":
			for UniqueID, Access in self.Torchlight().Access:
				if Access["name"].lower().find(message[1].lower()) != -1:
					Player = self.Torchlight().Players.FindUniqueID(UniqueID)
					if Player:
						self.Torchlight().SayChat(self.FormatAccess(Player))
					else:
						self.Torchlight().SayChat("#? \"{0}\"({1}) is level {2!s} is currently offline.".format(Access["name"], UniqueID, Access["level"]))

					Count += 1
					if Count >= 3:
						break
		return 0

class Calculate(BaseCommand):
	import urllib.parse
	import aiohttp
	import json
	def __init__(self, torchlight):
		super().__init__(torchlight)
		self.Triggers = ["!c"]
		self.Level = 0

	async def Calculate(self, Params):
		async with self.aiohttp.ClientSession() as session:
			Response = await asyncio.wait_for(session.get("http://math.leftforliving.com/query", params=Params), 5)
			if not Response:
				return 1

			Data = await asyncio.wait_for(Response.json(content_type = "text/json"), 5)
			if not Data:
				return 2

		if not Data["error"]:
			self.Torchlight().SayChat(Data["answer"])
			return 0

	async def _func(self, message, player):
		self.Logger.debug(sys._getframe().f_code.co_name + ' ' + str(message))
		Params = dict({"question": message[1]})
		Ret = await self.Calculate(Params)
		return Ret

class WolframAlpha(BaseCommand):
	import urllib.parse
	import aiohttp
	import xml.etree.ElementTree as etree
	import re
	def __init__(self, torchlight):
		super().__init__(torchlight)
		self.Triggers = ["!cc"]
		self.Level = 0

	def Clean(self, Text):
		return self.re.sub("[ ]{2,}", " ", Text.replace(' | ', ': ').replace('\n', ' | ').replace('~~', ' ≈ ')).strip()

	async def Calculate(self, Params):
		async with self.aiohttp.ClientSession() as session:
			Response = await asyncio.wait_for(session.get("http://api.wolframalpha.com/v2/query", params=Params), 10)
			if not Response:
				return 1

			Data = await asyncio.wait_for(Response.text(), 5)
			if not Data:
				return 2

		Root = self.etree.fromstring(Data)


		# Find all pods with plaintext answers
		# Filter out None -answers, strip strings and filter out the empty ones
		Pods = list(filter(None, [p.text.strip() for p in Root.findall('.//subpod/plaintext') if p is not None and p.text is not None]))

		# no answer pods found, check if there are didyoumeans-elements
		if not Pods:
			Didyoumeans = Root.find("didyoumeans")
			# no support for future stuff yet, TODO?
			if not Didyoumeans:
				# If there's no pods, the question clearly wasn't understood
				self.Torchlight().SayChat("Sorry, couldn't understand the question.")
				return 3

			Options = []
			for Didyoumean in Didyoumeans:
				Options.append("\"{0}\"".format(Didyoumean.text))
			Line = " or ".join(Options)
			Line = "Did you mean {0}?".format(Line)
			self.Torchlight().SayChat(Line)
			return 0

		# If there's only one pod with text, it's probably the answer
		# example: "integral x²"
		if len(Pods) == 1:
			Answer = self.Clean(Pods[0])
			self.Torchlight().SayChat(Answer)
			return 0

		# If there's multiple pods, first is the question interpretation
		Question = self.Clean(Pods[0].replace(' | ', ' ').replace('\n', ' '))
		# and second is the best answer
		Answer = self.Clean(Pods[1])
		self.Torchlight().SayChat("{0} = {1}".format(Question, Answer))
		return 0

	async def _func(self, message, player):
		self.Logger.debug(sys._getframe().f_code.co_name + ' ' + str(message))
		Params = dict({"input": message[1], "appid": self.Torchlight().Config["WolframAPIKey"]})
		Ret = await self.Calculate(Params)
		return Ret

class WUnderground(BaseCommand):
	import aiohttp
	def __init__(self, torchlight):
		super().__init__(torchlight)
		self.Triggers = ["!w"]
		self.Level = 0

	async def _func(self, message, player):
		if not message[1]:
			# Use IP address
			Search = "autoip"
			Additional = "?geo_ip={0}".format(player.Address.split(":")[0])
		else:
			async with self.aiohttp.ClientSession() as session:
				Response = await asyncio.wait_for(session.get("http://autocomplete.wunderground.com/aq?format=JSON&query={0}".format(message[1])), 5)
				if not Response:
					return 2

				Data = await asyncio.wait_for(Response.json(), 5)
				if not Data:
					return 3

			if not Data["RESULTS"]:
				self.Torchlight().SayPrivate(player, "[WU] No cities match your search query.")
				return 4

			Search = Data["RESULTS"][0]["name"]
			Additional = ""

		async with self.aiohttp.ClientSession() as session:
			Response = await asyncio.wait_for(session.get("http://api.wunderground.com/api/{0}/conditions/q/{1}.json{2}".format(
				self.Torchlight().Config["WundergroundAPIKey"], Search, Additional)), 5)
			if not Response:
				return 2

			Data = await asyncio.wait_for(Response.json(), 5)
			if not Data:
				return 3

		if "error" in Data["response"]:
			self.Torchlight().SayPrivate(player, "[WU] {0}.".format(Data["response"]["error"]["description"]))
			return 5

		if not "current_observation" in Data:
			Choices = str()
			NumResults = len(Data["response"]["results"])
			for i, Result in enumerate(Data["response"]["results"]):
				Choices += "{0}, {1}".format(Result["city"],
					Result["state"] if Result["state"] else Result ["country_iso3166"])

				if i < NumResults - 1:
					Choices += " | "

			self.Torchlight().SayPrivate(player, "[WU] Did you mean: {0}".format(Choices))
			return 6

		Observation = Data["current_observation"]

		self.Torchlight().SayChat("[{0}, {1}] {2}°C ({3}F) {4} | Wind {5} {6}kph ({7}mph) | Humidity: {8}".format(Observation["display_location"]["city"],
			Observation["display_location"]["state"] if Observation["display_location"]["state"] else Observation["display_location"]["country_iso3166"],
			Observation["temp_c"], Observation["temp_f"], Observation["weather"],
			Observation["wind_dir"], Observation["wind_kph"], Observation["wind_mph"],
			Observation["relative_humidity"]))

		return 0

### LEVEL 0 COMMANDS ###

### LIMITED LEVEL 0 COMMANDS ###
class VoiceCommands(BaseCommand):
	import json
	import random
	def __init__(self, torchlight):
		super().__init__(torchlight)
		self.Triggers = ["!random"]
		self.Level = 0

	def LoadTriggers(self):
		try:
			with open("triggers.json", "r") as fp:
				self.VoiceTriggers = self.json.load(fp)
		except ValueError as e:
			self.Logger.error(sys._getframe().f_code.co_name + ' ' + str(e))
			self.Torchlight().SayChat(str(e))

	def _setup(self):
		self.Logger.debug(sys._getframe().f_code.co_name)
		self.LoadTriggers()
		for Triggers in self.VoiceTriggers:
			for Trigger in Triggers["names"]:
				self.Triggers.append(Trigger)

	async def _func(self, message, player):
		self.Logger.debug(sys._getframe().f_code.co_name + ' ' + str(message))

		Level = 0
		if player.Access:
			Level = player.Access["level"]

		Disabled = self.Torchlight().Disabled
		if Disabled and (Disabled > Level or Disabled == Level and Level < self.Torchlight().Config["AntiSpam"]["ImmunityLevel"]):
			self.Torchlight().SayPrivate(player, "Torchlight is currently disabled!")
			return 1

		if message[0][0] == '_' and Level < 2:
			return 1

		if message[0].lower() == "!random":
			Trigger = self.random.choice(self.VoiceTriggers)
			if isinstance(Trigger["sound"], list):
				Sound = self.random.choice(Trigger["sound"])
			else:
				Sound = Trigger["sound"]
		else:
			for Trigger in self.VoiceTriggers:
				for Name in Trigger["names"]:
					if message[0].lower() == Name:
						Num = Utils.GetNum(message[1])
						if Num:
							Num = int(Num)

						if isinstance(Trigger["sound"], list):
							if Num and Num > 0 and Num <= len(Trigger["sound"]):
								Sound = Trigger["sound"][Num - 1]
							else:
								Sound = self.random.choice(Trigger["sound"])
						else:
							Sound = Trigger["sound"]

						break

		Path = os.path.abspath(os.path.join("sounds", Sound))
		AudioClip = self.Torchlight().AudioManager.AudioClip(player, "file://" + Path)
		if not AudioClip:
			return 1

		return AudioClip.Play()

class YouTube(BaseCommand):
	def __init__(self, torchlight):
		super().__init__(torchlight)
		self.Triggers = ["!yt"]
		self.Level = 0

	async def _func(self, message, player):
		self.Logger.debug(sys._getframe().f_code.co_name + ' ' + str(message))

		Level = 0
		if player.Access:
			Level = player.Access["level"]

		Disabled = self.Torchlight().Disabled
		if Disabled and (Disabled > Level or Disabled == Level and Level < self.Torchlight().Config["AntiSpam"]["ImmunityLevel"]):
			self.Torchlight().SayPrivate(player, "Torchlight is currently disabled!")
			return 1

		if self.Torchlight().LastUrl:
			message[1] = message[1].replace("!last", self.Torchlight().LastUrl)

		Temp = DataHolder()
		Time = None

		if Temp(message[1].find("&t=")) != -1 or Temp(message[1].find("?t=")) != -1 or Temp(message[1].find("#t=")) != -1:
			TimeStr = message[1][Temp.value + 3:].split('&')[0].split('?')[0].split('#')[0]
			if TimeStr:
				Time = Utils.ParseTime(TimeStr)

		AudioClip = self.Torchlight().AudioManager.AudioClip(player, message[1])
		if not AudioClip:
			return 1

		return AudioClip.Play(Time)

class YouTubeSearch(BaseCommand):
	import json
	import datetime
	def __init__(self, torchlight):
		super().__init__(torchlight)
		self.Triggers = ["!yts"]
		self.Level = 0

	async def _func(self, message, player):
		self.Logger.debug(sys._getframe().f_code.co_name + ' ' + str(message))

		Level = 0
		if player.Access:
			Level = player.Access["level"]

		Disabled = self.Torchlight().Disabled
		if Disabled and (Disabled > Level or Disabled == Level and Level < self.Torchlight().Config["AntiSpam"]["ImmunityLevel"]):
			self.Torchlight().SayPrivate(player, "Torchlight is currently disabled!")
			return 1

		Temp = DataHolder()
		Time = None

		if Temp(message[1].find("&t=")) != -1 or Temp(message[1].find("?t=")) != -1 or Temp(message[1].find("#t=")) != -1:
			TimeStr = message[1][Temp.value + 3:].split('&')[0].split('?')[0].split('#')[0]
			if TimeStr:
				Time = Utils.ParseTime(TimeStr)
			message[1] = message[1][:Temp.value]

		Proc = await asyncio.create_subprocess_exec("youtube-dl", "--dump-json", "-xg", "ytsearch:" + message[1],
			stdout = asyncio.subprocess.PIPE)
		Out, _ = await Proc.communicate()

		url, Info = Out.split(b'\n', maxsplit = 1)
		url = url.strip().decode("ascii")
		Info = self.json.loads(Info)

		if Info["extractor_key"] == "Youtube":
			self.Torchlight().SayChat("\x07E52D27[YouTube]\x01 {0} | {1} | {2}/5.00 | {3:,}".format(
				Info["title"], str(self.datetime.timedelta(seconds = Info["duration"])), round(Info["average_rating"], 2), int(Info["view_count"])))

		AudioClip = self.Torchlight().AudioManager.AudioClip(player, url)
		if not AudioClip:
			return 1

		self.Torchlight().LastUrl = url

		return AudioClip.Play(Time)

class Say(BaseCommand):
	import gtts
	import tempfile
	VALID_LANGUAGES = [lang for lang in gtts.gTTS.LANGUAGES.keys()]
	def __init__(self, torchlight):
		super().__init__(torchlight)
		self.Triggers = [("!say", 4)]
		self.Level = 0

	async def Say(self, player, language, message):
		GTTS = self.gtts.gTTS(text = message, lang = language, debug = False)

		TempFile = self.tempfile.NamedTemporaryFile(delete = False)
		GTTS.write_to_fp(TempFile)
		TempFile.close()

		AudioClip = self.Torchlight().AudioManager.AudioClip(player, "file://" + TempFile.name)
		if not AudioClip:
			os.unlink(TempFile.name)
			return 1

		if AudioClip.Play():
			AudioClip.AudioPlayer.AddCallback("Stop", lambda: os.unlink(TempFile.name))
			return 0
		else:
			os.unlink(TempFile.name)
			return 1

	async def _func(self, message, player):
		self.Logger.debug(sys._getframe().f_code.co_name + ' ' + str(message))

		Level = 0
		if player.Access:
			Level = player.Access["level"]

		Disabled = self.Torchlight().Disabled
		if Disabled and (Disabled > Level or Disabled == Level and Level < self.Torchlight().Config["AntiSpam"]["ImmunityLevel"]):
			self.Torchlight().SayPrivate(player, "Torchlight is currently disabled!")
			return 1

		if not message[1]:
			return 1

		Language = "en"
		if len(message[0]) > 4:
			Language = message[0][4:]

		if not Language in self.VALID_LANGUAGES:
			return 1

		asyncio.ensure_future(self.Say(player, Language, message[1]))
		return 0

class Stop(BaseCommand):
	def __init__(self, torchlight):
		super().__init__(torchlight)
		self.Triggers = ["!stop"]
		self.Level = 0

	async def _func(self, message, player):
		self.Logger.debug(sys._getframe().f_code.co_name + ' ' + str(message))

		self.Torchlight().AudioManager.Stop(player, message[1])
		return True

### LIMITED LEVEL 0 COMMANDS ###


### LEVEL 1 COMMANDS ###
### LEVEL 1 COMMANDS ###


### LEVEL 2 COMMANDS ###
### LEVEL 2 COMMANDS ###


### LEVEL 3 COMMANDS ###
class EnableDisable(BaseCommand):
	def __init__(self, torchlight):
		super().__init__(torchlight)
		self.Triggers = ["!enable", "!disable"]
		self.Level = 3

	async def _func(self, message, player):
		self.Logger.debug(sys._getframe().f_code.co_name + ' ' + str(message))
		if message[0] == "!enable":
			if self.Torchlight().Disabled:
				if self.Torchlight().Disabled > player.Access["level"]:
					self.Torchlight().SayPrivate(player, "You don't have access to enable torchlight since it was disabled by a higher level user.")
					return 1
				self.Torchlight().SayChat("Torchlight has been enabled for the duration of this map - Type !disable to disable it again.")

			self.Torchlight().Disabled = False

		elif message[0] == "!disable":
			if not self.Torchlight().Disabled:
				self.Torchlight().SayChat("Torchlight has been disabled for the duration of this map - Type !enable to enable it again.")

			self.Torchlight().Disabled = player.Access["level"]
### LEVEL 3 COMMANDS ###


### LEVEL 4 COMMANDS ###
class AdminAccess(BaseCommand):
	from collections import OrderedDict
	def __init__(self, torchlight):
		super().__init__(torchlight)
		self.Triggers = ["!access"]
		self.Level = 4

	def ReloadValidUsers(self):
		self.Torchlight().Access.Load()
		for Player in self.Torchlight().Players:
			Access = self.Torchlight().Access[Player.UniqueID]
			Player.Access = Access

	async def _func(self, message, player):
		self.Logger.debug(sys._getframe().f_code.co_name + ' ' + str(message))
		if not message[1]:
			return -1

		if message[1].lower() == "reload":
			self.ReloadValidUsers()
			self.Torchlight().SayChat("Loaded access list with {0} users".format(len(self.Torchlight().Access)))

		elif message[1].lower() == "save":
			self.Torchlight().Access.Save()
			self.Torchlight().SayChat("Saved access list with {0} users".format(len(self.Torchlight().Access)))

		# Modify access
		else:
			Player = None
			Buf = message[1]
			Temp = Buf.find(" as ")
			if Temp != -1:
				try:
					Regname, Level = Buf[Temp + 4:].rsplit(' ', 1)
				except ValueError as e:
					self.Torchlight().SayChat(str(e))
					return 1

				Regname = Regname.strip()
				Level = Level.strip()
				Buf = Buf[:Temp].strip()
			else:
				try:
					Buf, Level = Buf.rsplit(' ', 1)
				except ValueError as e:
					self.Torchlight().SayChat(str(e))
					return 2

				Buf = Buf.strip()
				Level = Level.strip()

			# Find user by User ID
			if Buf[0] == '#' and Buf[1:].isnumeric():
				Player = self.Torchlight().Players.FindUserID(int(Buf[1:]))
			# Search user by name
			else:
				for Player_ in self.Torchlight().Players:
					if Player_.Name.lower().find(Buf.lower()) != -1:
						Player = Player_
						break

			if not Player:
				self.Torchlight().SayChat("Couldn't find user: {0}".format(Buf))
				return 3

			if Level.isnumeric() or (Level.startswith('-') and Level[1:].isdigit()):
				Level = int(Level)

				if Level >= player.Access["level"] and player.Access["level"] < 10:
					self.Torchlight().SayChat("Trying to assign level {0}, which is higher or equal than your level ({1})".format(Level, player.Access["level"]))
					return 4

				if Player.Access:
					if Player.Access["level"] >= player.Access["level"] and player.Access["level"] < 10:
						self.Torchlight().SayChat("Trying to modify level {0}, which is higher or equal than your level ({1})".format(Player.Access["level"], player.Access["level"]))
						return 5

					if "Regname" in locals():
						self.Torchlight().SayChat("Changed \"{0}\"({1}) as {2} level/name from {3} to {4} as {5}".format(
							Player.Name, Player.UniqueID, Player.Access["name"], Player.Access["level"], Level, Regname))
						Player.Access["name"] = Regname
					else:
						self.Torchlight().SayChat("Changed \"{0}\"({1}) as {2} level from {3} to {4}".format(
							Player.Name, Player.UniqueID, Player.Access["name"], Player.Access["level"], Level))

					Player.Access["level"] = Level
					self.Torchlight().Access[Player.UniqueID] = Player.Access
				else:
					if not "Regname" in locals():
						Regname = Player.Name

					self.Torchlight().Access[Player.UniqueID] = self.OrderedDict([("name", Regname), ("level", Level)])
					Player.Access = self.Torchlight().Access[Player.UniqueID]
					self.Torchlight().SayChat("Added \"{0}\"({1}) to access list as {2} with level {3}".format(Player.Name, Player.UniqueID, Regname, Level))
			else:
				if Level == "revoke" and Player.Access:
					if Player.Access["level"] >= player.Access["level"] and player.Access["level"] < 10:
						self.Torchlight().SayChat("Trying to revoke level {0}, which is higher or equal than your level ({1})".format(Player.Access["level"], player.Access["level"]))
						return 6

					self.Torchlight().SayChat("Removed \"{0}\"({1}) from access list (was {2} with level {3})".format(
						Player.Name, Player.UniqueID, Player.Access["name"], Player.Access["level"]))
					del self.Torchlight().Access[Player.UniqueID]
					Player.Access = None
		return 0
### LEVEL 4 COMMANDS ###


### LEVEL X COMMANDS ###
class Exec(BaseCommand):
	def __init__(self, torchlight):
		super().__init__(torchlight)
		self.Triggers = ["!exec"]
		self.Level = 9

	async def _func(self, message, player):
		self.Logger.debug(sys._getframe().f_code.co_name + ' ' + str(message))
		try:
			Response = eval(message[1])
		except Exception as e:
			self.Torchlight().SayChat("Error: {0}".format(str(e)))
			return 1
		self.Torchlight().SayChat(str(Response))
		return 0

class Reload(BaseCommand):
	def __init__(self, torchlight):
		super().__init__(torchlight)
		self.Triggers = ["!reload"]
		self.Level = 6

	async def _func(self, message, player):
		self.Logger.debug(sys._getframe().f_code.co_name + ' ' + str(message))
		self.Torchlight().Reload()
		return 0
### LEVEL X COMMANDS ###