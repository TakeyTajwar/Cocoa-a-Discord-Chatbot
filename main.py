import os
import discord
from discord.ext import commands
from bs4 import BeautifulSoup
import requests
from replit import db
from random import randint
import time
from datetime import datetime
import asyncio
import re

from keep_alive import keep_alive

intents = discord.Intents.default()
intents.presences = True
intents.members = True
client = commands.Bot(command_prefix='++', intents=intents)



last_time = time.gmtime().tm_hour * 60 * 60 + time.gmtime(
).tm_min * 60 + time.gmtime().tm_sec
print(last_time)

emojis = {
	'verify': "<a:Verify:832201162345938986>",
	'flushed': "<a:thats_so_flushed:806909343916097557>",
	'peek': "<a:Peek:855423985860870175>",
	'butterflies': "<a:butterflies:832203019474960401>"
	}

commands = {
	'++help': "See all the commands",
	'++secret_msg': "Send secret messages to someone (you can add attachments)",
}


probability_lit = 2
probability_channel_rank = 2


activity_general = 0
activity_interests = 0
activity_misc = 0
activity_personal_channels = 0
activity_all = 0


inv_link = r"https://discord.gg/WrQkFpy7sg"


@client.event
async def on_ready():
	global personal_channel_asc, personal_channel, personal_channel_nobles, personal_channel_knights, personal_channel_citizens, personal_channel_new, personal_channel_exc
	global list_personal_channel
	global list_score_thr_personal_channel
	global channel_finder, lit_chan
	global last_time_prch_sorted, list_id_personal_channel
	global bScoreDownAllPerChan


	
  
  
	print(f"We have logged in as {client.user}")
	await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name='Layers of Fear'))
	personal_channel_asc = client.get_channel(889099337941004310) # ascended
	personal_channel = client.get_channel(819890501415075880) # monarch
	personal_channel_nobles = client.get_channel(870210864047849513) # nobles 
	personal_channel_knights = client.get_channel(870210934520553543) #knights
	personal_channel_citizens = client.get_channel(870211119774584903) # citizens
	personal_channel_new = client.get_channel(868910910297755648) # settlers
	personal_channel_exc = client.get_channel(869599701647917106) # execution

	list_personal_channel = [personal_channel_asc, personal_channel, personal_channel_nobles, personal_channel_knights, personal_channel_citizens, personal_channel_new, personal_channel_exc]
	list_id_personal_channel = [channel.id for channel in list_personal_channel]
	list_score_thr_personal_channel = db["per_chan_score_threshold"]

	channel_finder = client.get_channel(831345726394990593)
	lit_chan = client.get_channel(825530904939069440)

	last_time_prch_sorted = 0

	bScoreDownAllPerChan = False



	await startup_functions()


async def startup_functions():
	await setup_guild()
	# await print_db()

	await	 update_utc_chn_name()	






async def print_db():
	print("-"*40)
	for cu in db.keys():
		print(f"** {cu}: {db[cu]}")
	print("-"*40)







async def setup_guild():
	global guild
	global server_booster_role, auth_role, mod_role

	guild = client.get_guild(806413017440845845)

	server_booster_role = discord.utils.get(guild.roles, id=830465050174816336)
	auth_role = discord.utils.get(guild.roles, id=807089336243454012)
	mod_role = discord.utils.get(guild.roles, id=806420752076111872)





async def update_utc_chn_name():
	utc_chn = client.get_channel(861857005559218197)

	while True:
		utcnow = datetime.utcnow()
		utcnow = str(utcnow)
		utcnow = utcnow.split(' ')[1]
		utcnow = utcnow.split('.')[0]
		utcnow = utcnow[:-3]
		print(utcnow)
		await utc_chn.edit(name=f"🕒utc_time_{utcnow}")

		await asyncio.sleep(5*60)




async def send_chn_message(chn_id, msg):
	chn = client.get_channel(chn_id)
	await chn.send(msg)



async def roll_a_dice():
	x = randint(1, 20)
	x_str = "Your number is **" + str(x) + "**. "
	if x == 1:
			x_str = x_str + "Oops, that sucks!"
	elif x <= 5:
			x_str = x_str + "That's pretty low!"
	elif x <= 10:
			x_str = x_str + "That's a-okay!"
	elif x <= 15:
			x_str = x_str + "Nice!"
	elif x <= 19:
			x_str = x_str + "Good job!"
	elif x == 20:
			x_str = x_str + "Fucking awesome!"
	
	return(x_str)




