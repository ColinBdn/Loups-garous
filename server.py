from flask import Flask, send_from_directory
import socketio
import logging
import random
import time
from collections import Counter

class Colors:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    ORANGE = '\033[38;5;208m'
    PINK = '\033[38;5;200m'
    VIOLET = '\033[38;5;129m'
    LIGHT_GREEN = '\033[38;5;120m'
    LIGHT_BLUE = '\033[38;5;123m'
    LIGHT_CYAN = '\033[38;5;152m'
    LIGHT_MAGENTA = '\033[38;5;207m'
    GOLD = '\033[38;5;220m'
    SILVER = '\033[38;5;7m'
    TEAL = '\033[38;5;86m'
    GREY = '\033[38;5;242m'
    
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    BG_BRIGHT_BLACK = '\033[100m'
    BG_BRIGHT_RED = '\033[101m'
    BG_BRIGHT_GREEN = '\033[102m'
    BG_BRIGHT_YELLOW = '\033[103m'
    BG_BRIGHT_BLUE = '\033[104m'
    BG_BRIGHT_MAGENTA = '\033[105m'
    BG_BRIGHT_CYAN = '\033[106m'
    BG_BRIGHT_WHITE = '\033[107m'
    
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    REVERSED = '\033[7m'
    RESET = '\033[0m'

def print(*args, color=None, **kwargs):
    if color:
        __builtins__.print(color, end="")
    __builtins__.print(*args, **kwargs)
    if color:
        __builtins__.print(Colors.RESET, end="")



#------------------------------------------------------------------------
#------------------------------------------------------------------------
#---------------------------- SERVER SETUP ------------------------------
#------------------------------------------------------------------------
#------------------------------------------------------------------------


log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

sio = socketio.Server()

app = Flask(__name__)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)




