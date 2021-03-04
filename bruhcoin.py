import discord
from discord.ext import commands
import json
import os
import random
import hashlib
import time

with open('TOKEN') as f:    # Get Discord Token
    token = f.read()

_word = 'bruhcoin'
hashlist = []

def hash(s):
    return hashlib.sha256(s.encode('ascii')).hexdigest()

def reward(diff):
    if diff == 1:
        return 0.01
    if diff == 2:
        return 0.015
    if diff == 3:
        return 0.02
    if diff == 4:
        return 0.03
    else:
        return round((((2**diff)*reward(diff-1))/10),2)

"""
def mine(s,diff=1):
    t = time.time()
    prefix = '0' * diff
    i = 0
    while not hash(s+str(i)).startswith(prefix):
        i+=1
    print(f"Hash {hash(s+str(i))} found with difficulty {diff} and nonce {i}. Time took: {time.time()-t}")
"""

client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.command()
async def wallet(ctx, *args):
    if args:
        to_check = args[0].replace('<','').replace('>','').replace('@','').replace('!','')
        if '&' in to_check:
            return False
        try:
            to_check = int(to_check)
        except:
            return False
        
        await(open_account_byid(to_check))
        users = await get_account_data()

        wallet_amt = users[str(to_check)]["wallet"]
        em = discord.Embed(title = f"{to_check}'s wallet", color = discord.Color.red())
        em.add_field(name = "ID", value = to_check)
        em.add_field(name = "Wallet", value = format(wallet_amt, '.4f')+' [:b:]')
    
    else:
        await open_account(ctx.author)
        users = await get_account_data()
        
        wallet_amt = users[str(ctx.author.id)]["wallet"]

        await ctx.send(ctx.author.mention)

        em = discord.Embed(title = f"{ctx.author.name}'s wallet", color = discord.Color.red())
        em.add_field(name = "ID", value = ctx.author.id)
        em.add_field(name = "Wallet", value = format(wallet_amt, '.4f')+' [:b:]')
    
    await ctx.send(embed = em)

@client.command()
async def mine(ctx, arg):
    if not arg:
        await ctx.send(f"{ctx.author.mention} You need to provide a nonce!")
        return False
    
    if (ctx.message.guild == None):
        await ctx.send("You currently can't mine in dm's!")
        return False

    h = hash(_word+str(arg))
    if h[0] != '0':
        await ctx.send(f"{ctx.author.mention} Invalid hash, nonce isn't valid.")
        return False

    if h in hashlist:
        await ctx.send(f"{ctx.author.mention} That [:b:] was already mined.")
        return False
    
    hashlist.append(h)
        
    diff = (len(h)-len(h.lstrip('0')))
    
    await open_account(ctx.author)
    
    users = await get_account_data()
    
    earnings = reward(diff)
    
    await ctx.send(f"{ctx.author.mention} mined {earnings}[:b:] from hash {h} with difficulty of {diff}.")

    users[str(ctx.author.id)]["wallet"] += earnings
    
    with open("bruhcoin.json","w") as f:
        json.dump(users, f)

@client.command()
async def send(ctx, *args):
    sender_id = ctx.author.id
    recipient_id = 0
    if len(args) > 0:
        recipient_id = args[0].replace('<','').replace('>','').replace('@','').replace('!','')
        if '&' in recipient_id:
            await ctx.send(f"{ctx.author.mention} transaction failed.")
            return False
        else:
            try:
                recipient_id = int(recipient_id)
            except:
                await ctx.send(f"{ctx.author.mention} transaction failed.")
                return False
        amount = 0
        if len(args) > 1:
            try:
                amount = float(args[1])
            except:
                amount = 0
            tr = await transaction(sender_id, recipient_id, amount)
            if tr:
                await ctx.send(f"{ctx.author.mention} sent {amount} [:b:] to {recipient_id}.")

                print(f"{ctx.author.mention} sent {amount} [:b:] to {recipient_id}.")            
    
                return True
            await ctx.send(f"{ctx.author.mention} transaction failed.")
            return False
        else:
            await ctx.send(f"{ctx.author.mention} you need to provide an amount.")
            return False
    else:
        await ctx.send(f"{ctx.author.mention} you need to provide a recipient.")
        return False

async def open_account(usr):
    with open("bruhcoin.json", "r") as f:
        users = json.load(f)

    if str(usr.id) in users:
        return False
    else:
        users[str(usr.id)] = {}
        users[str(usr.id)]["wallet"] = 0.0

    with open("bruhcoin.json", "w") as f:
        json.dump(users, f)

    return True

async def open_account_byid(id):
    with open("bruhcoin.json", "r") as f:
        users = json.load(f)

    if str(id) in users:
        return False
    else:
        users[str(id)] = {}
        users[str(id)]["wallet"] = 0.0

    with open("bruhcoin.json", "w") as f:
        json.dump(users, f)

    return True

async def get_account_data():
    with open("bruhcoin.json", "r") as f:
        users = json.load(f)
    return users


async def transaction(sender, recipient, amount):
    if amount != float(amount):
        return False
    if sender == recipient or amount <= 0:
        return False
    await open_account_byid(sender)
    await open_account_byid(recipient)
    users = await get_account_data()
    if users[str(sender)]["wallet"] < float(amount):
        return False
    users[str(sender)]["wallet"] -= float(amount)
    users[str(recipient)]["wallet"] += float(amount)

    with open("bruhcoin.json","w") as f:
        json.dump(users, f)
        
    return True

client.run(token)
