import random
import discord
import requests
from bs4 import BeautifulSoup
import os
import json
from discord.ext import commands
from config import TOKEN


client = discord.Client()
bot = commands.Bot(command_prefix='%')
if not os.path.isfile('bad_words.txt'):
    with open('bad_words.txt', 'w') as file:
        file.write('лох')
        file.write(' ')
anek = '- Завтрак съешь сам, обед подели с другом, ужин отдай врагу.\n- Товарищ генерал, а можно я буду вашим врагом?\n- Можно! Расстрелять!!'
if not os.path.isfile('aneks.txt'):
    with open('aneks.txt', 'w') as file:
        file.write(anek)
        file.write('\naboba\n')


def bad(data):
    with open('bad_words.txt', 'r') as file:
        bad_words = file.read().split()
    for elem in data:
        for w in bad_words:
            if elem == w:
                return w
    return False


@client.event
async def on_message(message):
    if message.author == client.user:
        return None
    #print(message.content)
    if 'путин' in message.content.lower():
        await message.channel.send('Россия священная наша держава')
        await message.channel.send('Россия великая наша страна')
    elif '%info' in message.content.lower():
        await message.channel.send('я могу присылать анекдоты, запоминать анекдоты, писать треки шадоврейза(и не только), и еще я тайный агент Кремля')
    elif 'россия' in message.content.lower():
        await message.channel.send('Владимир Владимирович Путин - президент мира')
    elif 'америк' in message.content.lower():
        await message.channel.send('ядерная ракета направлена, подготовка к уничтожению пентагона')
    elif '%' in message.content.lower() and 'анек' in message.content.lower() and 'бот' in message.content.lower():
        with open('aneks.txt', 'r') as file:
            data = file.read().split('\naboba\n')
            for el in data:
                if not el:
                    del data[data.index(el)]
            await message.channel.send(random.choice(data))
            print(data)
    elif '%запоминай анек:' in message.content.lower():
        with open('aneks.txt', 'r') as file:
            data = file.read().split('\naboba\n')
        with open('aneks.txt', mode='a') as file:
            if message.content[17:] not in data:
                file.write(message.content[17:])
                file.write('\naboba\n')
                await message.channel.send('запомнил')
            else:
                await message.channel.send('уже знаю')
    elif '%дай текст песни:' in message.content.lower():
        msg = message.content.lower().split()
        if not os.path.isfile(msg[3] + '.txt'):
            autors = ('shadowraze')
            await message.channel.send(f'разраб такого не знает, доступные авторы - {autors}')
        else:
            with open(msg[3] + '.txt', 'r', encoding='utf-8') as file:
                data = file.read().split('\naboba')
                for el in data:
                    if not el:
                        del data[data.index(el)]
                if len(msg) > 4:
                    if not msg[4].isdigit():
                        await message.channel.send(f'Ты тупой? Когда {msg[4]} стало цифрой?')
                        return None
                    try:
                        await message.channel.send(data[int(msg[4]) - 1])
                    except:
                        await message.channel.send(f'у нас только {len(data)} песен')
                else:
                    await message.channel.send(random.choice(data))
    elif bad(message.content.lower().split()):
        w = bad(message.content.lower().split())
        await message.channel.send(f'{message.author}, сам {w}')
    elif '%добавить плохое слово:' in message.content.lower():
        msg = message.content.split()
        with open('bad_words.txt', 'r') as file:
            data = file.read().split()
        print(msg)
        with open('bad_words.txt', mode='a') as file:
            if msg[3] not in data:
                file.write(msg[3])
                file.write(' ')
                await message.channel.send('запомнил')
            else:
                await message.channel.send('уже знаю')
    elif '%commands' in message.content.lower():
        await message.channel.send('%info - информация\n%бот анекдот - рандомный анекдот\n%запоминай анек: {текст} - бот запомнит анекдот\n'
                                   '%дай текст песни: {автор} {номер} - пишет текст выбранной песни\n%добавить плохое слово: {слово} - запоминает плохое слово и ругает за его использование')
    elif '%брось кубик' in message.content.lower():
        msg = message.content.split()
        try:
            rd = random.randint(int(msg[2]), int(msg[3]))
            await message.channel.send(f'выпало {rd}')
        except:
            await message.channel.send(f'{message.author}, ты ебанутый?')

    elif '%русская рулетка' in message.content.lower():
        msg = message.content.split()
        rnd = random.randint(1, 6)
        if not 0 < int(msg[2]) < 6:
            await message.channel.send(f'{message.author} застрелян за читерство')
            return None
        if rnd == int(msg[2]):
            await message.channel.send(f'{message.author} застрелился')
        else:
            await message.channel.send(f'{message.author} стрелял, но не попал. Выпало {rnd}')
    elif '%искать на genius:' in message.content.lower():
        msg = message.content.split()
        url = f'https://genius.com/api/search/multi?per_page=5&q={"%20".join(msg[3:])}'
        try:
            page = requests.get(url)
        except:
            await message.channel.send('ссылка не открывается')
            return None
        url2 = page.text
        url2 = json.loads(url2)["response"]["sections"][1]["hits"][0]["result"]["url"]
        page2 = requests.get(url2)
        soup = BeautifulSoup(page2.text, "html.parser")
        res = soup.select_one("#lyrics-root > div.Lyrics__Container-sc-1ynbvzw-6.YYrds")
        print(res)
        await message.channel.send("```" + res.get_text("\n") + "```")


client.run(TOKEN)
bot.run(TOKEN)
