''' --> IMPORT <--'''

import discord
from discord.ext import commands
import hashlib
import csv
import time
import os

''' --> DEF <-- '''

def getToken():
    with open('TOKEN') as f:
        token = f.read()
    return token

def hashSha256(s):
    return hashlib.sha256(s.encode('ascii')).hexdigest()

def getMiningReward(diff):
    if diff == 0:
        return 0
    reward = round((0.2602052164933*2.7182818284**(2.8935861583891*diff/2))/6511, 4)
    return reward

def getHashDifficulty(hash):
    diff = (len(hash)-len(hash.lstrip('0')))
    return diff

def mine(s):
    _hash_ = hashSha256(s)
    _diff_ = getHashDifficulty(_hash_)
    _reward_ = getMiningReward(_diff_)
    return {'str':s,'hash':_hash_,'diff':_diff_,'reward':_reward_}

def convertMiningRes(res):
    return [res['str'],res['hash'],res['diff'],res['reward']]

async def appendCsv(file,fields):
    with open(file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(fields)
    return 0

async def loadTransactions(file):
    with open(file, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
    return data

async def loadMined(file):
    with open(file, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
    return data

async def appendMined(f,l,h):
    await appendCsv(f, [h])
    l.append(h)
    return l

async def processTransactions(l):
    accounts = {}
    for e in l:
        if e[1] not in accounts:
            accounts[e[1]] = float(e[2])
        else:
            accounts[e[1]] += float(e[2])
        if e[0] != '0':
            accounts[e[0]] -= float(e[2])
    return accounts

async def loadProcessedTr(f):
    return await processTransactions(await loadTransactions(f))

async def createTransaction(f,s,r,a):
    a = float(a)
    accounts = await loadProcessedTr(f)
    if s == '0':
        await appendCsv(f,[s,r,a])
        print(f'MINED: Recipient: {r} | Amount: {a}')
        return True
    if s not in accounts:
        return False
    if accounts[s] < a or a <= 0:
        return False
    await appendCsv(f,[s,r,a])
    print(f'TRANSACTION: Sender: {s} --> Recipient: {r} | Amount: {a}')
    return True

''' --> BOT <-- '''

_token = getToken()
_word = 'bruhcoin'

f_transactions = './transactions.csv'
f_mined = './mined.csv'

client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
    print(f'Connected as {client.user}.')

@client.command()
async def wallet(ctx, *args):
    accounts = await loadProcessedTr(f_transactions)
    if args:
        usr = args[0].replace('<','').replace('>','').replace('@','').replace('!','')
        if '&' in usr:
            return False
        try:
            usr = int(usr)
        except:
            return False
        usr = str(usr)
        if usr not in accounts:
            await ctx.send(f"{ctx.author.mention} That user doesn't have any [:b:].")
            return True
        else:
            wallet_amt = accounts[usr]
            em = discord.Embed(title = f"{usr}'s wallet", color = discord.Color.red())
            em.add_field(name = "ID", value = usr)
            em.add_field(name = "Wallet", value = format(wallet_amt, '.6f')+' [:b:]')
    else:
        if str(ctx.author.id) in accounts:
            wallet_amt = accounts[str(ctx.author.id)]
            em = discord.Embed(title = f"{ctx.author.name}'s wallet", color = discord.Color.red())
            em.add_field(name = "ID", value = ctx.author.id)
            em.add_field(name = "Wallet", value = format(wallet_amt, '.6f')+' [:b:]')
        else:
            await ctx.send(f"{ctx.author.mention} You do not have any [:b:].")
            return True
    await ctx.send(embed = em)
    return True

@client.command()
async def mine(ctx, *args):
    mined = await loadMined(f_mined)
    minedBRHC = []
    for e in mined:
        minedBRHC.append(e[0])
    if (ctx.message.guild == None):
        await ctx.send("You currently can't mine in dm's!")
        return False
    if not args:
        await ctx.send(f"{ctx.author.mention} You need to provide a nonce.")
        return False
    try:
        nonce = int(args[0])
    except:
        await ctx.send(f"{ctx.author.mention} Invalid nonce!")
        return False
    h = hashSha256(_word+str(nonce))
    reward = getMiningReward(getHashDifficulty(h))
    if h in minedBRHC:
        await ctx.send(f"{ctx.author.mention} That [:b:] was already mined!")
        return False
    if reward > 0:
        await createTransaction(f_transactions,'0',str(ctx.message.author.id), reward)
        mined = await appendMined(f_mined,mined,h)
        await ctx.send(f"{ctx.author.mention} Mined {reward}[:b:].")
        return True
    else:
        await ctx.send(f"{ctx.author.mention} Invalid nonce!")
        return False

@client.command()
async def send(ctx, *args):
    _sender = str(ctx.author.id)
    if len(args) == 2:
        try:
            _amt = float(args[1])
        except:
            await ctx.send(f"{ctx.author.mention} Invalid amount.")
            return False
        _recipient = args[0].replace('<','').replace('>','').replace('@','').replace('!','')
        if '&' in _recipient:
            await ctx.send(f"{ctx.author.mention} transaction failed.")
            return False
        
        if(_sender == _recipient):
            await ctx.send(f"{ctx.author.mention} You can't send [:b:] to yourself.")
            return False
        
        tr = await createTransaction(f_transactions,str(_sender),str(_recipient), _amt)
        if tr:
            await ctx.send(f"{ctx.author.mention} Transaction successful.")
            return True
        else:
            await ctx.send(f"{ctx.author.mention} Transaction failed.")
            return False
        
    else:
        await ctx.send(f"{ctx.author.mention} Transaction failed, incorrect arguments.")
        return False
    
client.run(_token)