async def score_up_per_chan(chn_id):
	await client.wait_until_ready()
	db['chnScore_'+str(chn_id)] = db['chnScore_'+str(chn_id)] + 1
	await channel_finder.send(f"<#{chn_id}> scored up")
	print("personal channel scored up")

	await rank_per_chan(chn_id)


async def score_down_per_chan(chn_id):
	await client.wait_until_ready()
	db['chnScore_'+str(chn_id)] = db['chnScore_'+str(chn_id)] - 1
	await channel_finder.send(f"<#{chn_id}> scored down")
	print("personal channel scored down")

	if(db['chnScore_'+str(chn_id)] <= -5):
		print(f"deleting personal channel #{chn_id}")
		for c_u in db.prefix('c_'): # delete per chan info
			if(not(c_u.startswith('chnScore_'))):
				if(db[c_u] == str(chn_id)):
					await delete_per_chan_info(c_u)
					break;
		chn = client.get_channel(int(chn_id))
		if(chn):
			await channel_finder.send(f"<#{chn_id}> is going to be deleted for having a score below threshold.")
			await chn.delete(reason="Score below threshold.")
		return;
	elif(db['chnScore_'+str(chn_id)] <= 2):
		messages = client.get_channel(chn_id).history(limit=10).flatten()
		if(not(messages)):
			await channel_finder.send(f"<#{chn_id}> is going to be deleted for having a score below threshold for channel with no messages.")
			chn = client.get_channel(int(chn_id))
			await chn.delete(reason="Score below threshold for channel with no messages.")
			for c_u in db.prefix('c_'): # delete per chan info
				if(not(c_u.startswith('chnScore_'))):
					if(db[c_u] == str(chn_id)):
						await delete_per_chan_info(c_u)
						break;

	await rank_per_chan(chn_id)




async def score_up_all_per_chan():
	await client.wait_until_ready()
	dt_now = datetime.now()
	db["last_time_score_up_all_per_chan"] = dt_now.isoformat()
	
	for cat in list_personal_channel:
				for chn in cat.channels:
					if(not(chn.id in [831345726394990593, 826062486766616617])):
						try:
							last_message = await chn.fetch_message(chn.last_message_id)
							dt_delta = dt_now - last_message.created_at
							print(f"{chn}: {dt_delta}: {last_message.content}")
							if(dt_delta.days < 1): # if channel was active today
								await score_up_per_chan(chn.id)
						except Exception as e:
							print(e)
							print("except")
	
	await sort_channels()




async def score_down_all_per_chan():
	await client.wait_until_ready()
	dt_now = datetime.now()
	db["last_time_score_down_all_per_chan"] = dt_now.isoformat()
	
	for cat in list_personal_channel:
				for chn in cat.channels:
					if(not(chn.id in [831345726394990593, 826062486766616617])):
						try:
							last_message = await chn.fetch_message(chn.last_message_id)
							dt_delta = dt_now - last_message.created_at
							print(f"{chn}: {last_message.created_at}: {last_message.content}")
							if((dt_delta.days > 7*2)): # if channel is inactive for more than two weeks
								await score_down_per_chan(chn.id)
							else:
								dt_delta_created = dt_now - chn.created_at
								if(dt_delta_created.days < 7*4 and dt_delta.days > 7): # if channel is younger than 4 weeks and is inactive for 7 days
									await score_down_per_chan(chn.id)

						except Exception as e:
							print(e)
							await score_down_per_chan(chn.id)
	
	await sort_channels()
							


