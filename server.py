from flask import Flask, send_from_directory
import socketio
import logging
import random


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




class Player:
    def __init__(self, sid, username):
        self.sid=sid
        self.username=username   
        self.reset()
    
    def __str__(self):
        return f"Player{{sid: {self.sid}, username: {self.username}, role: {self.role}, alive: {self.alive}}}"
    
    def __repr__(self):
        return self.__str__()
    
    def reset(self):
        self.role=None
        self.alive=True



class Game:
    roles = {
    "Loup-Garou": 1,
    "Voyante": 0,
    "Chasseur": 0,
    "Sorcière": 1,
    "Villageois": 2,
    "Cupidon": 1
    }

    def __init__(self):
        self.reset()
    
    
    def reset(self):
        self.started = False
        self.nbPlayer = 0
        self.players: list[Player] = []
    
    def removePlayer(self, sid):
        for player in self.players:
            if (player.sid == sid):
                print(f"player {player.username} removed")
                self.players.remove(player)
    
    def exist(self, sid):
        for player in self.players:
            if (player.sid == sid):
                return True
        return False
    
    def showPlayers(self):
        for player in self.players:
            print(player)


    def randomize(self):
        available_roles = []
        for role, count in self.roles.items():
            available_roles.extend([role] * count)

        random.shuffle(available_roles)
        for i, player in enumerate(self.players):
            player.role = available_roles[i]
        
        
        
    def start(self):
        self.randomize()
        self.showPlayers()
        self.started = True
        
        self.ended = False
        
        self.runPrepRound()
        while not self.ended:
            self.runRound()
        
    def runPrepRound(self):
        pass
    
    def runRound(self):
        pass
        


game = Game()




@sio.event
def addPlayer(sid, data): 
    game.nbPlayer+=1
    sio.emit("updatePlayerNumber", game.nbPlayer)
    
    game.players.append(Player(sid, data))
    print(f"new player added, username: {data}, sid: {sid}")

    if game.nbPlayer>=3:
        game.start()


@sio.event
def disconnect(sid):
    if game.started:
        print("disconnected, reseting...\n")
        game.reset()
        sio.emit("reset", None)
    elif game.exist(sid):
        game.removePlayer(sid)
        game.nbPlayer-=1
        sio.emit("playerRemoved", game.nbPlayer)
        
@sio.event
def connect(sid, environ):
    sio.emit("updatePlayerNumber", game.nbPlayer)



if __name__ ==  '__main__':
    app.run()
    print("test")