import os
import discord
from discord.ext import commands
from bs4 import BeautifulSoup
import requests
from replit import db
from random import randint
import time

from keep_alive import keep_alive

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix='/DD', intents=intents)



last_time = time.gmtime().tm_hour * 60 * 60 + time.gmtime(
).tm_min * 60 + time.gmtime().tm_sec
print(last_time)

emojis = {
	'flushed': "<a:thats_so_flushed:806909343916097557>",
	}

probability_lit = 2
probability_channel_rank = 2

@client.event
async def on_ready():
	global personal_chan
	global channel_finder
  
  
	print(f"We have logged in as {client.user}")
	await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name='Layers of Fear'))
	    
	personal_chan = "——Personal Lairs——"
	channel_finder = client.get_channel(831345726394990593)

	#for (u, c) in zip(users, channels):
	#  db["c_"+str(u)] = c
	
	
	#chnnl = client.get_channel(814445041409064961)
	#await chnnl.send(file=discord.File("read_the_rules.jpg"))

	await startup_functions()


async def startup_functions():
	await print_db()
	# await sort_channels()

async def print_db():
	print("-"*40)
	for cu in db.keys():
		print(f"** {cu}: {db[cu]}")
	print("-"*40)


async def give_equal_channel_values(value=2):
	for cs in db.prefix('chnScore_'):
		if(cs.startswith('chnScore_')):
			del db[cs]
	print(db.prefix('c_'))
	for m in db.prefix('c_'):
		if(m.startswith('c_')):
			db['chnScore_' + str(db[m])] = value

sorting_channels = False
async def sort_channels(value=False):
	global sorting_channels
	print("Soring Channels...")
	sorting_channels = True

	if(not(value)):
		value = client.get_channel(826062486766616617).position + 1
	channels = dict()

	for chn_s in db.prefix('chnScore_'):
		if(chn_s.startswith('chnScore_')):
			x = int(chn_s.split('_')[-1])
			y = db[chn_s]
			new_update = {x: y}
			channels.update(new_update)
	channels = sorted(channels.items(), key=lambda x: x[1])
	for channel in channels:
		id=channel[0]
		chn = client.get_channel(id)
		if(chn):
			await chn.edit(position=value)
	print("Done.")
	sorting_channels = False


async def words_in_string(word_list, a_string):
	for w in word_list:
		if(not(w in a_string)):
			return(False)
	return(True)

async def get_time():
	return time.gmtime().tm_hour * 60 * 60 + time.gmtime(
		).tm_min * 60 + time.gmtime().tm_sec

async def whos_mentioned(msg):
	msg = msg.replace('!', '').replace("'s", '').lower().split()
	for w in msg:
		# print(w)
		if(w.startswith('<@') and w.endswith('>')):
			return(int(w.replace('<@', '').replace('>', '')))
	return(False)


# when a new member joins the server
@client.event
async def on_member_join(member):
	if (not (member.bot)):
		print(f"{member} joined")
		channel = client.get_channel(806413018056491029)
		await channel.send(
		    f"Welcome to the server, {str(member).split('#')[0]}! We are glad you joined. I will create a new personal channel just for you."
		)

		# create a new text channel
		personal_channel = discord.utils.get(member.guild.categories,
		                                     name=personal_chan)

		new_channel = await member.guild.create_text_channel(
		    f"{str(member).split('#')[0]}s-channel", category=personal_channel)
		await new_channel.send(
		    f"Welcome to your new personal channel, <@{member.id}>.\nThis is your personal Channel and you have your full control over it.\nYou can:\n`- Rename this Channel`\n`- Change the Channel's Description`\n`- Delete any message in this Channel`\n`- Pin any message in this Channel`\nHave Fun!"
		)

		await new_channel.set_permissions(member,
		                                  manage_channels=True,
		                                  manage_messages=True)
		db["c_" + str(member.id)] = new_channel.id


# when a member leaves
@client.event
async def on_member_remove(member):
	print(f"{member} removed")
	if (not (member.bot)):  #if it's not a bot
		await remove_member_data(member.id, str(member))

