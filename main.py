import random
import discord
import requests
from bs4 import BeautifulSoup
import json
from time import sleep
from discord.ext import commands
from config import TOKEN
from threading import Thread
from youtube_dl import YoutubeDL


vc = None
nxt = False
with open("playlists.json", "r") as file:
    pl = json.load(file)
    print(pl)
qe = []
YDL_OPTIONS = {'format': 'worstaudio/best', 'noplaylist': 'False', 'simulate': 'True',
               'preferredquality': '192', 'preferredcodec': 'mp3', 'key': 'FFmpegExtractAudio'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
client = commands.Bot(command_prefix='GG ')


def wait(ctx):
    global vc, nxt, qe
    print(qe)
    while qe:
        vc.stop()
        src = qe[0]
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(f"ytsearch:{src}", download=False)['entries'][0]
        url = info['formats'][0]['url']
        lenght = info['duration']
        vc.play(discord.FFmpegPCMAudio(executable="bin\\ffmpeg.exe", source=url, **FFMPEG_OPTIONS))
        print(lenght)
        for i in range(int(lenght) + 1):
            print(i)
            if nxt:
                print('wqww')
                nxt = False
                break
            sleep(1)
        del qe[0]


@client.command()
async def анек(ctx):
    with open('aneks.txt', 'r') as file:
        data = file.read().split('\naboba\n')
        for el in data:
            if not el:
                del data[data.index(el)]
    await ctx.send(random.choice(data))


@client.command(pass_context=True)
async def запоминай_анек(ctx, *args):
    anek = ' '.join(args)
    with open('aneks.txt', 'r') as file:
        data = file.read().split('\naboba\n')
    with open('aneks.txt', mode='a') as file:
        if anek not in data:
            file.write(anek)
            file.write('\naboba\n')
            await ctx.send('запомнил')
        else:
            await ctx.send('уже знаю')


@client.command(pass_context=True)
async def русская_рулетка(ctx, *args):
    rnd = random.randint(1, 6)
    if not 0 < int(args[0]) < 6:
        await ctx.send(f'застрелян за читерство')
        return None
    if rnd == int(args[0]):
        await ctx.send(f'застрелился')
    else:
        await ctx.send(f'стрелял, но не попал. Выпало {rnd}')


@client.command(pass_context=True)
async def text(ctx, *args):
    url = f'https://genius.com/api/search/multi?per_page=5&q={"%20".join(args)}'
    page = requests.get(url)
    url2 = page.text
    try:
        url2 = json.loads(url2)["response"]["sections"][1]["hits"][0]["result"]["url"]
    except:
        await ctx.send("не найдено текста по этому запросу")
        return None
    print(url2)
    page2 = requests.get(url2)
    soup = BeautifulSoup(page2.text, "html.parser")
    res = soup.select_one("#lyrics-root > div.Lyrics__Container-sc-1ynbvzw-6.YYrds")
    autor = soup.select_one(".SongHeaderdesktop__Artist-sc-1effuo1-11")
    embed = discord.Embed(title=f"текст вашей песни:", url="https://realdrewdata.medium.com/", description="```" + autor.get_text() + "\n" + res.get_text("\n") + "```", color=0xa35de0)
    await ctx.send(embed=embed)


@client.command(pass_context=True)
async def брось_кубик(ctx, *args):
    try:
        rd = random.randint(int(args[0]), int(args[1]))
        await ctx.send(f'выпало {rd}')
    except:
        await ctx.send(f'с головой все в порядке?')


@client.command(pass_context=True)
async def play(ctx, *arg):
    global vc, qe
    if arg and 'list:' in arg[0]:
        if any([1 if i in qe else 0 for i in pl[arg[1]]]):
            await ctx.send('плейлист уже в очереди')
            return None
        try:
            plst = pl[arg[1]]
            #print(plst)
        except:
            await ctx.send(f"нет плейлиста с таким именем")
            return None
        qe = plst + qe
        print(qe)
    elif arg:
        print(1)
        qe.insert(0, arg)
    try:
        print(2)
        vc = await ctx.message.author.voice.channel.connect()
    except:
        if not vc:
            await ctx.send('вы не в голосовом канале')
            return None
        await stop(ctx, clear=False)
    await ctx.send('включаю...')
    print(qe, 'fdsjj')
    th1 = Thread(target=wait, args=[ctx])
    th1.start()


@client.command()
async def stop(ctx, clear=True):
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client
        voice_channel.stop()
        if clear:
            qe.clear()
    except:
        await ctx.send('музыка сейчас не играет, воспользуйтесь командой GG play')



@client.command()
async def pause(ctx):
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client
        voice_channel.pause()
    except:
        await ctx.send('музыка сейчас не играет, воспользуйтесь командой GG play')



@client.command()
async def resume(ctx):
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client
        voice_channel.resume()
    except:
        await ctx.send('музыка сейчас не играет, воспользуйтесь командой GG play')


@client.command()
async def leave(ctx):
    global vc
    try:
        voice_client = ctx.message.guild.voice_client
        await voice_client.disconnect()
    except:
        await ctx.send('бот не в голосовом канале')


@client.command(pass_context=True)
async def queue(ctx, *arg):
    global qe
    if arg and 'list:' in arg[0]:
        try:
            if all([1 if i in qe else 0 for i in pl[arg[1]]]):
                await ctx.send('плейлист уже в очереди')
                return None
            qe.extend(pl[arg[1]])
        except:
            await ctx.send(f"нет плейлиста с таким именем")
            return None
    else:
        if arg in qe:
            await ctx.send('уже добавлено')
            return None
        qe.append(' '.join(arg))
    await ctx.send('добавлено')


@client.command()
async def next(ctx):
    global nxt
    nxt = True
    if qe:
        await ctx.send('переключаю..')
    else:
        await ctx.send('ваш плейлист кончился')
        await stop(ctx)


@client.command()
async def commands(ctx):
    txt = 'GG queue {название песни} - добавляет песню в конец очереди\nGG play {название/list: {плейлист}}/{ничего} добавляет песню/плейлист в начало очереди и воспроизводит ее\nGG text {название} - выводит текст песни по названию\nGG next - переключает очередь на следующую песню\nGG pause - пауза\nGG resume - снятие с паузы\nGG leave - выход из голосового канала\nGG create_playlist {название} {песни через запятую и пробел} - создает плейлист с выбранными песнями\nGG add_to_list {название} {песни через запятую и пробел} - добавляет выбранные песни в конец выбранного плейлиста\nGG rewiew {название плейлиста/ничего} - обзор вашей текущей очереди/плейлиста'
    embed = discord.Embed(title=f"комманды этого бота:", url="https://realdrewdata.medium.com/", description=txt, color=0xA35DE0)
    await ctx.send(embed=embed)


@client.command(pass_context=True)
async def create_playlist(ctx, *arg):
    name = arg[0]
    pl[name] = ' '.join(arg[1:]).split(', ')
    with open("playlists.json", "w") as write_file:
        json.dump(pl, write_file)
    await ctx.send('плейлист создан')


@client.command(pass_context=True)
async def add_to_list(ctx, *arg):
    try:
        e = ' '.join(arg[1:]).split(', ')
        if all([1 if i in pl[arg[0]] else 0 for i in e]):
            qe.clear()
        pl[arg[0]].extend(e)
        with open("playlists.json", "w") as write_file:
            json.dump(pl, write_file)
        print(pl)
        await ctx.send('добавлено в плейлист')
    except:
        await ctx.send(f"нет плейлиста с таким именем")


@client.command(pass_cotext=True)
async def rewiew(ctx, *arg):
    global qe
    if arg:
        lname = ' '.join(arg)
        try:
            txt = '\n'.join(pl[lname])
        except:
            await ctx.send("нет плейлиста с таким именем")
    else:
        if not qe:
            await ctx.send("вы еще не добавили элементов в очередь")
            return None
        txt = '\n'.join(qe)
    embed = discord.Embed(title=f"плейлист {lname}" if arg else f"ваша текущая очередь:", url="https://realdrewdata.medium.com/", description=txt, color=0xA35DE0)
    await ctx.send(embed=embed)


client.run(TOKEN)
