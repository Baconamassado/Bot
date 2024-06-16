import discord
from discord.ext import commands
import os
import requests
import zipfile
import sys

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
OWNER_ID = os.environ['ID']  # Substitua pelo seu ID do Discord
GITHUB_REPO_URL = os.environ['Fezes']  # Substitua pela URL do seu repositório GitHub
TOKEN = os.environ['Token']  # Substitua pelo token do seu bot

@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} has connected to Discord!')

def is_owner(ctx):
    return ctx.author.id == int(OWNER_ID)

@bot.command()
@commands.check(is_owner)
async def dmall(ctx, *, message: str):
    for member in ctx.guild.members:
        if not member.bot:
            try:
                await member.send(message)
            except discord.Forbidden:
                print(f"Could not send message to {member.name}")

@bot.command()
@commands.check(is_owner)
async def fm(ctx):
    first_message = None
    async for message in ctx.channel.history(oldest_first=True, limit=1):
        first_message = message
    if first_message:
        await ctx.send(f"A primeira mensagem deste canal é: {first_message.jump_url}")
    else:
        await ctx.send("Não foi possível encontrar a primeira mensagem.")

@bot.command()
@commands.check(is_owner)
async def tryselfupdate(ctx):
    github_repo_url = GITHUB_REPO_URL.rstrip('/')  # Remover barra final se houver
    zip_url = f'{github_repo_url}/archive/refs/heads/main.zip'  # URL para o arquivo ZIP

    await ctx.send(f"Atualizando o bot... Tentando baixar de: {zip_url}")

    try:
        response = requests.get(zip_url)
        if response.status_code == 200:
            with open('update.zip', 'wb') as f:
                f.write(response.content)

            # Verifica se o arquivo baixado é um arquivo ZIP válido
            if zipfile.is_zipfile('update.zip'):
                # Extraindo o arquivo baixado
                with zipfile.ZipFile('update.zip', 'r') as zip_ref:
                    zip_ref.extractall('./')

                os.remove('update.zip')

                # Reiniciando o bot
                await ctx.send("Bot atualizado com sucesso! Reiniciando...")
                os.execv(sys.executable, ['python'] + sys.argv)
            else:
                os.remove('update.zip')
                await ctx.send("Falha na atualização: O arquivo baixado não é um arquivo ZIP válido.")
        else:
            await ctx.send(f"Falha na atualização: Não foi possível baixar o arquivo (status code: {response.status_code}).")
    except Exception as e:
        await ctx.send(f"Falha na atualização: {e}")

@dmall.error
@fm.error
@tryselfupdate.error
async def permission_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Você não tem permissão para usar este comando.")

bot.run(TOKEN)