# remove_members_db_datas
async def remove_member_data(member_id, member_name = None):
	if(member_name == None):
		member_name = str(client.get_channel(member_id))
	
	print(f"deleting {member_name}'s channel")
	user_chan_id = db["c_" + str(member_id)]
	user_chan = client.get_channel(user_chan_id)
	await user_chan.delete()  #delete user's personal channel
	del db['chnScore_' + str(db['c_'+str(member_id)])]
	del db["c_" + str(member_id)]
	del db["favmusic_" + str(member_id)]


@client.event
async def on_message(message):
	global last_time
	global TruthAsked
	global sorting_channels
	global probability_lit, probability_channel_rank
	
	# if the sender is the bot herself
	if (message.author == client.user):
		return

	else:
		msg = message.content
		msg_len = len(msg)
		msg_auth = message.author
		chn_id = message.channel.id
		time_now = await get_time()

		print(f"{time_now}: {msg}") # read the message
		
		if(not(sorting_channels)):
			if (time_now > last_time + 2 * 60):
				if(message.channel.category):
					if(message.channel.category.id == 819890501415075880): # personal lairs
							if(randint(1, 5) > probability_channel_rank):
								if(not(chn_id in (831345726394990593, 826062486766616617))):
									db['chnScore_'+str(chn_id)] = db['chnScore_'+str(chn_id)] + 1
									probability_channel_rank
									await sort_channels()
							else:
								probability_channel_rank += 1

					elif (randint(1, 15) > probability_lit):
						await post_4chan_lit(0)
						probability_lit = 2
					else:
						probability_lit += 1
				
		if(message.channel.id == 825530904939069440):
			LitMsg = message.content.lower()
			for c in ["'", " ", ".", "please", ","]:
				LitMsg = LitMsg.replace(c, "")
			print(LitMsg)
			if (LitMsg == "provideuswithathread"):
				await post_4chan_lit(randint(0,2))

			elif (LitMsg == "differentthread"):
				await post_4chan_lit(randint(4, 7))
		
		# if message mentions @everyone
		if("@everyone" in msg):
			await message.delete()
		
		elif(message.channel.id == 831345726394990593):
			if(msg.lower()=="all"):
				text = []
				for c_u in db.prefix('c_'):
					if(not(c_u.startswith('chnScore_'))):
						text.append(f":stars:`{str(client.get_user(int(c_u[2:])))[:-5]}`: <#{db[c_u]}>\n")
				text = sorted(text)
				text = ''.join(text)
				# text.replace('_', '\_').replace('**', '\**').replace('*', '\*')
				await channel_finder.send(text)
			elif(msg.startswith('<@') and msg.endswith('>')):
				m = msg.replace('!', '')
				await channel_finder.send(f"<#{db['c_'+(m[2:-1])]}>")
			else:
				print("NO USE: " + msg)
				await message.delete()
		elif("<@823554116356669521>" in msg or "<@!823554116356669521>" in msg):
			print("DDL is mentioned;")
			if("truth or dare" in msg.lower().replace('?', '')):
				await message.reply("Truth.")
			elif(msg.endswith('?')):
				print("answering a question;")
				ans = await answer_to_question(msg)
				if(ans):
					await message.reply(ans)
				else:
					await message.reply("I don't know.")
			
			if(message.channel.id == 806413018056491031):
				print("music channel")
				if(await words_in_string(['track', 'my', 'favourite', 'spotify'], msg.lower())):
					await message.channel.send(await setup_favourite_music(message.author.id, msg.split()[-1]))
				elif(await words_in_string(['what', 'my', 'track', 'favourite'], msg.lower())):
					await message.channel.send(await show_favourite_music(message.author.id, message.channel))
				elif(await words_in_string(['what', '<@', 'track', 'favourite'], msg.replace('!', '').lower())):
					mentioned = await whos_mentioned(msg.replace('!', '').replace('<@823554116356669521>', ''))
					print(f"{mentioned} is mentioned")
					await message.channel.send(await show_favourite_music(mentioned, message.channel))
		
		if('flushed' in msg or 'flush me' in msg):
			await message.add_reaction(emojis['flushed'])

		
		last_time = time_now


