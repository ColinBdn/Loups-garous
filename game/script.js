function hideForm()
{
    var form = document.getElementById("connectForm");
    form.getElementsByTagName("div")[0].style.display= "none";
}
function hideAll()
{
    document.getElementById("connectForm").style.display= "none";
}
function showAll()
{
    document.getElementById("connectForm").style.display= "";
    var form = document.getElementById("connectForm");
    form.getElementsByTagName("div")[0].style.display= "";
}




function connect()
{
    playerName = document.getElementById("playerName").value;
    hideForm();
    socket.emit("addPlayer", playerName);
}

function waitForPlayer()
{
    socket.on('updatePlayerNumber', function(data) {
        document.getElementById("nbPlayer").textContent = data;
        if (data >= 3)
        {
            hideAll();
            socket.off('updatePlayerNumber');
            start();
        }
    });
    socket.on('playerRemoved', function(data) {
        document.getElementById("nbPlayer").textContent = data;
    });
}

function handleReset()
{
    socket.on('reset', function() {
        reset();
    });

    socket.io.on("error", function() {
        // alert("connection error");
        reset();
    });
}

function reset()
{
    showAll();
    waitForPlayer();
}


function start()
{
    socket.on('gameMessage', function(data) {
        document.getElementById("gameMessages").textContent = data;
    });
}


function draw()
{
    // canvas = document.getElementById("gameCanva");
    // ctx = canvas.getContext("2d");

    // resize = () => {
    //     canvas.width = window.innerWidth;
    //     canvas.height = window.innerHeight;
    // }
    // resize()
    // window.addEventListener('resize', resize)

    // ctx.fillStyle = "rgb(200 0 0)";
    // ctx.fillRect(10, 10, 50, 50);
}

function drawPlayers()
{
    let players = document.getElementsByClassName("player");
    // let nbPlayers = players.length;
    // console.log(players);

    for (let i = 0; i < players.length; i++)
    {
        console.log("a")
        players[i].style.top = Math.round(Math.sin(i/players.length * 2*Math.PI) * 50 + 50).toString()+"vh"
        players[i].style.left = Math.round(Math.cos(i/players.length * 2*Math.PI) * 50 + 50).toString()+"vh"
    }    
}






socket = io();
waitForPlayer();
handleReset();

drawPlayers()