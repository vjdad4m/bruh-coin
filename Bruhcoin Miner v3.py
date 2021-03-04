import hashlib
import time
from datetime import datetime
import pyfiglet

v = '3.0'

print()
result = pyfiglet.figlet_format("BruhCoin", font = "larry3d")
print(result,v)

print('-----------------------------------------------------------------')
diff = int(input("* Enter mining difficulty: "))
point = int(input("* Enter starting point: "))
should_save = input("* Save results? (y/n): ")

if should_save == 'y' or should_save == 'yes':
    should_save = True
else:
    should_save = False

result = pyfiglet.figlet_format("Mining...", font = "slant") 
print(result)

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
        y = f"{nonce} | Diff: {diff} | Hash: {hash(s+str(nonce))} | Start: {start} | End: {end} | Elapsed: {elapsed}\n"
        if should_save:
            with open("results.txt", "a") as myfile:
                myfile.write(y)
        print(y)
        nonce+=1
        
mine('bruhcoin',diff)