async def rank_per_chan(chn_id):
	chn = client.get_channel(chn_id)
	chn_cat = chn.category
	chn_score = db['chnScore_'+str(chn_id)]
	
	if(chn_score >= list_score_thr_personal_channel[0]): # monarchs
		if(chn_cat == list_personal_channel[0]):
			return;
		else:
			if(len(list_personal_channel[0].channels) < 47):
				await chn.edit(category = list_personal_channel[0])
				await channel_finder.send(f"<#{chn_id}> ranked up to <#{list_id_personal_channel[0]}>!")
			else:
				await send_chn_message(820840150044770335, f"<#{list_id_personal_channel[0]}> is (/almost) full!")
				await rank_all_per_chan(specific_cat=list_id_personal_channel[0])
		return;

	for i in list(range(1, len(list_personal_channel))):
		if(chn_score >= list_score_thr_personal_channel[i]):
			if(chn_cat == list_personal_channel[i]):
				return;
			else:
				if(len(list_personal_channel[i].channels) < 47):
					await chn.edit(category = list_personal_channel[i])
					await channel_finder.send(f"<#{chn_id}> ranked to <#{list_id_personal_channel[i]}>!")
				else:
					await send_chn_message(820840150044770335, f"<#{list_id_personal_channel[i]}> is (/almost) full!")
					await rank_all_per_chan(specific_cat=list_id_personal_channel[i])
			return;

	if(chn_score <= list_score_thr_personal_channel[-1]): # execution pit 
			if(chn_cat == list_personal_channel[-1]):
				return;
			else:
				if(len(list_personal_channel[i].channels) < 47):
					await chn.edit(category = list_personal_channel[-1])
					await channel_finder.send(f"<#{chn_id}> ranked to <#{list_id_personal_channel[-1]}>!")
				else:
					await send_chn_message(820840150044770335, f"<#{list_id_personal_channel[-1]}> is (/almost) full!")
					await rank_all_per_chan(specific_cat=list_id_personal_channel[-1])
				return;


ranking_channels = False
async def rank_all_per_chan(specific_cat = None):
	global ranking_channels
	ranking_channels = True

	message = await channel_finder.send("Ranking channels")

	await client.wait_until_ready()
	if(specific_cat == None):
		for cat in list_personal_channel:
				for chn in cat.channels:
					if(not(chn.id in [831345726394990593, 826062486766616617])):
						await rank_per_chan(chn.id)
	else:
		for chn in specific_cat.channels:
			if(not(chn.id in [831345726394990593, 826062486766616617])):
				await rank_per_chan(chn.id)
	
	await message.edit(content=f"{message.content} (**Done**)")



# async def give_equal_channel_values(value=2):
# 	for cs in db.prefix('chnScore_'):
# 		if(cs.startswith('chnScore_')):
# 			del db[cs]
# 	print(db.prefix('c_'))
# 	for m in db.prefix('c_'):
# 		if(m.startswith('c_')):
# 			db['chnScore_' + str(db[m])] = value



sorting_channels = False
async def sort_channels(value=2):
	dt_now = datetime.now()
	db['last_time_sort_per_chan'] = dt_now.isoformat()

	global sorting_channels, last_time_prch_sorted
	last_time_prch_sorted = await get_time()
	await client.wait_until_ready()
	print("Soring Channels...")
	sorting_channels = True
	message = await channel_finder.send("Sorting Channels.")

	if(not(value)):
		value = client.get_channel(826062486766616617).position + 1
	channels = dict()

	for chn_s in db.prefix('chnScore_'):
		if(chn_s.startswith('chnScore_')):
			if(not(chn_s.endswith('826062486766616617'))):
				x = int(chn_s.split('_')[-1])
				y = db[chn_s]
				new_update = {x: y}
				channels.update(new_update)
	channels = sorted(channels.items(), key=lambda x: x[1])
	for channel in channels:
		id=channel[0]
		chn = client.get_channel(id)
		if(chn):
			if(chn.category == personal_channel):
				if(not(chn.id in [831345726394990593, 826062486766616617])):
					await chn.edit(position=value)
			# if(chn.category == personal_channel_new):
			else:
				await chn.edit(position=0)
	
	await client.get_channel(831345726394990593).edit(position=0)
	await client.get_channel(826062486766616617).edit(position=1)
	await update_per_chan_count()

	print("Done.")
	sorting_channels = False
	await message.edit(content=f"{message.content} (**Done**)")
	return(True)



async def count_per_chan():
	n = 0
	for chan_id in list_id_personal_channel:
		chan = client.get_channel(chan_id)
		n += int(len(chan.channels))
	
	return(n)

async def update_per_chan_count():
	print("Updating per chan count")
	count = await count_per_chan()
	count_chan = client.get_channel(870997494170013748)
	await count_chan.edit(name=f"{count} Channels")




async def decide_all_channel_score_down():
	dt_now = datetime.now()
	dt_last_time_score_down_all_per_chan = datetime.fromisoformat(db["last_time_score_down_all_per_chan"])
	dt_delta = dt_now - dt_last_time_score_down_all_per_chan
	dt_delta_hours = dt_delta.total_seconds()//3600
	print(f"last time all channels scored down: {dt_delta_hours} hours ago")
	if(dt_delta_hours > 24):
		await score_down_all_per_chan()
		return(True)
	return(False)



