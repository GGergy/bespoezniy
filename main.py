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
from sqlaver import insert_blob, read_blob_data

vc = None
nxt = False
pl = {}
qe = []
YDL_OPTIONS = {'format': 'worstaudio/best', 'noplaylist': 'False', 'simulate': 'True',
               'preferredquality': '192', 'preferredcodec': 'mp3', 'key': 'FFmpegExtractAudio'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
client = commands.Bot(command_prefix='GG ')


def wait(ctx, lst):
    global vc, nxt
    qdl = False
    if lst == qe:
        qdl = True
    while lst:
        vc.stop()
        src = ' '.join(lst[0]) if qdl else lst[0]
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(f"ytsearch:{src}", download=False)['entries'][0]
        url = info['formats'][0]['url']
        lenght = info['duration']
        vc.play(discord.FFmpegPCMAudio(executable="bin\\ffmpeg.exe", source=url, **FFMPEG_OPTIONS))
        #insert_blob(src, discord.FFmpegPCMAudio(executable="bin\\ffmpeg.exe", source=url, **FFMPEG_OPTIONS).read())
        del lst[0]
        for i in range(int(lenght) + 1):
            if nxt:
                nxt = False
                print(1)
                break
            sleep(1)
    if qdl:
        qe.clear()


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
    plst = False
    if 'list:' in arg[0]:
        plst = pl[arg[1]]
        print(plst)
    elif arg:
        qe.insert(0, arg)
    try:
        vc = await ctx.message.author.voice.channel.connect()
    except:
        if not vc:
            await ctx.send('вы не в голосовом канале')
            return None
        await stop(ctx)
    await ctx.send('включаю...')
    print(plst.copy())
    th1 = Thread(target=wait, args=[ctx, plst.copy() if plst else qe])
    th1.start()


@client.command()
async def stop(ctx):
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client
        voice_channel.stop()
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
    if arg in qe:
        await ctx.send('уже добавлено')
        return None
    qe.append(arg)
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
    txt = 'GG queue {название песни} - добавляет песню в конец очереди\nGG play {название}/{ничего} добавляет песню в начало очереди и воспроизводит ее\nGG text {название} - выводит текст песни по названию\nGG next - переключает очередь на следующую песню\nGG pause - пауза\nGG resume - снятие с паузы\nGG leave - выход из голосового канала'
    embed = discord.Embed(title=f"комманды этого бота:", url="https://realdrewdata.medium.com/", description=txt, color=0xA35DE0)
    await ctx.send(embed=embed)


@client.command(pass_context=True)
async def create_playlist(ctx, *arg):
    name = arg[0]
    pl[name] = ' '.join(arg[1:]).split(', ')
    print(pl)
    await ctx.send('плейлист создан')




client.run(TOKEN)
