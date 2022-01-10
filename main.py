from bombPartyBot import BombPartyBot
from colorama import init, Fore


init()

title = '''
   ___  ___      ___  ____  ______
  / _ )/ _ \____/ _ )/ __ \/_  __/
 / _  / ___/___/ _  / /_/ / / /   
/____/_/      /____/\____/ /_/
'''


print(Fore.LIGHTCYAN_EX + title)
print("===================================================")


print(Fore.WHITE)
roomCode = input("Enter Room Code: ")
name = input("Enter Name: ")


c = BombPartyBot(name, roomCode, 0.03)
c.startClient()