async def decide_all_channel_score_up():
	dt_now = datetime.now()
	dt_last_time_score_down_all_per_chan = datetime.fromisoformat(db["last_time_score_up_all_per_chan"])
	dt_delta = dt_now - dt_last_time_score_down_all_per_chan
	dt_delta_hours = dt_delta.total_seconds()//3600
	print(f"last time all channels scored up: {dt_delta_hours} hours ago")
	if(dt_delta_hours > 24):
		await score_up_all_per_chan()
		return(True)
	return(False)



async def update_per_chan_rank_threshold(score_thresholds):
	global list_score_thr_personal_channel

	if(not(len(score_thresholds) == len(list_id_personal_channel))):
		print("Does not match personal channel ranks number.")
		return(False);

	for i in score_thresholds:
		if(not(isinstance(i, int))):
			return(False);


	def ordertest(A):
		for i in range(len(A) - 1):
			if A[i] < A[i+1]:
					print("Not all items are integers.")
					return False
		return True

	if(ordertest(score_thresholds)):
			db["per_chan_score_threshold"] = score_thresholds
			list_score_thr_personal_channel = score_thresholds
			print(f"Rank threolds updated: {score_thresholds}")
			return(True);
	
	print("List is not in descending order or something else is wrong.")
	return(False);





async def reset_vars():

	print("Resetting variables")

	






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
		gen_channel = client.get_channel(806413018056491029)
		# await channel.send(
		#     f"Welcome to the server, {str(member).split('#')[0]}! We are glad you joined. I will create a new personal channel just for you."
		# )
		embed=discord.Embed(title="A New Member Joined Our Server!")
		embed.add_field(name="English", value=f"Welcome <@{member.id}>. We are glad that you joined. Please look around and meet new people. I will create a personal channel for you.", inline=True)
		embed.add_field(name="Español", value=f"Bienvenido <@{member.id}>. Nos alegra que se haya unido. Por favor, mire a su alrededor y conozca gente nueva. Crearé un canal personal para ti.", inline=True)
		await gen_channel.send(embed=embed)

		new_channel = await create_per_chan(member)
		if(new_channel):
			embed=discord.Embed()
			embed.add_field(name=f"{new_channel}", value=f"<@{member.id}>, your new channel is <#{new_channel.id}>.", inline=True)
			embed.add_field(name="{new_channel}", value="<@{member.id}>, tu nuevo canal es <#{new_channel.id}>.", inline=True)
			await gen_channel.send(embed=embed)



async def create_per_chan(member):
	if(not(member in guild.members)):
		return("Inv_UserNotMember")
	# create a new text channel

	new_channel = await guild.create_text_channel(
			f"{str(member).split('#')[0]}s-channel", category=personal_channel_new)
	
	embed = discord.Embed(title="Welcome to Your New Personal Channel!", description=f"**(En)**Welcome to your new personal channel, <@{member.id}>. Your Personal Channel in our server. You have your full control over your personal channel (but do not violate [discord's TOS](https://discord.com/terms) or server rules).\n**(ES)**Bienvenido a su nuevo canal personal, <@{member.id}>. Tu canal personal en nuestro servidor. Tienes el control total sobre tu canal personal (pero no infrinjas los [TOS de Discord](https://discord.com/terms) o las reglas del servidor).", color=0x88ff4b)
	embed.add_field(name='Rename this Channel ', value="**(En)**This is your personal channel so of course you can rename it! If you're on Desktop then click on the settings icon (next to your channel's name in channel list) and if you're on a mobile device, hold the channel to go the edit-channel page of your channel. Your channel deserves a proper title.\n**(Es)**Este es tu canal personal, así que, por supuesto, ¡puedes cambiarle el nombre! Si está en el escritorio, haga clic en el ícono de configuración (junto al nombre de su canal en la lista de canales) y si está en un dispositivo móvil, mantenga presionado el canal para ir a la página de edición del canal de su canal. Tu canal merece un título adecuado.", inline=False)
	embed.add_field(name='Change the Channel\'s Description', value="**(En)**You can change the description of your channel in the same page you can change the name of your channel.\n**(Es)**Puedes cambiar la descripción de tu canal en la misma página puedes cambiar el nombre de tu canal.", inline=False)
	embed.add_field(name='Delete any message', value="**(En)**Are there messages in your channel that you don't want it to have? Clean your channel up.\n**(Es)**¿Hay mensajes en tu canal que no quieres que tenga? Limpia tu canal.", inline=False)
	embed.add_field(name='Pin any message', value="**(En)**You can pin any message in your channel. On desktop, hold shift and click the pin icon or click the three-dots icon and pin. On Mobile, hold the message and then click on the pin option.\n**(Es)**Puedes anclar cualquier mensaje en tu canal. En el escritorio, mantenga presionada la tecla Mayús y haga clic en el ícono de alfiler o haga clic en el ícono de tres puntos y el alfiler. En el dispositivo móvil, mantenga presionado el mensaje y luego haga clic en la opción de pin.", inline=False)
	embed.add_field(name='Manage permissions', value="**(En)**You can manage permissions for members for your channel.\n**(Es)**Puede administrar los permisos de los miembros de su canal.", inline=False)
	embed.set_footer(text="Have Fun! ¡Divertirse!")

	await new_channel.send(embed=embed)
	
	await new_channel.send(f"**Welcome, <@{member.id}>, to your new Personal Channel!**")

	# await new_channel.send(
	# 		f"Welcome to your new personal channel, <@{member.id}>.\nThis is your personal Channel and you have your full control over it.\nYou can:\n`- Rename this Channel`\n`- Change the Channel's Description`\n`- Delete any message in this Channel`\n`- Pin any message in this Channel`\n`- Manage permissions for any member or role`\nHave Fun!"
	# )
	await new_channel.set_permissions(member,
																		manage_channels=True,
																		manage_messages=True,
																		manage_permissions=True)
	db["c_" + str(member.id)] = new_channel.id
	db["chnScore_"+str(new_channel.id)] = 2

	await update_per_chan_count()

	return(new_channel)




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
	await update_per_chan_count()
	await delete_per_chan_info(member_id)
	if("favmusic_" + str(member_id) in db.keys()):
		del db["favmusic_" + str(member_id)]



