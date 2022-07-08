import discord
from discord.ext import commands
from config import TOKEN


client = discord.Client()
bot = commands.Bot(command_prefix='%')
aneks = '- Завтрак съешь сам, обед подели с другом, ужин отдай врагу.\n- Товарищ генерал, а можно я буду вашим врагом?\n- Можно! Расстрелять!!'


@client.event
async def on_message(message):
    if message.author == client.user:
        return None
    print(message.content)
    if 'путин' in message.content.lower():
        await message.channel.send('Россия священная наша держава')
        await message.channel.send('Россия великая наша страна')
    elif 'россия' in message.content.lower():
        await message.channel.send('Владимир Владимирович Путин - президент мира')
    elif 'америк' in message.content.lower():
        await message.channel.send('ядерная ракета направлена, подготовка к уничтожению пентагона')
    elif 'анек' in message.content.lower() and 'бот' in message.content.lower():
        await message.channel.send(aneks)


client.run(TOKEN)
bot.run(TOKEN)