# setup favourite music
async def setup_favourite_music(member_id, link, xtra_cmd=False):
	favmusic_id = f"favmusic_{member_id}"
	if((link.startswith("https://open.spotify") or link.startswith("open.spotify")and('track' in link))):
		link_xtrct = link.split('/')[-1]
	else:
		return("The link must be a valid spotify track link.")

	if(favmusic_id in db.keys()):
		if(len(db[favmusic_id]) >= 4):
			return("You already have 4 favourite tracks saved. Please remove or replace one instead.")
		else:
			db[favmusic_id].append(link_xtrct)
			return("I've added that as one of your favourite track! It's good to share music with others, isn't it?")
	else:
		db[favmusic_id] = []
		db[favmusic_id].append(link_xtrct)
		return("I've added that as one of your favourite track! It's good to share music with others, isn't it?")

# show favourite music
async def show_favourite_music(member_id, channel, xtra_cmd=False):
	favmusic_id = f"favmusic_{member_id}"
	if((favmusic_id in db.keys()) and len(db[favmusic_id])>0):
		await channel.send(f"<@{member_id}> has {len(db[favmusic_id])} favourite tracks. I'll send the links to them one by one!")
		for track in db[favmusic_id]:
			await channel.send(f"https://open.spotify.com/track/{track}")
		return("There!")
	else:
		return("User does not have any favourite music set up. Sorry.")


# answer to questions
async def answer_to_question(msg):
	msg = msg.replace('<@823554116356669521>', '').replace('<@!823554116356669521>', '').replace(' ', '+')
	print(f"https://answers.search.yahoo.com/search?p={msg}")
	# print(f"https://www.answers.com/search?q={msg}")

	html_text = requests.get(f"https://answers.search.yahoo.com/search?p={msg}").text
	# print(html_text)
	if(not(html_text)):
		return(False)

	soup = BeautifulSoup(html_text, 'lxml')
	# print(soup.find_all('div'))

	# answer = soup.find('p')
	try:
		answer = soup.find('div', class_="dd AnswrsV2").find(class_='compText')
	except:
		return(False)
	# print(answer)
	if(not(answer)):
		return(False)
	elif("we did not find results" in answer.text.lower()):
		return(False)
	return(str(answer.text))


# 4chan lit post
async def post_4chan_lit(indx=1):
	if (indx > 10):
		indx = 0
	print(f"4chan thread index: {indx}")
	lit_chan = client.get_channel(825530904939069440)
	html_text = requests.get('https://boards.4chan.org/lit/').text
	# print(html_text)
	soup = BeautifulSoup(html_text, 'lxml')
	thread = soup.find_all('div', class_='thread')[indx]

	# print(thread.find_all('img')) # thread src

	subject = thread.find('span', class_='subject').text
	msg = thread.find('blockquote', class_='postMessage')
	img_src = None

	m = ""
	for i in msg.childGenerator():
		i = str(i)
		if (not (i.startswith('<'))):
			m = m + f"\n{i}"
  
	if (subject.startswith("Welcome to")):
		await post_4chan_lit(indx=indx + 1)
		return
	try:
		img_src = thread.find_all('img')[0]['src'][2:]
		img_src = "https://" + img_src
	except:
		pass
	emoji = "<a:Pepe_Spell_Book:831740706242297926>"
	if (img_src):  #if img exists
		image = requests.get(img_src).content
		with open("temp.jpg", "wb") as f:
		  f.write(image)
		image = discord.File("temp.jpg")
		await lit_chan.send(
		    f"**{emoji} {subject}**\n```\n{m}\n```", file=image
		    )#+ "https://" + img_src)
	else:
		await lit_chan.send(
		    f"**{emoji} {subject}**\n```\n{m}\n```"
		)


# run the bot
keep_alive()
client.run(os.getenv('TOKEN'))