async def delete_per_chan_info(member_id):
	print("Deleting personal chan informations")

	print("del chnScore_")
	print(db['chnScore_' + str(db['c_'+str(member_id)])])
	del db['chnScore_' + str(db['c_'+str(member_id)])]
	
	print("del c_")
	del db["c_" + str(member_id)]
	print("Done")




@client.event
async def on_guild_channel_delete(channel):
	print("A channel has been deleted")
	channel_id = channel.id
	if channel.category == personal_channel:
		print("Personal channel deleted.")
		for c_u in db.prefix('c_'):
			if(not(c_u.startswith('chnScore_'))):
				if(db[c_u] == str(channel_id)):
					await delete_per_chan_info(c_u)
					break;

			












# deleted message
@client.event
async def on_message_delete(message):
	global bScoreDownAllPerChan

	time_now_omd = await get_time()
	print("omd_" + str(time_now_omd))



	# score down all personal channels
	if(not(activity_all>15)):
		if(activity_all % 2 == 0):
			await decide_all_channel_score_down()
		else:
			await decide_all_channel_score_up()
	
	# sort personal channels
	if((activity_all < 2) and (2 > randint(1, 5))):
		dt_now = datetime.now()
		dt_last_time_sort_per_chn = datetime.fromisoformat(db["last_time_sort_per_chan"])
		dt_delta = dt_now - dt_last_time_sort_per_chn
		if(dt_delta.days > 1):
			await sort_channels()
		