@app.route('/')
def index():
    return send_from_directory('.', 'test2.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)


#------------------------------------------------------------------------
#------------------------------------------------------------------------
#----------------------------- PLAYER CLASS------------------------------
#------------------------------------------------------------------------
#------------------------------------------------------------------------

class Player:
    def __init__(self, sid, username):
        self.sid=sid
        self.username=username
        self.choice=None
        self.reset()
    
    def __str__(self):
        return f"Player{{sid: {self.sid}, username: {self.username}, role: {self.role+',':<11} alive: {str(self.alive)+',':<6} choice: {self.choice}}}"
    
    def __repr__(self):
        return self.__str__()
    
    def reset(self):
        self.role=None
        self.alive=True


#------------------------------------------------------------------------
#------------------------------------------------------------------------
#------------------------------ GAME CLASS ------------------------------
#------------------------------------------------------------------------
#------------------------------------------------------------------------


class Game:
    roles = {
    "loup": 2,
    "voyante": 1,
    "sorciere": 1,
    "villageois": -1,
    "cupidon": 1
    }

    def __init__(self):
        self.reset()
    
    
    def reset(self):
        sio.emit("reset", None)
        self.started = False
        self.nbPlayer = 0
        self.players: list[Player] = []
        self.lovers: list[Player] = [None, None]
        self.currentKilled = None
        self.sorciereKill = None
        self.chatEnabled = False
    

    def randomize(self) -> None:
        available_roles = []

        nbNonVillageois = 0
        for role, count in self.roles.items():
            if role!="villageois":
                nbNonVillageois+=count

        self.roles["villageois"] = len(self.players)-nbNonVillageois

        for role, count in self.roles.items():
            available_roles.extend([role] * count)

        random.shuffle(available_roles)
        for i, player in enumerate(self.players):
            player.role = available_roles[i]


    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------


    def addPlayer(self, sid, data):
        self.players.append(Player(sid, data))
        print(f"new player added, username: {data}, sid: {sid}", color=Colors.GREY)

        game.nbPlayer+=1
        sio.emit("updatePlayerNumber", game.nbPlayer)

        if self.nbPlayer==6:
            sio.emit("start", {"nbPlayers": self.nbPlayer, "usernames":self.getUsernames()})
            self.start()


    def removePlayer(self, sid) -> None:
        for player in self.players:
            if (player.sid == sid):
                print(f"player {player.username} removed", color=Colors.GREY)
                self.players.remove(player)


    def handleDisconnect(self, sid):
        if self.started:
            print("\n\n\n///////////////////////////////////////////////////////////", color=Colors.RED)
            print(      "////////////     disconnected, reseting...     ////////////", color=Colors.RED)
            print(      "///////////////////////////////////////////////////////////\n\n", color=Colors.RED)
            self.reset()
        elif self.exist(sid):
            self.removePlayer(sid)
            self.nbPlayer-=1
            sio.emit("playerRemoved", self.nbPlayer)

    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------


    def exist(self, sid) -> bool:
        for player in self.players:
            if (player.sid == sid):
                return True
        return False
    
    def showPlayers(self) -> None:
        for player in self.players:
            print(player, color=Colors.GREY)

        
    def getUsernames(self) -> list[str]:
        usernames = []
        for player in self.players:
            usernames.append(player.username)
        return usernames
    

    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------


    def findPlayerByName(self, username, removeAlive=False) -> Player:
        for player in self.players:
            if (player.username == username):
                if (removeAlive==True and player.alive==True):
                    return player
                elif (removeAlive==False):
                    return player

    def findPlayerBySid(self, sid, removeAlive=False) -> Player:
        for player in self.players:
            if (player.sid == sid):
                if (removeAlive==True and player.alive==True):
                    return player
                elif (removeAlive==False):
                    return player
            
    def findPlayersByRole(self, role, removeAlive=False) -> list[Player]:
        res = []
        for player in self.players:
            if (player.role == role):
                if (removeAlive==True and player.alive==True):
                    res.append(player)
                elif (removeAlive==False):
                    res.append(player)

        return res

    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------



    def sendMessage(self, data: str):
        sio.emit("gameMessage", data)
        
    def sendRole(self, role: str, removeAlive=False, data: str = None):
        playerList = self.findPlayersByRole(role, removeAlive)
        for player in playerList:
            sio.emit("role", {"role":role, "data":data}, room=player.sid)

    def sendToRole(self, role: str, data: str, removeAlive=False):
        playerList = self.findPlayersByRole(role, removeAlive)
        for player in playerList:
            sio.emit("privateMessage", data, room=player.sid)

    def sendToPlayer(self, player: Player, data: str):
        sio.emit("privateMessage", data, room=player.sid)

    def sendToUsername(self, username: str, data: str):
        player = self.findPlayerByName(username)
        sio.emit("privateMessage", data, room=player.sid)


    def toggleChat(self, enable):
        self.chatEnabled = enable
        sio.emit('toggleChat', enable)

    def sendChatMessage(self, sid, data):
        if self.chatEnabled:
            sio.emit('chatMessage', {"username":   self.findPlayerBySid(sid).username, "message":data})

    def sendPlayersRole(self):
        for player in self.players:
            sio.emit("ownRole", data=player.role, room=player.sid)

    def sendDead(self):
        for player in self.players:
            if player.alive==False:
                sio.emit("isDead", data={"username":player.username, "role":player.role})
    
    def showSomeoneRole(self, receiver: Player, playerToShow:Player):
        sio.emit("showSomeoneRole", data={"username":playerToShow.username, "role":playerToShow.role}, room=receiver.sid)

    def hideSomeoneRole(self, receiver: Player, playerToHide:Player):
        sio.emit("hideSomeoneRole", data={"username":playerToHide.username}, room=receiver.sid)

    def showEveryoneRole(self):
        for player in self.players:
            sio.emit("showSomeoneRole", data={"username":player.username, "role":player.role})

    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------



    def processRoundResult(self, sid, data):
        if (data["round"]=="cupidon"):
            self.processCupidon(sid, data["data"])
        elif (data["round"]=="voyante"):
            self.processVoyante(sid, data["data"])
        elif (data["round"]=="loups"):
            self.processLoups(sid, data["data"])
        elif (data["round"]=="sorciere"):
            self.processSorciere(sid, data["data"])
        elif (data["round"]=="vote"):
            self.processVote(sid, data["data"])
        

    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------
    #------------------------------------------------------------------------


    def start(self):
        print("\n\n--------------------------------------", color=Colors.GREEN)
        print("------------ GAME STARTED ------------", color=Colors.GREEN)
        print("--------------------------------------\n", color=Colors.GREEN)

        self.randomize()
        self.sendPlayersRole()

        self.showPlayers()
        
        self.started = True
        # time.sleep(2)
        # self.toggleChat(True)
        self.runBeginning(first=True)
        # self.runCupidon()
        # self.runVoyante()
        # self.runLoups()
        # self.runSorciere()
        

    #------------------------------------------------------------------------
    #------------------------------------------------------------------------


    def runBeginning(self, first=False):
        self.toggleChat(False)
        self.sendMessage("le village s'endort")
        time.sleep(1)
        self.sendMessage("le village s'endort.")
        time.sleep(1)
        self.sendMessage("le village s'endort..")
        time.sleep(1)
        self.sendMessage("le village s'endort...")
        time.sleep(1)

        if first:
            self.runCupidon()
        else:
            self.runVoyante()



    #------------------------------------------------------------------------
    #------------------------------------------------------------------------


    def runCupidon(self):
        print("\n------------ CUPIDON ------------", color=Colors.BLUE)
        self.sendRole("cupidon")
        self.sendToRole(role="cupidon", data="Cupidon, cliques sur les 2 personnes qui vont tomber amoureux")

        self.sendMessage("Cupidon se reveille")
        time.sleep(1.5)
        self.sendMessage("Cupidon réfléchit...")

    def processCupidon(self, sid, data):
        self.lovers = [self.findPlayerByName(data["lover1"]), self.findPlayerByName(data["lover2"])]
        print("--- cupidon has chosen", color=Colors.GREY)
        print("--- lovers:", color=Colors.GREY)
        print(self.lovers[0], color=Colors.GREY)
        print(self.lovers[1], color=Colors.GREY)

        self.sendMessage("Cupidon a choisit !")
        self.sendToPlayer(self.lovers[0], f"tu est en couple avec {self.lovers[1].username}")
        self.sendToPlayer(self.lovers[1], f"tu est en couple avec {self.lovers[0].username}")

        self.sendMessage("regardez bien si vous êtes en couple ou pas !")
        time.sleep(3)

        self.runVoyante()


    #------------------------------------------------------------------------
    #------------------------------------------------------------------------


    def runVoyante(self):
        if (self.findPlayersByRole("voyante", removeAlive=False)[0].alive==False):
            print("\n--- VOYANTE IS DEAD, SKIPPING ---", color=Colors.BLUE)
            self.runLoups()
            return

        print("\n------------ VOYANTE ------------", color=Colors.BLUE)
        self.sendRole("voyante")
        self.sendToRole(role="voyante", data="voyante, cliques sur le personne dont tu veux connaître le rôle")

        self.sendMessage("La voyante se réveille")
        time.sleep(1.5)
        self.sendMessage("La voyante réfléchit...")

    def processVoyante(self, sid, data):
        chosenPlayer = self.findPlayerByName(data["username"])
        print("--- voyante has chosen", color=Colors.GREY)
        print("--- player chosen:", color=Colors.GREY)
        print(chosenPlayer, color=Colors.GREY)

        self.sendMessage("La voyante vient de découvrir le rôle de l'un d'entre vous !")
        self.sendToRole("voyante", f"le role de {chosenPlayer.username} est: {chosenPlayer.role}")

        self.runLoups()



    #------------------------------------------------------------------------
    #------------------------------------------------------------------------


    def runLoups(self):
        print("\n------------ LOUPS ------------", color=Colors.BLUE)
        self.sendRole("loup", removeAlive=True)
        self.sendToRole(role="loup", data="loups, cliquez sur la personnes que vous voulez tuer")

        loupsList = self.findPlayersByRole("loup", removeAlive=True)
        for player in loupsList:
            for toShow in loupsList:
                self.showSomeoneRole(player, toShow)

        self.sendMessage("Les loups se réveillent")
        time.sleep(1.5)
        self.sendMessage("Les loups réfléchissent...")
        

    def processLoups(self, sid, data):
        targetPlayer = self.findPlayerByName(data["targetUsername"])
        loupPlayer = self.findPlayerBySid(sid)
        loupPlayer.choice = targetPlayer.username
        print(f"--- loup {loupPlayer.username} has chosen {targetPlayer.username}", color=Colors.GREY)

        loupsList = self.findPlayersByRole("loup", removeAlive=True)
        nbToHaveChose = 0
        for player in loupsList:
            if (player.choice != None):
                nbToHaveChose+=1

        if nbToHaveChose==len(loupsList):
            self.processLoupsLogic()
            self.sendMessage("Les loups viennent de tuer quelqu'un !!")
            self.runSorciere()


    def processLoupsLogic(self):
        loupsList = self.findPlayersByRole("loup", removeAlive=True)

        for player in loupsList:
            for toShow in loupsList:
                self.hideSomeoneRole(player, toShow)

        choice_counts = {}
        for player in loupsList:
            if player.choice in choice_counts:
                choice_counts[player.choice] += 1
            else:
                choice_counts[player.choice] = 1
            sio.emit("loupRemoveChoice", {"username":player.username, "target":player.choice})
            player.choice = None
        

        for player in loupsList:
            sio.emit("loupRemoveListener", "", room=player.sid)
        

        max_count = 0
        for count in choice_counts.values():
            if count > max_count:
                max_count = count
        
        most_chosen = []
        for user, count in choice_counts.items():
            if count == max_count:
                most_chosen.append(user)

        chosenUsername = random.choice(most_chosen)
        chosenPlayer = self.findPlayerByName(chosenUsername)
        self.currentKilled = chosenPlayer
        print(f"--- {chosenPlayer.username} has been killed", color=Colors.GREY)



    def loupGraphicalInfo(self, sid, data):
        targetPlayer = self.findPlayerByName(data["targetUsername"])
        loupPlayer = self.findPlayerBySid(sid)

        resData = {"username":loupPlayer.username, "target":targetPlayer.username}

        playerList = self.findPlayersByRole("loup", removeAlive=True)
        if (data["action"]=="add"):
            for player in playerList:
                sio.emit("loupAddChoice", resData, room=player.sid)
        elif (data["action"]=="remove"):
            for player in playerList:
                sio.emit("loupRemoveChoice", resData, room=player.sid)



    #------------------------------------------------------------------------
    #------------------------------------------------------------------------


    def runSorciere(self):
        if (self.findPlayersByRole("sorciere")[0].alive==False):
            self.currentKilled.alive = False
            print("\n--- SORCIERE IS DEAD, SKIPPING ---", color=Colors.BLUE)
            self.runRoundEnd()
            return
        self.currentKilled.alive = False


        print("\n------------ SORCIERE ------------", color=Colors.BLUE)
        self.sendRole("sorciere")
        phrase = ""
        if self.currentKilled is not None:
            phrase = f"sorcière, cette personne à été tué:\n- {self.currentKilled.username} -\nQue veut tu faire ?"
        else:
            phrase = f"sorcière, cette personne à été tué:\n- ERROR -\nQue veut tu faire ?"
            print("--- error: currentKiller is none", color=Colors.RED)
        self.sendToRole(role="sorciere", data=phrase)

        self.sendMessage("La sorcière se réveille")
        time.sleep(1.5)
        self.sendMessage("La sorcière réfléchit...")


    def processSorciere(self, sid, data):
        if (data["action"] == "doNothing"):
            print("--- sorciere choose to do nothing", color=Colors.GREY)
        elif (data["action"] == "resurrect"):
            print("--- sorciere choose to resurrect", color=Colors.GREY)
            if (self.currentKilled is not None):
                print(f"--- resurrected: {self.currentKilled}", color=Colors.GREY)
                self.currentKilled.alive = True
                self.currentKilled = None
            else:
                print(f"--- currentKilled is none, no one resurrected", color=Colors.GREY)
        elif (data["action"] == "killSomeoneElse"):
            self.sorciereKill = self.findPlayerByName(data["username"])
            self.sorciereKill.alive = False
            print("--- sorciere choose to kill someone else", color=Colors.GREY)
            print(f"--- killed: {self.sorciereKill}", color=Colors.GREY)

        self.runRoundEnd()



    #------------------------------------------------------------------------
    #------------------------------------------------------------------------


    def runRoundEnd(self):
        print("------------ ROUND ENDED ------------", color=Colors.GREEN)


        phrase=""
        if (self.currentKilled is not None):
            phrase += f"\"{self.currentKilled.username}\" est mort cette nuit sont rôle était: \"{self.currentKilled.role}\"\n"
        elif (self.currentKilled is None):
            phrase += f"Personne n'est mort cette nuit !\n"

        if (self.sorciereKill is not None):
            if phrase!="":
                phrase+="\n"
            phrase += f"Ce n'est pas tout, \"{self.sorciereKill.username}\" est aussi morte cette nuit,"+\
                             f" sont rôle était: \"{self.sorciereKill.role}\"\n"

        if (self.currentKilled in self.lovers and self.sorciereKill in self.lovers):
            if phrase!="":
                phrase+="\n"
            phrase += f"De plus \"{self.currentKilled.username}\" était mariée avec \"{self.sorciereKill.username}\"\n"
        elif (self.currentKilled in self.lovers):
            if phrase!="":
                phrase+="\n"
            other = not self.lovers.index(self.currentKilled)
            other: Player = self.lovers[other]
            other.alive = False
            phrase += f"Ce n'est pas tout, \"{self.currentKilled.username}\" était mariée avec "+\
                            f"\"{other.username}\", \"{other.username}\" est donc mort,"+\
                            f"sont rôle était: \"{other.role}\""
        elif (self.sorciereKill in self.lovers):
            if phrase!="":
                phrase+="\n"
            other = not self.lovers.index(self.sorciereKill)
            other: Player = self.lovers[other]
            other.alive = False
            phrase += f"Ce n'est toujours pas tout, \"{self.sorciereKill}\" était mariée avec "+\
                            f"\"{other.username}\", \"{other.username}\" est donc mort, "+\
                            f"sont rôle était: \"{other.role}\""

        self.currentKilled = None
        self.sorciereKill = None

        self.toggleChat(True)
        self.showPlayers()
        self.sendMessage("Le village se réveille")
        time.sleep(2)
        self.sendMessage(phrase)
        self.sendDead()


        time.sleep(4)
        if self.checkWin()==True:
            self.showEveryoneRole()
            print("--- game finished...")
        else:
            time.sleep(2)
            print("--- game continue...")
            self.runVote()





    def checkWin(self):
        loups = []
        villageois = []

        finish=False

        loupsDead=True
        for player in self.players:
            if player.role == "loup" and player.alive:
                loupsDead=False

        villageoisDead=True
        for player in self.players:
            if player.role != "loup" and player.alive:
                villageoisDead=False

        if (loupsDead==True and villageoisDead==False):
            self.sendMessage("Tous les loups sont mort, les villageois on gagné !!!")
            finish=True
        elif (loupsDead==False and villageoisDead==True):
            self.sendMessage("Tous les villageois sont mort, les loups on gagné !!!")
            finish=True

        vivants = []
        for player in self.players:
            if player.alive == True:
                vivants.append(player)
        
        if len(vivants)==2 and self.lovers[0] in vivants and self.lovers[1] in vivants:
            self.sendMessage(f"Tout le monde sauf le couple sont mort,"+\
                             f" \"{self.lovers[0].username}\" et \"{self.lovers[1].username}\" ont donc gagné !!!")
            finish=True
        
        return finish


    #------------------------------------------------------------------------
    #------------------------------------------------------------------------


    def runVote(self):
        print("------------ VOTE ------------", color=Colors.GREEN)
        
        for player in self.players:
            if player.alive:
                sio.emit("role", {"role":"vote", "data":None}, room=player.sid)
        
        self.sendMessage("Nous allons maintenant procédér au vote !")
        time.sleep(3)
        self.sendMessage("Cliquez sur la personne que vous voulez voter."+\
                        "\nVous pouvez débattre dans le chat pour décider qui voter")

    def processVote(self, sid, data):
        targetPlayer = self.findPlayerByName(data["targetUsername"])
        voterPlayer = self.findPlayerBySid(sid)
        voterPlayer.choice = targetPlayer.username
        print(f"--- {voterPlayer.username} has chosen {targetPlayer.username}", color=Colors.GREY)

        nbToHaveChose = 0
        nbAlive = 0
        for player in self.players:
            if player.alive:
                nbAlive+=1
                if (player.choice != None):
                    nbToHaveChose+=1

        if nbToHaveChose==nbAlive:
            self.processVoteLogic()



    def processVoteLogic(self):
        choice_counts = {}
        for player in self.players:
            if player.alive:
                if player.choice in choice_counts:
                    choice_counts[player.choice] += 1
                else:
                    choice_counts[player.choice] = 1
                sio.emit("voteRemoveChoice", {"username":player.username, "target":player.choice})
                player.choice = None
        

        for player in self.players:
            sio.emit("voteRemoveListener", "", room=player.sid)
        

        max_count = 0
        for count in choice_counts.values():
            if count > max_count:
                max_count = count
        
        most_chosen = []
        for username, count in choice_counts.items():
            if count == max_count:
                most_chosen.append(username)

        chosenUsername = random.choice(most_chosen)
        chosenPlayer = self.findPlayerByName(chosenUsername)
        chosenPlayer.alive = False

        print(f"--- {chosenPlayer.username} has been killed", color=Colors.GREY)
        self.sendMessage(f"Le village à fait son vote !"+\
            f"\n{chosenPlayer.username} à été éliminer et son rôle était: {chosenPlayer.role}")


        if (chosenPlayer in self.lovers):
            other = not self.lovers.index(chosenPlayer)
            other: Player = self.lovers[other]
            other.alive = False
            time.sleep(4)
            self.sendMessage(f"Malheureusement (ou heureusement), \"{chosenPlayer.username}\" était mariée avec "+\
                            f"\"{other.username}\", \"{other.username}\" est donc mort,"+\
                            f"sont rôle était: \"{other.role}\"")

        self.sendDead()

        time.sleep(4)
        if self.checkWin()==True:
            self.showEveryoneRole()
            print("--- game finished...")
        else:
            time.sleep(2)
            print("--- game continue...")
            self.toggleChat(False)
            self.runBeginning()




    def voteGraphicalInfo(self, sid, data):
        targetPlayer = self.findPlayerByName(data["targetUsername"])
        voterPlayer = self.findPlayerBySid(sid)

        resData = {"username":voterPlayer.username, "target":targetPlayer.username}

        if (data["action"]=="add"):
            for player in self.players:
                sio.emit("voteAddChoice", resData, room=player.sid)
        elif (data["action"]=="remove"):
            for player in self.players:
                sio.emit("voteRemoveChoice", resData, room=player.sid)

        




#------------------------------------------------------------------------
#------------------------------------------------------------------------
#------------------------------------------------------------------------
#------------------------------------------------------------------------


game = Game()


#------------------------------------------------------------------------
#------------------------------------------------------------------------
#---------------------------- SOCKET EVENTS -----------------------------
#------------------------------------------------------------------------
#------------------------------------------------------------------------



@sio.event
def test(sid, data): 
    print("test response")


@sio.event
def debug(sid, data):
    print("\n========= DEBUG =========", color=Colors.ORANGE)
    print("nb players:", len(game.players))
    game.showPlayers()
    print("=========================\n", color=Colors.ORANGE)



@sio.event
def roundResult(sid, data): 
    game.processRoundResult(sid, data)


@sio.event
def addPlayer(sid, data): 
    game.addPlayer(sid, data)


@sio.event
def loupGraphicalInfo(sid, data): 
    game.loupGraphicalInfo(sid, data)

@sio.event
def voteGraphicalInfo(sid, data): 
    game.voteGraphicalInfo(sid, data)

@sio.event
def disconnect(sid):
    game.handleDisconnect(sid)

        

@sio.event
def connect(sid, environ):
    sio.emit("updatePlayerNumber", game.nbPlayer)


@sio.event
def chatMessage(sid, data):
    game.sendChatMessage(sid, data)




if __name__ ==  '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)