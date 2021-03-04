import hashlib
import time
from datetime import datetime

v = '2.0'

print('------------------')
print(f'BruhCoin Miner {v}')
print('------------------')
diff = int(input("* Enter mining difficulty: "))
point = int(input("* Enter starting point: "))
print('------------------')
print('Started mining...')
print('------------------')

def hash(s):
    return hashlib.sha256(s.encode('ascii')).hexdigest()

def mine(s,diff=1):
    nonce = point
    while True:
        start_t = datetime.now()
        start = start_t.strftime("%H:%M:%S")
        prefix = '0' * diff
        while not hash(s+str(nonce)).startswith(prefix):
            nonce+=1
        end_t = datetime.now()
        end = end_t.strftime("%H:%M:%S")
        elapsed = (end_t - start_t)
        print(f"{nonce} | Diff: {diff} | Hash: {hash(s+str(nonce))} | Start: {start} | End: {end} | Elapsed: {elapsed}")
        nonce+=1
        
mine('bruhcoin',diff)
