import random
import time
from colorama.ansi import Fore
from websocket import create_connection
import threading
import requests
import json
from colorama import Fore, init
import datetime
import os
init()
caps = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
lower = "abcdefghijklmnopqrstuvwxyz"

def printStatus(color, message):
    dt = datetime.datetime.now(datetime.timezone.utc).strftime("[%H:%M:%S]")
    if color == "green":
        print(Fore.LIGHTGREEN_EX + f"{dt} | {message}")
    elif color == "yellow":
        print(Fore.LIGHTYELLOW_EX + f"{dt} | {message}")
    elif color == "red":
        print(Fore.LIGHTRED_EX + f"{dt} | {message}")
    elif color == "cyan":
        print(Fore.LIGHTCYAN_EX + f"{dt} | {message}")
    elif color == "white":
        print(Fore.WHITE + f"{dt} | {message}")

class BombPartyBot:
    def __init__(self, name, roomCode, typeDelay) -> None:
        printStatus("yellow", "Initializing BP-Bot...")
        script_dir = os.path.dirname(__file__)
        abs_file_path = os.path.join(script_dir, "words.txt")
        file = open(abs_file_path, "r+")
        self.wordlist = file.readlines()
        self.usedWords = []
        self.typeDelay = typeDelay

        self.userCode = caps[random.randint(0,len(caps) - 1)]
        self.name = name
        self.peerID = ""

        self.roomCode = roomCode
        self.url = ""

        self.myTurn = False
        printStatus("green","BP-Bot Initialized")

    def createUserCode(self):
        for x in range(0, 15):
            choice = random.randint(0, 1)
            if choice == 0:
                self.userCode += str(random.randint(0,9))
            else:
                choice2 = random.randint(0,1)
                if choice2 == 0:
                    self.userCode += caps[random.randint(0,len(caps) - 1)]
                else:
                    self.userCode += lower[random.randint(0,len(caps) - 1)]
                    
    def findword(self, syl):
        longest = ""
        for word in self.wordlist:
            if syl in word and len(word) > len(longest) and word not in self.usedWords:
                longest = word
        self.usedWords.append(longest)
        return longest.replace('\n','')

    def sendWord(self, ws, word):
        total = ""
        for letter in word:
            total += letter
            if total == word:
                pass
                ws.send(f'42["setWord","{total}",true]')
            else:
                ws.send(f'42["setWord","{total}",false]')
            time.sleep(self.typeDelay)

    def getRoomURL(self):
        while True:
            try:
                printStatus("yellow","Getting Room Information")
                headers = {
                    'authority': 'jklm.fun',
                    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
                    'sec-ch-ua-mobile': '?0',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
                    'sec-ch-ua-platform': '"Windows"',
                    'content-type': 'application/json',
                    'accept': '*/*',
                    'origin': 'https://jklm.fun',
                    'sec-fetch-site': 'same-origin',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-dest': 'empty',
                    'accept-language': 'en-US,en;q=0.9',
                }

                data = '{"roomCode":"' + self.roomCode + '"}'

                response = requests.post('https://jklm.fun/api/joinRoom', headers=headers, data=data)
                self.url = json.loads(response.text)["url"].replace("https", "wss")
                printStatus("green", "Room Found")
                break
            except:
                printStatus("red", "Error Getting Room Information")

    def joinRoom(self):
        printStatus("yellow", "Joining Room")
        websocket = create_connection(self.url + "/socket.io/?EIO=3&transport=websocket")
        websocket.send('420["joinRoom",{"roomCode":"' + self.roomCode + '","userToken":"' + self.userCode + '","nickname":"' + self.name + '","language":"en-US"}]')
        printStatus("green", "Room Joined")
        while True:
            time.sleep(1)
            websocket.recv()
            websocket.send("2")

    def joinGame(self):
        printStatus("yellow","Connecting to Game")
        websocket = create_connection(self.url + "/socket.io/?EIO=3&transport=websocket")
        websocket.recv()
        websocket.recv()
        websocket.send('42["joinGame","bombparty","' + self.roomCode + '","' + self.userCode + '"]')
        websocket.recv()
        websocket.send('42["joinRound"]')
        printStatus("green","Game Connection Established")

        prevThree = False
        while True:
            response = websocket.recv()
            if response == "3" and prevThree == False:
                printStatus("yellow", "Waiting for Status...")
                prevThree = True
            else:
                if "addPlayer" in response and f'"{self.name}"' in response:
                    prevThree = False
                    self.peerID = response.split('{"peerId":')[1].split(',"nickname"')[0]
                    printStatus("green", f"PeerID Found: {self.peerID}")

                elif "setMilestone" in response and f'"currentPlayerPeerId":{self.peerID},' in response:
                    prevThree = False
                    syl = response.split('"syllable":"')[1].split('","')[0]
                    myTurn = True
                    printStatus("green","Syllable Found: " + syl)
                    while myTurn:
                        word = self.findword(syl)
                        printStatus("yellow","Sending Word: " + word)
                        self.sendWord(websocket, word)

                        while True:
                            status = websocket.recv()

                            if "failWord" in status and f",{self.peerID}," in status:
                                printStatus("red", f"Word Failed")
                                break
                            elif "correctWord" in status and f'"playerPeerId":{self.peerID},"' in status:
                                printStatus("green", f"Word Successful")
                                myTurn = False
                                break
                            
                
                elif "nextTurn" in response and f",{self.peerID}," in response:
                    prevThree = False
                    syl = response.split(f'{self.peerID},"')[1].split('"')[0]
                    myTurn = True
                    printStatus("green","Syllable Found: " + syl)
                    while myTurn:
                        word = self.findword(syl)
                        printStatus("yellow","Sending Word: " + word)
                        self.sendWord(websocket, word)

                        while True:
                            status = websocket.recv()

                            if "failWord" in status and f",{self.peerID}," in status:
                                printStatus("red", f"Word Failed")
                                break
                            elif "correctWord" in status and f'"playerPeerId":{self.peerID},"' in status:
                                printStatus("green", f"Word Successful")
                                myTurn = False
                                break

                
            websocket.send("2")
            

    def startClient(self):
        self.getRoomURL()
        self.createUserCode()
        threading.Thread(target=self.joinRoom).start()
        time.sleep(1)
        threading.Thread(target=self.joinGame).start()