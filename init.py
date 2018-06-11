import random
import discord
import datetime
import urllib.request
import json
import os
import inflect

# Create ur own directory with variables.py
# where would be your BOT token and another stuff
from modules import variables

from collections import OrderedDict
from discord.ext import commands

max_records_in_leaderboard = 1500
command_prefix = 'nap?'.upper()
leaderboard = 'leaderboard.txt'
settings = 'settings.txt'
inflect_engine = inflect.engine()

class KartonBot:
    def __init__(self, bot):
        self.bot = bot
        self.load_leader_board()
        self.load_settings()
        self.dateLastCheck = datetime.datetime(2010, 1, 1)
        self.jsonINFO = {}
        self.gameCache = {}
        self.newGame()

        self.server_flags = {}
        self.flags = [
            ":flag_ac:",":flag_af:",":flag_al:",":flag_dz:",":flag_ad:",":flag_ao:",":flag_ai:",
            ":flag_ag:",":flag_ar:",":flag_am:",":flag_aw:",":flag_au:",":flag_at:",":flag_az:",
            ":flag_bs:",":flag_bh:",":flag_bd:",":flag_bb:",":flag_by:",":flag_be:",":flag_bz:",
            ":flag_bj:",":flag_bm:",":flag_bt:",":flag_bo:",":flag_ba:",":flag_bw:",":flag_br:",
            ":flag_bn:",":flag_bg:",":flag_bf:",":flag_bi:",":flag_cv:",":flag_kh:",":flag_cm:",
            ":flag_ca:",":flag_ky:",":flag_cf:",":flag_td:",":flag_cl:",":flag_cn:",":flag_co:",
            ":flag_km:",":flag_cg:",":flag_cd:",":flag_cr:",":flag_hr:",":flag_cu:",":flag_cy:",
            ":flag_cz:",":flag_dk:",":flag_dj:",":flag_dm:",":flag_do:",":flag_ec:",":flag_eg:",
            ":flag_sv:",":flag_gq:",":flag_er:",":flag_ee:",":flag_et:",":flag_fk:",":flag_fo:",
            ":flag_fj:",":flag_fi:",":flag_fr:",":flag_pf:",":flag_ga:",":flag_gm:",":flag_ge:",
            ":flag_de:",":flag_gh:",":flag_gi:",":flag_gr:",":flag_gl:",":flag_gd:",":flag_gu:",
            ":flag_gt:",":flag_gn:",":flag_gw:",":flag_gy:",":flag_ht:",":flag_hn:",":flag_hk:",
            ":flag_hu:",":flag_is:",":flag_in:",":flag_id:",":flag_ir:",":flag_iq:",":flag_ie:",
            ":flag_il:",":flag_it:",":flag_ci:",":flag_jm:",":flag_jp:",":flag_je:",":flag_jo:",
            ":flag_kz:",":flag_ke:",":flag_ki:",":flag_xk:",":flag_kw:",":flag_kg:",":flag_la:",
            ":flag_lv:",":flag_lb:",":flag_ls:",":flag_lr:",":flag_ly:",":flag_li:",":flag_lt:",
            ":flag_lu:",":flag_mo:",":flag_mk:",":flag_mg:",":flag_mw:",":flag_my:",":flag_mv:",
            ":flag_ml:",":flag_no:",":flag_sj:",":flag_bv:",":flag_hm:",":flag_gg:",":flag_re:",
            ":flag_ax:",":flag_ve:",":flag_ug:",":flag_cp:",":flag_dg:",":flag_pm:",":flag_bl:",
            ":flag_ta:",":flag_va:",":flag_ax:",":flag_uz:",":gay_pride_flag:"
        ]

    def load_leader_board(self):
        if os.path.exists(leaderboard):
            with open(leaderboard, 'r') as lFile:
                try:
                    self.leaderboard = json.loads(lFile.read())                
                except:
                    self.leaderboard = [[], {}]        
        else:
            self.leaderboard = [[], {}]

    def load_settings(self):
        if os.path.exists(settings):
            with open(settings, 'r') as lFile:  
                try:
                    self.settings = json.loads(lFile.read())    
                except:
                    self.settings = dict()              
        else:
            self.settings = dict()    

    def save_leader_board(self):
        # self.leaderboard = {x: OrderedDict(sorted(self.leaderboard[x].items(), key=lambda t: self.leaderboard[x][t[0]]['try'])) for x in self.leaderboard}     
        self.leaderboard[0] = sorted(self.leaderboard[0], key=lambda x:(x['try'], x['time']))[:max_records_in_leaderboard]
        with open (leaderboard, 'w') as lFile:
            lFile.write(json.dumps(self.leaderboard))

    def save_settings(self):
        with open (settings, 'w') as lFile:
            lFile.write(json.dumps(self.settings))                

    def mindANumber(self):
        while True:
            num = random.randrange(1000, 9999)
            if (not self.checkNumber(str(num))):
                continue
            else:
                break
        return str(num)

    def getStringDict(self, index, item, show_all):
        answer = {}
        cur_flag = self.server_flags.get(item['server'])
        if show_all:
            if cur_flag == None:
                cur_flag = random.choice(self.flags)
                self.server_flags[item['server']] = cur_flag 
            answer['flag'] = cur_flag
        else:
            answer['flag'] = ''  

        answer['smile'] = ""
        for num in str(index + 1):
            answer['smile'] = f"{answer['smile']}:{inflect_engine.number_to_words(num)}:"
        
        answer['server_name'] = f" ({item['servername'][:15]})" if show_all else ''
        answer['display_name'] = item['player']
        answer['try'] = item['try']
        answer['time'] = item['time']
        answer['number'] = item['number']
        answer['games'] = self.leaderboard[1].get(item['player'], 0)

        return answer        

    def newGame(self):
        self.player = None
    
    def checkNumber(self, num_): 
        return num_.isdigit() and len(num_) == 4 and len(list(num_)) == len(list(set(list(num_)))) and num_[0] != '0'

    def getInfo(self):
        if self.dateLastCheck + datetime.timedelta(minutes=10) < datetime.datetime.now():
            resp = urllib.request.urlopen("http://ip-api.com/json").read()
            # ubuntu support
            if type(resp) == bytes:
                resp = resp.decode('utf-8')
            self.jsonINFO = json.loads(resp) 
        return self.jsonINFO

    def compareNumbers(self, playerNum, computerNum):
        cows = bulls = 0
        bulls = sum([1 for i in range(4) if computerNum[i] == playerNum[i]])
        cows = sum([1 for i in range(4) for j in range(4) if i != j and computerNum[i] == playerNum[j]])    
        return (cows, bulls)        

    def is_bot_playing_here(self, disc_message):
        playing_info = self.gameCache.get(f"{disc_message.channel.id}{disc_message.channel.server.id}", False)
        return False if playing_info == False else True   

    async def on_ready(self):
        print('Картон запущен :3')
        await bot.change_presence(game=discord.Game(name='nap?help', type=0))

    async def on_message(self, message):

        def check(msg):
            if self.player == None:
                return self.checkNumber(msg.content) and not msg.author.bot
            else:
                return self.checkNumber(msg.content) and not msg.author.bot and msg.author.id == self.player

        if message.author.bot:
            return

        player_display_name = f"{message.author.display_name}#{message.author.discriminator}"

        # COMMANDS
        if message.content.upper().startswith(command_prefix):
            com_message = message.content[len(command_prefix):].upper()
            server_channel_id = f"{message.channel.id}{message.channel.server.id}"
            if com_message in ["PLAY", "PLAYWITHME", "PL", "PWM"]:

                if self.settings.get(message.channel.server.id, []) is not ['']:
                    if message.channel.name.upper() not in self.settings[message.channel.server.id]:
                        return

                if self.is_bot_playing_here(message):
                    await bot.send_message(message.channel, "А я уже играю прямо сейчас, мур")
                    return 

                if com_message in ["PLAYWITHME", "PWM"]:
                    self.player = message.author.id
                else:
                    self.player = None

                self.gameCache[server_channel_id] = {"player" : self.player}
                self.gameCache[server_channel_id]['myst_num'] = self.mindANumber()
                self.gameCache[server_channel_id]['time'] = datetime.datetime.now()
                self.gameCache[server_channel_id]['tries'] = 1
                self.gameCache[server_channel_id]['try_list'] = OrderedDict()

                if self.gameCache[server_channel_id]['player'] == None:
                    await bot.send_message(message.channel, "Хорошо, давайте играть! Я загадала число..")   
                else:
                    await bot.send_message(message.channel, f"Хорошо, давай играть, <@{self.gameCache[server_channel_id]['player']}>! Я загадала число.. {self.gameCache[server_channel_id]['myst_num']}")
                while True:
                    answer = await bot.wait_for_message(channel=message.channel, timeout=120, check=check)
                    if answer == None:
                        await bot.send_message(message.channel, "Эх.. Ну и молчите..")
                        self.gameCache.pop(server_channel_id, None)
                        self.newGame()
                        break
                    cows, bulls = self.compareNumbers(answer.content, self.gameCache[server_channel_id]['myst_num'])
                    self.gameCache[server_channel_id]['try_list'][len(self.gameCache[server_channel_id]['try_list'])] = {
                        'player' : player_display_name,
                        'number' : answer.content,
                        'cows' : cows,
                        'bulls' : bulls
                    }  
                    if bulls == 4:
                        deltatime = datetime.datetime.now() - self.gameCache[server_channel_id]['time']
                        # time_text = "%0.3f" % ((deltatime.seconds * 1000000 + deltatime.microseconds) / 1000000)
                        time_text = f"{((deltatime.seconds * 1000000 + deltatime.microseconds) / 1000000)}:.2f"
                        await bot.send_message(message.channel, f"Да! <@{answer.author.id}> отгадал число :3\nПопыток: {self.gameCache[server_channel_id]['tries']}, время: {time_text} секунд")
                        if self.gameCache[server_channel_id]['player'] != None:
                            cur_data = [i for i, t in enumerate(self.leaderboard[0]) if t['player'] == player_display_name and t['server'] == message.server.id]
                            message_text = ""
                            if cur_data != []:
                                if self.leaderboard[0][cur_data[0]]['try'] > self.gameCache[server_channel_id]['tries']:
                                    last_tries = self.leaderboard[0][cur_data[0]]['try']
                                    message_text = f"Уоо! <@{message.author.id}> только что про побил свой рекорд!\nБыло попыток: {last_tries}, стало: {self.gameCache[server_channel_id]['tries']}\nТы молодец!\n"
                                if float(self.leaderboard[0][cur_data[0]]['time']) > float(time_text):   
                                    last_time = self.leaderboard[0][cur_data[0]]['time']
                                    message_text += f"Ура! <@{message.author.id}> только что про побил свой временной рекорд!\nБыло время: {last_time}, стало: {time_text}\nТы молодец!\n"
                            else:
                                message_text = f"Поздравляю с первой победой, <@{message.author.id}>! " 

                            if message_text != "":
                                if cur_data != []:
                                    self.leaderboard[0].pop(cur_data[0])    
                                await bot.send_message(message.channel, message_text[:-1])
                            
                            self.leaderboard[0].append({
                                    'server' : message.server.id,
                                    'servername' : message.server.name,
                                    'player' : player_display_name,
                                    'number' : self.gameCache[server_channel_id]['myst_num'],
                                    'time' : time_text,
                                    'try' : self.gameCache[server_channel_id]['tries'],
                                    'log' : self.gameCache[server_channel_id]['try_list']
                                })

                            games_played = self.leaderboard[1].get(player_display_name, 0)
                            self.leaderboard[1][player_display_name] = games_played + 1
                            self.save_leader_board()
                        self.gameCache.pop(f"{message.channel.id}{message.channel.server.id}", None)
                        self.newGame()
                        break
                    else:                                              
                        if len(self.gameCache[server_channel_id]['try_list']) == 11:
                            self.gameCache[server_channel_id]['try_list'].pop(0)
                        await bot.send_message(message.channel, f"Хмм.. {answer.content}, здесь {cows} коров и {bulls} быков")
                        self.gameCache[server_channel_id]['tries'] += 1
            elif com_message in ["PROGRESS", "P"]:
                if self.is_bot_playing_here(message):
                    if len(self.gameCache[server_channel_id]['try_list']) != 0:
                        message_text = ""
                        for item in self.gameCache[server_channel_id]['try_list'].items():
                            message_text += f"({item[1]['player']}) {item[1]['number']} : {item[1]['cows']} коров, {item[1]['bulls']} быков\n"
                        await bot.send_message(message.channel, f"Игроки пытались отгадать вот так:```{message_text[:-1]}```")
                else:
                    await bot.send_message(message.channel, "А? Что? Я не играю сейчас здесь")    
                        
            elif com_message in ["CITY", "C"]:
                city = self.getInfo()
                await bot.send_message(message.channel, f"Я живу в городе {city['city']} ({city['country']}) и мой провайдер {city['org']}")
            elif com_message in ["HELP", "H"]:
                await bot.send_message(message.channel,"Все очень просто! Мои картонные команды:\n**kar?city** или **kar?c** - узнать, откуда я запущена сейчас :3\n**kar?play** или **kar?pl** - поиграть в игру 'Быки и коровы'\n**kar?playhelp** или **kar?ph** - правила игры 'Быки и коровы'\n**kar?progress** или **kar?p**- детализация текущих ходов\n**kar?playwithme** или **kar?pwm**- битва один на один!:exclamation:Только тут записываются рекорды\n**kar?leaderboard** или **kar?lb**- таблица рекордов на этом сервере\n**kar?leaderboardall** или **kar?lball**- таблица рекордов среди всех\n**kar?tleaderboard** или **kar?tlb**- таблица рекордов на этом сервере (сортировка по времени)\n**kar?tleaderboardall** или **kar?tlball**- таблица рекордов среди всех (сортировка по времени)")
            elif com_message in ["PLAYHELP", "PH"]:
                await bot.send_message(message.channel, "```Я задумываю тайное 4-значное число с неповторяющимися цифрами. Игрок делает первую попытку отгадать число. Попытка — это 4-значное число с неповторяющимися цифрами, сообщаемое мне!. Я сообщаю в ответ, сколько цифр угадано без совпадения с их позициями в тайном числе (то есть количество коров) и сколько угадано вплоть до позиции в тайном числе (то есть количество быков)\nТвоя задача определить тайное число, используя информацию о быках и коровах :3```")
            elif com_message in ["LEADERBOARD", "LB", "LEADERBOARDALL", "LBALL", "TLEADERBOARD", "TLB", "TLEADERBOARDALL", "TLBALL", "GLEADERBOARD", "GLB", "GLEADERBOARDALL", "GLBALL", "R", "RATING", "TR", "TRATING", "GR", "GRATING", "RALL", "RATINGALL", "TRALL", "TRATINGALL", "GRALL", "GRATINGALL"]:
                message_text = ""
                records = self.leaderboard[0] 
                
                show_all = "ALL" in com_message 
                if not show_all:
                    records = [r for r in records if r['server'] == message.server.id]
                    
                if com_message.startswith("T"):
                    records = sorted(records, key=lambda x:x['time'])
                elif com_message.startswith("G"):
                    for item in records:
                        item['games'] = self.leaderboard[1].get(item['player'], 0)
                    records = sorted(records, key=lambda x:x['games'], reverse=True)

                unique = []
                i = 0
                while i < len(records):
                    if records[i]['player'] in unique:
                        records.pop(i)
                    else:
                        unique.append(records[i]['player'])
                        i += 1

                if com_message in ["R", "RATING", "TR", "TRATING", "GR", "GRATING", "RALL", "RATINGALL", "TRALL", "TRATINGALL", "GRALL", "GRATINGALL"]:         
                    try:
                        player_index = records.index(next(s for s in records if s['player'] == player_display_name))
                    except StopIteration:
                        await bot.send_message(message.channel, f"<@{message.author.id}>, тебя еще нет в таблице лучших. Попробуй поиграть в игру!")
                        return
                        
                    if player_index < 10:
                        player_list = list(range(player_index + 1))
                    else:
                        player_list = [0, 1, 2]
                        player_list += [player_index - 2] + [player_index - 1] + [player_index]
                        player_list = list(set(player_list))
                        
                        records_new = []

                        for index in player_list:
                            try:
                                temp = records[index]
                            except:
                                records_new.append(temp)

                        records = records_new.copy()
                        del records_new
                else:                        
                    records = records[:9]
                
                if records == []:
                    message_text = "Списки лидеров еще пустые.."
                else:
                    self.server_flags = {}
                    for index, item in enumerate(records):
                        string_dict = self.getStringDict(index, item, show_all)
                        message_text += "%(smile)s%(flag)s **%(display_name)s**%(server_name)s: Попыток: **%(try)s**, Число: **%(number)s**, Время: **%(time)s**s. Игр: **%(games)d**\n" % string_dict
                    message_text = f"Списки лучших! ^_^:\n{message_text[:-1]}" 
                await bot.send_message(message.channel, message_text)
                del records
            elif com_message in ["DETAILME", "DM"]:            
                try:
                    log = next(s for s in self.leaderboard[0] if s['player'] == player_display_name and s['server'] == message.server.id)['log']
                except:
                    log = None
                if log == None:
                    await bot.send_message(message.channel, f"<@{message.author.id}>, тебя еще нет в таблице лучших. Попробуй поиграть в игру!")
                    return
                else:
                    message_text = ""
                    for index, line in enumerate(log.items()):
                        message_text += "Ход % 3d: Число: %s, Коров: %d, Быков: %d\n" % (index + 1, line[1]['number'], line[1]['cows'], line[1]['bulls'])
                    await bot.send_message(message.channel, "Детализация твоего рекорда, <@%s>:\n```%s```" % (message.author.id, message_text[:-1]))
            elif com_message.startswith("SET"):
                if message.author.server_permissions.administrator or player_display_name == variables.DUDE_WHO_CAN_MAKE_ALL:
                    channels_list = message.content[len(command_prefix + "?SET"):].upper().split(' ')
                    self.settings[message.channel.server.id] = [channel.upper() for channel in channels_list]
                    if channels_list == ['']:
                        message_text = "Поняла! Настройки каналов сброшены"
                    else:
                        message_text = "Поняла! Я буду играть только в каналах: " + ", ".join(channels_list)
                    self.save_settings()
                else:
                    message_text = "Стой.. ты не можешь мною командовать"
                await bot.send_message(message.channel, message_text)
            else:
                if random.randint(1, 1000) <= 5:
                    messagetype = random.choice([1, 2])
                    if messagetype == 1:
                        message_text = random.choice(['зевает', 'чешется', 'щурится', 'чешет носик', 'Апч-хи!'])
                        await bot.send_message(message.channel, "*%s*" % message_text)
                    elif messagetype == 2:
                        message_text = random.choice([
                            'Ты так часто пишешь, <@%s>...', 
                            'А я знаю тебя, <@%s> :3', 
                            '<@%s>, кусь тебя!', 
                            '<@%s>, и тебе привет С:', 
                            'Кто ты без своего айфона, <@%s>?'
                        ])
                        await bot.send_message(message.channel, message_text % message.author.id)
                elif "КАРТОН" in message.content.upper() and random.randint(1, 100) <= 45:
                    text_list = [
                        "Что? Кто сказал 'картон'?",
                        "Вы меня звали? Я тут.",
                        "Можно назвать твердой бумагой еще",
                        "Поделки детают из меня :3",
                        "Это только на первый взгляд так, ясно?",
                        "Обращайтесь ко мне через команды лучше..",
                        "Здесь! ^^"
                    ]
                    await bot.send_message(message.channel, random.choice(text_list))    


def setup(bot):
    bot.add_cog(KartonBot(bot))


bot = commands.Bot(command_prefix="a8nytphfa3dfsd27ayc-kghps")
setup(bot)

# Картонка
# bot.run(variables.TOKEN_KARTON)

# Напальчник
bot.run(variables.TOKEN_NAP)