# new message
@client.event
async def on_message(message):
	await client.wait_until_ready()

	global last_time
	global TruthAsked
	global sorting_channels
	global probability_lit, probability_channel_rank
	global activity_general, activity_interests, activity_misc, activity_personal_channels, activity_all
	
	# if the sender is the bot herself
	if (message.author == client.user):
		return

	msg = message.content
	msg_len = len(msg)
	msg_lower = msg.lower()
	msg_auth = message.author
	chn_id = message.channel.id
	msg_attachments = message.attachments
	if(not(str(message.channel.type)=='private')):
		msg_inserver = True
		msg_auth_roles = msg_auth.roles
		if(message.channel.category):
			chn_cat_id = message.channel.category.id
		else:
			chn_cat_id = None
	else:
		msg_inserver = False
		msg_auth_roles = chn_cat_id = None
		guild = client.get_guild(806413017440845845)
		if(not(msg_auth in guild.members)):
			await msg_auth.send(f"Hey, it looks like you're not a member of our server. Here is an invite link to our server. We will love to have as one of us.\n{inv_link}")
	
	

	time_now = await get_time()

	# print(msg_auth_roles)

	print(f"{time_now}: {msg}") # read the message

	if(time_now > last_time + 45 * 60):
		activity_general = 0
		activity_interests = 0
		activity_misc = 0
		activity_cool_ideas = 0
		activity_personal_channels = 0
		activity_all = 0

		await reset_vars()
	
	if(not(str(message.channel.type)=='private')):
		if(chn_cat_id==806413018056491028):
			activity_general += 1
		elif(chn_cat_id==825523271004192799):
			activity_interests += 1
		elif(chn_cat_id==806423158344384512):
			activity_misc += 1
		elif(chn_cat_id==810881959273431092):
			activity_cool_ideas += 1
		elif(chn_cat_id in list_id_personal_channel):
			activity_personal_channels += 1

		activity_all += 1
	# if message mentions @everyone
	if(message.mention_everyone):
		await message.delete()
		return;
	
	if(msg.startswith('++')): # commands
		print('command')
		if(chn_id==820840150044770335): #bot-settings
			print('command in #bot-settings')
			# test command
			if(msg_lower=='++test'):
				await message.reply("I can read your command.")
				return;
			
			# get per chan number
			elif(msg_lower=='++num_of_per_chan'):
				await message.reply(str(await count_per_chan()))
			
			# update per chan count channel
			elif(msg_lower=='++update_per_chan_count'):
				await update_per_chan_count()
			
			elif(msg_lower.startswith('++upd_rank_thr')):
				rank_thr = msg_lower.replace(',', '').split()
				rank_thr = rank_thr[1:]
				rank_thr = [int(thr) for thr in rank_thr]
				print(rank_thr)
				if(await update_per_chan_rank_threshold(rank_thr)):
					await message.reply("Done.")
				else:
					await message.reply("Something's wrong.")
			
			# score down all per chan
			elif(msg_lower=='++score_down_all_per_chan'):
				if(auth_role in msg_auth_roles):
					if(sorting_channels):
						await message.reply("Can not do that right now. Currently sorting channels.")
						return;
					else:
						if(await decide_all_channel_score_down()):
							await message.reply("Done.")
						else:
							await message.reply("Last time all channels were scored down less than threshold hours ago.")
						return;

			# sort per chan
			elif(msg_lower=='++sort_per_chan'):
				if(not(sorting_channels)):
					if(await sort_channels()):
						await message.reply("Sorting personal channels done.")
				else:
					await message.reply("Already sorting personal channels.")
			
			# rank per chan
			elif(msg_lower=='++rank_all_per_chan'):
				if(not(sorting_channels)):
					await rank_all_per_chan()
					await message.reply("Done.")
				else:
					await message.reply("Can not do that right now. Currently sorting channels.")

			# send chan message
			elif(msg.startswith('++send_ch')):
				if(auth_role in msg_auth_roles):
					await send_chn_message(int(msg.split()[1]), ' '.join(msg.split()[2:]))
				await message.delete()
				return;

		# help command
		if(msg_lower.startswith('++help')):
			await message.reply(await help_msg(msg_auth))
		
		# send secret message
		elif(msg.lower().startswith(('++secret_msg', '++secret_message'))):
			if((re.match('^\+\+secret_(msg|message)\s*<?@?!?[\d]{17,19}>?\s*(\[.+])?\s*', msg)) or re.match('\+\+secret_(msg|message)\s*@?([\w\d\s]+#\d{4})\s*', msg)):
				scrt_msg = await secret_message(msg, sender=msg_auth, attachments=msg_attachments)
				if(scrt_msg==True):
					await msg_auth.send(f"**Secret message sent! {emojis['verify']}**")
				elif(scrt_msg.startswith('403')):
					await msg_auth.send(f"I am sorry. I could not deliver the secret message to the recipient. Discord does not allow bots to send messages to one who does not share any common server with the bot. The recipent needs to be a member of *Dark & Daisy Association* for me to send them a message.\nYou can send the recipent this invitation link: {inv_link}")
				elif(scrt_msg.startswith('StC')):
					await msg_auth.send(f"{emojis['peek']} You can't send secret messages to me, silly.")
				else:
					await msg_auth.send(f"Something went wrong sending the secret message. Please contact one of my developers so they can fix me. :'(\nErrorMessage:```{scrt_msg}```")
			else:
				await msg_auth.send("**Invalid Syntax!**\nCorrect syntax is: ```++secret_msg USER_ID Message```\nWith secret name:```++secret_msg USER_ID [secret_name] Message```\nFor example:```++secret_msg 823554116356669521 [Your Secret Stalker] Hello, Dark & Daisy Lady!```\nOr you can use Username too:\n```++secret_msg @Dark & Daisy Lady#1095 [Your Secret Stalker] Hello, Dark & Daisy Lady!```")
			if(not(str(message.channel.type)=='private')):
					await message.delete()
			return;
		
	elif(str(message.channel.type)=='private'):
		await msg_auth.send("Please use `++help` to see all the commands.")
	
	if(not(sorting_channels)):
		if (time_now > last_time + 25):
			if(chn_cat_id):
				if(chn_cat_id in list_id_personal_channel): # personal channel
						if(probability_channel_rank > randint(1, 4 + activity_all)):
							if(not(chn_id in (831345726394990593, 826062486766616617))):
								await score_up_per_chan(chn_id)
								if(3 >= randint(1, 5)):
									if(time_now > last_time_prch_sorted + 2 * 60 * 60):
										await sort_channels()
									probability_channel_rank = 0
						else:
							probability_channel_rank += 1

				elif (probability_lit > randint(1, 70 + activity_all)):
					await post_4chan_lit(0)
					probability_lit = 0
				else:
					probability_lit += 1
			
	if(message.channel.id == 825530904939069440): #literature
		LitMsg = message.content.lower()
		for c in ["'", " ", ".", "please", ","]:
			LitMsg = LitMsg.replace(c, "")
		print(LitMsg)
		if (LitMsg == "provideuswithathread"):
			await post_4chan_lit(randint(0,2))

		elif (LitMsg == "differentthread"):
			await post_4chan_lit(randint(4, 7))
	

	elif(message.channel.id == 883651265563877416):
		if(not(message.author.bot)):
			if(not(msg_lower == '!d bump')):
				await message.delete()

	
	elif(message.channel.id == 831345726394990593): #channel-finder
		if(re.match(r'all ?[\d]*', msg.lower())):
			text = []
			if(msg.lower()=="all"):
				try:
					for c_u in db.prefix('c_'):
						if(not(c_u.startswith('chnScore_'))):
							chn = client.get_channel(int(db[str(c_u)]))
							if(chn):
								text_ = ""
								text_ = text_ + (f":stars:`{str(client.get_user(int(c_u[2:])))[:-5]}`: <#{db[c_u]}>")
								text_ = text_ + (f" ({db['chnScore_'+str(db['c_'+str(c_u[2:])])]})\n")
								text.append(text_)
							else:
								if('c_'+c_u in db.keys()):
									await delete_per_chan_info(c_u)
					text = sorted(text)
					# text = ''.join(text)
					for t_ in text:
						await channel_finder.send(t_)
				except Exception as e:
					await channel_finder.send(e)

		elif(re.match(r'top ?[\d]+', msg.lower())):
			all_chn_score = {}
			range_ = int(re.search(r'\d+', msg.lower()).group(0))
			
			for chn_ in db.prefix('chnScore_'):
				chn_id = int(chn_.split('_')[-1])
				print(chn_id)
				chn = client.get_channel(chn_id)
				if(chn):
					all_chn_score[chn_] = db[str(chn_)]
				else:
					for c_u in db.prefix('c_'): # delete per chan info
						if(not(c_u.startswith('chnScore_'))):
							if(db[c_u] == str(chn_id)):
								await delete_per_chan_info(c_u)
								break;
			
			all_chn_score = {k: v for k, v in sorted(all_chn_score.items(), key=lambda item: item[1], reverse=True)}
			all_chn_score = {A:N for (A,N) in [x for x in all_chn_score.items()][:range_]}
			# print(all_chn_score)
			r_ = 1
			await channel_finder.send("="*20)
			for k, v in all_chn_score.items():
				# if(not(r>r_)):
				# 	break
				try:
					await client.wait_until_ready()
					# await channel_finder.send(f"<#{all_chn_score[r_]}>: {all_chn_score.keys()[r_]}")
					await channel_finder.send(f"**{r_}** <#{(k.split('_')[-1])}>: `{v}`")
					r_ += 1
				except Exception as e:
					await channel_finder.send(e)
			await channel_finder.send("="*20)

			
		elif(msg.startswith('<@') and msg.endswith('>')):
			m = msg.replace('!', '')
			# print(m)
			# print(client.get_channel(db['c_'+(m[2:-1])]))
			if ('c_'+(m[2:-1]) in db) and (not(client.get_channel(db['c_'+(m[2:-1])]) == None)):
				await channel_finder.send(f"<#{db['c_'+(m[2:-1])]}>" + '\n' + f"Score: {db['chnScore_'+str(db['c_'+(m[2:-1])])]}")
			else:
				m_member = client.get_user(int(m[2:-1]))
				await channel_finder.send("Unfortunately the user currently does not have a personal channel. But not to worry I will make one right now.")
				create_per_chan_return = await create_per_chan(m_member)
				if(create_per_chan_return == True):
					await channel_finder.send("Done creating a new channel for the user.")
				elif(create_per_chan_return == "Inv_UserNotMember"):
					await channel_finder.send("The user is not a member of our server. Can not create a channel for someone who is not a member of our server.")
				else:
					await channel_finder.send("Failed to create a new channel for the user.")
		else:
			print("NO USE: " + msg)
			await message.delete()
	
	elif(chn_id == 850962046527078441): #boosters-only
		if(not(server_booster_role in msg_auth_roles)):
			await message.delete()
			print("deleting message;")
			return;

	if("<@823554116356669521>" in msg or "<@!823554116356669521>" in msg):
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
		
		if(message.channel.id == 806413018056491031): #music
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

	elif(msg_lower == 'roll dice'):
		dice = await roll_a_dice()
		await message.reply(dice)

	
	last_time = time_now




