import random
import discord
import requests
from bs4 import BeautifulSoup
import json
from discord.ext import commands
from config import TOKEN
import re
import dpath.util
from youtube_dl import YoutubeDL

vc = None

YDL_OPTIONS = {'format': 'worstaudio/best', 'noplaylist': 'False', 'simulate': 'True',
               'preferredquality': '192', 'preferredcodec': 'mp3', 'key': 'FFmpegExtractAudio'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
client = commands.Bot(command_prefix='GG ')
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0'
PATTERNS = [
    re.compile(r'window\["ytInitialData"\] = (\{.+?\});'),
    re.compile(r'var ytInitialData = (\{.+?\});'),
]
session = requests.Session()
session.headers['User-Agent'] = USER_AGENT


def get_ytInitialData(url: str):
    rs = session.get(url)

    for pattern in PATTERNS:
        m = pattern.search(rs.text)
        if m:
            data_str = m.group(1)
            return json.loads(data_str)


def search_youtube(text_or_url: str):
    url = text_or_url
    data = get_ytInitialData(url)
    videos = dpath.util.values(data, '**/videoRenderer')
    if not videos:
        videos = dpath.util.values(data, '**/playlistVideoRenderer')
    return 'https://www.youtube.com/watch?v=' + videos[0]['videoId']


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
async def текст(ctx, *args):
    url = f'https://genius.com/api/search/multi?per_page=5&q={"%20".join(args)}'
    page = requests.get(url)
    url2 = page.text
    try:
        url2 = json.loads(url2)["response"]["sections"][1]["hits"][0]["result"]["url"]
    except:
        await ctx.send("по этому запросу ничего не найдено")
        return None
    print(url2)
    page2 = requests.get(url2)
    soup = BeautifulSoup(page2.text, "html.parser")
    res = soup.select_one("#lyrics-root > div.Lyrics__Container-sc-1ynbvzw-6.YYrds")
    autor = soup.select_one(".SongHeaderdesktop__Artist-sc-1effuo1-11")
    embed = discord.Embed(title="Sample Embed", url="https://realdrewdata.medium.com/", description="```" + autor.get_text() + "\n" + res.get_text("\n") + "```", color=0xa35de0)
    await ctx.send(embed=embed)


@client.command(pass_context=True)
async def брось_кубик(ctx, *args):
    try:
        rd = random.randint(int(args[0]), int(args[1]))
        await ctx.send(f'выпало {rd}')
    except:
        await ctx.send(f'с головой все в порядке?')


@client.command(pass_context=True)
async def играть(ctx, *arg):
    global vc
    url = f'https://www.youtube.com/results?search_query={"+".join(arg)}'
    video_url = search_youtube(url)
    try:
        vc = await ctx.message.author.voice.channel.connect()
    except:
        server = ctx.message.guild
        voice_channel = server.voice_client
        voice_channel.stop()
    with YoutubeDL(YDL_OPTIONS) as ydl:
        if 'https://' in video_url:
            info = ydl.extract_info(video_url, download=False)
        else:
            info = ydl.extract_info(f"ytsearch:{video_url}", download=False)['entries'][0]
    url = info['formats'][0]['url']
    vc.play(discord.FFmpegPCMAudio(executable="bin\\ffmpeg.exe", source=url, **FFMPEG_OPTIONS))


@client.command()
async def stop(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    voice_channel.stop()


@client.command()
async def pause(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    voice_channel.pause()


@client.command()
async def resume(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    voice_channel.resume()


client.run(TOKEN)