async def help_msg(user):
	await client.wait_until_ready()
	help_msg = ""
	for command in commands:
		help_msg = help_msg + '`' + command + '`' + ": " + commands[command] + '\n'
	client.wait_until_ready()
	return(help_msg)





# secret message
async def secret_message(msg, sender=False, attachments=False):
	# await user.send('message'))
	if(re.match('\+\+secret_(msg|message)\s*@?([\w\d\s]+#\d{4})\s*', msg)):
		user = re.search('\+\+secret_(msg|message)\s*@([\w\d\s]+#\d{4})\s*', msg)[2]
		user = user.split('#')
		user = discord.utils.get(client.get_all_members(), name=user[0], discriminator=user[1])
	else:
		user_id = int(re.search('[\d]{17,19}', msg).group())
		user = await client.fetch_user(user_id)
	await client.wait_until_ready()
	print(user)
	if(user.id==823554116356669521):
		return("StC");
	if(sender):
		await sender.send(f"Sending secret message to *{str(user)} ({user.id})*")
	secret_name = re.search('^\+\+secret_(msg|message)\s*[\d]{17,19}\s*\[(.+)]\s*', msg)
	msg = re.sub('^\+\+secret_(msg|message)\s*[\d]{17,19}\s*(\[.+])?\s*', '', msg)
	msg = f"**You have a new secret message! {emojis['butterflies']}**\n" + msg
	if(secret_name):
		secret_name=secret_name.group(2)
		msg = msg + "\n*-" + secret_name + "*"
	try:
		await user.send(msg)
		# attachments
		if(len(attachments)>0):
			tmp_str = 'attachment' if (len(attachments)==1) else 'attachments'
			await user.send(f"The secret message contains {len(attachments)} {tmp_str}.")
			for attachment in attachments:
				filename = attachment.filename
				await attachment.save(filename)
				await client.wait_until_ready()
				await user.send(file=discord.File(filename))
				await client.wait_until_ready()
				os.remove(filename)

		print("secret message sent")
	except Exception as e:
		print(e)
		return(str(e))
	return(True)






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
		# answer = soup.find('div', class_="dd AnswrsV2").find(class_='compText')
		answer = soup.find('li', class_='va-top ov-h')
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
	html_text = requests.get('https://boards.4chan.org/lit/').text
	# print(html_text)
	soup = BeautifulSoup(html_text, 'lxml')
	thread = soup.find_all('div', class_='thread')[indx]
	await client.wait_until_ready()
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
		await client.wait_until_ready()
		image = discord.File("temp.jpg")
		await lit_chan.send(
		    f"**{emoji} {subject}**\n```\n{m}\n```", file=image
		    )#+ "https://" + img_src)
		await client.wait_until_ready()
		os.remove('temp.jpg') # delete the image
	else:
		await lit_chan.send(
		    f"**{emoji} {subject}**\n```\n{m}\n```"
		)


# run the bot
keep_alive()
client.run(os.getenv('TOKEN'))
