function hideUsernameInput()
{
    var form = document.getElementById("connectForm");
    form.getElementsByTagName("div")[0].style.display= "none";
}
function hideConnectForm()
{
    document.getElementById("connectForm").style.display= "none";
}
function showForm()
{
    document.getElementById("connectForm").style.display= "";
    var form = document.getElementById("connectForm");
    form.getElementsByTagName("div")[0].style.display= "";

    let button = document.getElementById("connectButton");
    button.addEventListener("keyup", function (event){
        if (event.key === "Enter")
        {
            button.click();
        }
    });
    
    
}
function showGame()
{
    document.getElementById("infoSection").style.display= "";
    document.getElementById("gameSection").style.display= "";
    document.getElementById("chatSection").style.display= "";
}
function hideGame()
{
    document.getElementById("infoSection").style.display= "None";
    document.getElementById("gameSection").style.display= "None";
    document.getElementById("chatSection").style.display= "None";
}



function connect()
{
    playerName = document.getElementById("playerName").value;
    hideUsernameInput();
    socket.emit("addPlayer", playerName);
}
function waitForPlayer()
{
    socket.on('updatePlayerNumber', function(n) {
        document.getElementById("nbPlayer").textContent = n;
    });
    socket.on('playerRemoved', function(n) {
        document.getElementById("nbPlayer").textContent = n;
    });

    socket.on('start', function(gameInfo) {
        socket.off('start');
        socket.off('updatePlayerNumber');
        socket.off('playerRemoved');
        start(gameInfo);
    });
}




function handleReset()
{
    socket.on('reset', function() {
        reset();
    });

    socket.io.on("error", function() {
        reset();
    });
}
function reset()
{
    window.location.reload(true);
}

function deletePlayer()
{
    let players = document.getElementsByClassName("player");
    let playerLen = players.length;
    for (let i = playerLen-1; i >= 0 ; i--)
    {
        players[i].remove();
    }
}



function start(gameInfo)
{
    hideConnectForm();
    showGame();

    createPlayers(gameInfo['nbPlayers'], gameInfo['usernames']);
    drawPlayers();

    setupChat();

    socket.on('gameMessage', function(data) {
        const formattedData = data.replace(/\n/g, '<br>');
        document.getElementById("gameMessages").innerHTML = formattedData;
    });


    socket.once("ownRole", function(data) {
        document.getElementById("ownRole").src = "./images/"+data+".png"
        document.getElementById("ownRoleText").textContent = data
    })

    socket.on('role', function(data) {
        const role = data["role"]
        const additionalData = data["data"]
        if (role=="cupidon")
        {
            cupidon(additionalData);
        }
        else if (role=="voyante")
        {
            voyante(additionalData);
        }
        else if (role=="loup")
        {
            loup(additionalData);
        }
        else if (role=="sorciere")
        {
            sorciere(additionalData);
        }
        else if (role=="vote")
        {
            vote(additionalData);
        }
});

    socket.on('privateMessage', function(data){
        const formattedData = data.replace(/\n/g, '<br>');
        let privateDiv = document.getElementById("privateMessage")
        privateDiv.getElementsByTagName("p")[0].innerHTML = formattedData;
    });


    socket.on('isDead', function(data){
        let playerDiv = document.getElementById(data["username"])
        playerDiv.classList.add("dead")

        let playerImage = playerDiv.getElementsByTagName("img")[0]
        playerImage.src = "./images/"+data["role"]+".png"

        let img = document.createElement('img');
        img.src = "./images/deadCross.png"
        img.style.height = "75%"
        img.style.width = "100%"
        img.style.position = "absolute"
        img.style.top = "0px"
        img.style.left = "0px"
        playerDiv.appendChild(img)
    });

    socket.on('showSomeoneRole', function(data){
        let playerDiv = document.getElementById(data["username"])
        let playerImage = playerDiv.getElementsByTagName("img")[0]
        playerImage.src = "./images/"+data["role"]+".png"
    });

    socket.on('hideSomeoneRole', function(data){
        let playerDiv = document.getElementById(data["username"])
        let playerImage = playerDiv.getElementsByTagName("img")[0]
        playerImage.src = "./images/cardBack.jpg"
    });
}




function cupidon(data)
{
    let nbSelected = 0;
    let selected1 = {"element":null, "username":null};
    let selected2 = {"element":null, "username":null};

    const clickEventFunction = function(event) {
        if (!event.currentTarget.classList.contains("clicked"))
        {
            if (nbSelected==2)
            {
                alert("can not select more than two player !");
                return
            }
            nbSelected+=1;
            
            if (nbSelected==1)
            {
                selected1["element"] = event.currentTarget;
                selected1["username"] = event.currentTarget.getElementsByClassName("username")[0].textContent;
            }
            if (nbSelected==2)
            {
                selected2["element"] = event.currentTarget;
                selected2["username"] = event.currentTarget.getElementsByClassName("username")[0].textContent;
                document.body.appendChild(validateButton);
            }

            event.currentTarget.classList.add("clicked");
            event.currentTarget.style.outline = "6px solid green";
        }
        else
        {
            if (nbSelected==2) {document.body.removeChild(validateButton)}
            nbSelected-=1;
            event.currentTarget.classList.remove("clicked");
            event.currentTarget.style.outline = "none";
        }
    };
    addEventToAllPlayer("click", clickEventFunction);


    const validateEventFunction = function(event)
    {
        removeEventToAllPlayer("click", clickEventFunction)
        document.body.removeChild(validateButton)
        let privateDiv = document.getElementById("privateMessage")
        privateDiv.getElementsByTagName("p")[0].innerHTML = "";
        
        nbSelected = 0;

        selected1["element"].style.outline = "none";
        selected1["element"].classList.remove("clicked");

        selected2["element"].style.outline = "none";
        selected2["element"].classList.remove("clicked");

        socket.emit("roundResult",
        {
            "round":"cupidon",
            "data":{"lover1":selected1["username"], "lover2":selected2["username"]}
        })
    }
    
    let validateButton = document.createElement("button");
    validateButton.id = "validateButton";
    validateButton.textContent="validate"
    validateButton.addEventListener("click", validateEventFunction)
}

function voyante(data)
{
    let nbSelected = 0;
    let selected = {"element":null, "username":null};

    const clickEventFunction = function(event) {
        if (!event.currentTarget.classList.contains("clicked"))
        {
            if (nbSelected==1)
            {
                alert("vous ne pouvez pas choisir plus d'une seule personne !");
                return;
            }
            if (event.currentTarget.classList.contains("dead"))
            {
                alert("vous ne pouvez pas choisir quelqu'un de déjà mort !");
                return;
            }
            nbSelected+=1;
            
            selected["element"] = event.currentTarget;
            selected["username"] = event.currentTarget.getElementsByClassName("username")[0].textContent;
            
            document.body.appendChild(validateButton);

            event.currentTarget.classList.add("clicked");
            event.currentTarget.style.outline = "6px solid green";
        }
        else
        {
            document.body.removeChild(validateButton)
            nbSelected-=1;
            event.currentTarget.classList.remove("clicked");
            event.currentTarget.style.outline = "none";
        }
    };
    addEventToAllPlayer("click", clickEventFunction);


    const validateEventFunction = function(event)
    {
        removeEventToAllPlayer("click", clickEventFunction)
        document.body.removeChild(validateButton)
        let privateDiv = document.getElementById("privateMessage")
        privateDiv.getElementsByTagName("p")[0].innerHTML = "";

        nbSelected = 0;

        selected["element"].style.outline = "none";
        selected["element"].classList.remove("clicked");

        socket.emit("roundResult",
        {
            "round":"voyante",
            "data":{"username":selected["username"]}
        })
    }
    
    let validateButton = document.createElement("button");
    validateButton.id = "validateButton";
    validateButton.textContent="validate"
    validateButton.addEventListener("click", validateEventFunction)
}

function loup(data)
{
    let nbSelected = 0;
    let selected = {"element":null, "username":null};

    const clickEventFunction = function(event) {
        if (!event.currentTarget.classList.contains("clicked"))
        {
            if (nbSelected==1)
            {
                alert("vous ne pouvez pas choisir plus d'une seule personne !");
                return;
            }
            if (event.currentTarget.classList.contains("dead"))
            {
                alert("vous ne pouvez pas choisir quelqu'un de déjà mort !");
                return;
            }
            nbSelected+=1;
            
            selected["element"] = event.currentTarget;
            selected["username"] = event.currentTarget.getElementsByClassName("username")[0].textContent;

            socket.emit("loupGraphicalInfo",
            {
                "targetUsername":selected["username"],
                "action":"add"
            })


            document.body.appendChild(validateButton);

            event.currentTarget.classList.add("clicked");
            event.currentTarget.style.outline = "6px solid green";
        }
        else
        {
            socket.emit("loupGraphicalInfo",
            {
                "targetUsername":selected["username"],
                "action":"remove"
            })

            document.body.removeChild(validateButton)
            nbSelected-=1;
            event.currentTarget.classList.remove("clicked");
            event.currentTarget.style.outline = "none";
        }
    };
    addEventToAllPlayer("click", clickEventFunction);

 
    socket.on("loupAddChoice", function(data){
        let loupName = data["username"];
        let targetName = data["target"];

        let targetDiv = document.getElementById(targetName);
        let additionalInfoDiv = targetDiv.getElementsByClassName("additionalInfo")[0];
        let info = document.createElement("p");
        info.id = "target_"+loupName;
        info.textContent = loupName + " -> " + targetName;

        additionalInfoDiv.appendChild(info);
    });

    socket.on("loupRemoveChoice", function(data){
        let loupName = data["username"];
        document.getElementById("target_"+loupName).remove();
    });

    socket.once("loupRemoveListener", function(data){
        socket.off('loupAddChoice');
        socket.off('loupRemoveChoice');
    });


    const validateEventFunction = function(event)
    {
        removeEventToAllPlayer("click", clickEventFunction)

        document.body.removeChild(validateButton)
        let privateDiv = document.getElementById("privateMessage")
        privateDiv.getElementsByTagName("p")[0].innerHTML = "";

        nbSelected = 0;

        selected["element"].style.outline = "none";
        selected["element"].classList.remove("clicked");

        socket.emit("roundResult",
        {
            "round":"loups",
            "data":{"targetUsername":selected["username"]}
        })
    }

    let validateButton = document.createElement("button");
    validateButton.id = "validateButton";
    validateButton.textContent="validate"
    validateButton.addEventListener("click", validateEventFunction)
}


resurrectButtonUsed = false;
killSomeoneElseButtonUsed = false;
function sorciere(data)
{
    let menuDiv = document.createElement("div");
    menuDiv.id = "sorciereMenu";
    menuDiv.style.display = "flex";
    menuDiv.style.justifyContent = "center";
    menuDiv.style.flexDirection = "column";

    let doNothingButton = document.createElement("button");
    let resurrectButton = document.createElement("button");
    let killSomeoneElseButton = document.createElement("button");

    doNothingButton.type = "button";
    resurrectButton.type = "button";
    killSomeoneElseButton.type = "button";

    doNothingButton.id = "doNothing";
    resurrectButton.id = "resurrect";
    killSomeoneElseButton.id = "killSomeoneElse";

    doNothingButton.textContent = "ne rien faire";
    resurrectButton.textContent = "récussiter";
    killSomeoneElseButton.textContent = "tuer quelqu'un d'autre";

    doNothingButton.style.marginTop = "3%";
    doNothingButton.style.marginBottom = "3%";
    resurrectButton.style.marginTop = "3%";
    resurrectButton.style.marginBottom = "3%";
    killSomeoneElseButton.style.marginTop = "3%";
    killSomeoneElseButton.style.marginBottom = "3%";

    menuDiv.appendChild(doNothingButton);

    if (resurrectButtonUsed===false)
    {
        menuDiv.appendChild(resurrectButton);
    }
    if (killSomeoneElseButtonUsed===false)
    {
        menuDiv.appendChild(killSomeoneElseButton);
    }
    
    document.getElementById("privateMessage").appendChild(menuDiv);


    doNothingButton.addEventListener("click", function()
    {
        menuDiv.remove();
        let privateDiv = document.getElementById("privateMessage")
        privateDiv.getElementsByTagName("p")[0].innerHTML = "";

        socket.emit("roundResult",
        {
            "round":"sorciere",
            "data":{"action":"doNothing"}
        })
    });

    resurrectButton.addEventListener("click", function()
    {
        resurrectButtonUsed = true;
        menuDiv.remove();
        let privateDiv = document.getElementById("privateMessage")
        privateDiv.getElementsByTagName("p")[0].innerHTML = "";

        socket.emit("roundResult",
        {
            "round":"sorciere",
            "data":{"action":"resurrect"}
        })
    });

    killSomeoneElseButton.addEventListener("click", function()
    {
        killSomeoneElseButtonUsed = true;
        menuDiv.remove();
        let privateDiv = document.getElementById("privateMessage")
        privateDiv.getElementsByTagName("p")[0].innerHTML = "clique sur la personne que tu veux tuer";

        let nbSelected = 0;
        let selected = {"element":null, "username":null};
    
        const clickEventFunction = function(event) {
            if (!event.currentTarget.classList.contains("clicked"))
            {
                if (nbSelected==1)
                {
                    alert("vous ne pouvez pas choisir plus d'une seule personne !");
                    return;
                }
                if (event.currentTarget.classList.contains("dead"))
                {
                    alert("vous ne pouvez pas choisir quelqu'un de déjà mort !");
                    return;
                }
                nbSelected+=1;
                
                selected["element"] = event.currentTarget;
                selected["username"] = event.currentTarget.getElementsByClassName("username")[0].textContent;
                
                document.body.appendChild(validateButton);
    
                event.currentTarget.classList.add("clicked");
                event.currentTarget.style.outline = "6px solid green";
            }
            else
            {
                document.body.removeChild(validateButton)
                nbSelected-=1;
                event.currentTarget.classList.remove("clicked");
                event.currentTarget.style.outline = "none";
            }
        };
        addEventToAllPlayer("click", clickEventFunction);
    
        const validateEventFunction = function(event)
        {
            removeEventToAllPlayer("click", clickEventFunction)
            document.body.removeChild(validateButton)
            let privateDiv = document.getElementById("privateMessage")
            privateDiv.getElementsByTagName("p")[0].innerHTML = "";

            nbSelected = 0;
    
            selected["element"].style.outline = "none";
            selected["element"].classList.remove("clicked");
            
            socket.emit("roundResult",
            {
                "round":"sorciere",
                "data":{"action":"killSomeoneElse", "username":selected["username"]}
            })
        }
        
        let validateButton = document.createElement("button");
        validateButton.id = "validateButton";
        validateButton.textContent="validate"
        validateButton.addEventListener("click", validateEventFunction)
    });
}

function vote(data)
{
    let nbSelected = 0;
    let selected = {"element":null, "username":null};

    const clickEventFunction = function(event) {
        if (!event.currentTarget.classList.contains("clicked"))
        {
            if (nbSelected==1)
            {
                alert("vous ne pouvez pas choisir plus d'une seule personne !");
                return;
            }
            if (event.currentTarget.classList.contains("dead"))
            {
                alert("vous ne pouvez pas choisir quelqu'un de déjà mort !");
                return;
            }
            nbSelected+=1;
            
            selected["element"] = event.currentTarget;
            selected["username"] = event.currentTarget.getElementsByClassName("username")[0].textContent;

            socket.emit("voteGraphicalInfo",
            {
                "targetUsername":selected["username"],
                "action":"add"
            })


            document.body.appendChild(validateButton);

            event.currentTarget.classList.add("clicked");
            event.currentTarget.style.outline = "6px solid green";
        }
        else
        {
            socket.emit("voteGraphicalInfo",
            {
                "targetUsername":selected["username"],
                "action":"remove"
            })

            document.body.removeChild(validateButton)
            nbSelected-=1;
            event.currentTarget.classList.remove("clicked");
            event.currentTarget.style.outline = "none";
        }
    };
    addEventToAllPlayer("click", clickEventFunction);

 
    socket.on("voteAddChoice", function(data){
        let voterName = data["username"];
        let targetName = data["target"];

        let targetDiv = document.getElementById(targetName);
        let additionalInfoDiv = targetDiv.getElementsByClassName("additionalInfo")[0];
        let info = document.createElement("p");
        info.id = "target_"+voterName;
        info.textContent = voterName + " -> " + targetName;

        additionalInfoDiv.appendChild(info);
    });

    socket.on("voteRemoveChoice", function(data){
        let voterName = data["username"];
        document.getElementById("target_"+voterName).remove();
    });

    socket.once("voteRemoveListener", function(data){
        socket.off('voteAddChoice');
        socket.off('voteRemoveChoice');
    });


    const validateEventFunction = function(event)
    {
        removeEventToAllPlayer("click", clickEventFunction)

        document.body.removeChild(validateButton)
        let privateDiv = document.getElementById("privateMessage")
        privateDiv.getElementsByTagName("p")[0].innerHTML = "";

        nbSelected = 0;

        selected["element"].style.outline = "none";
        selected["element"].classList.remove("clicked");

        socket.emit("roundResult",
        {
            "round":"vote",
            "data":{"targetUsername":selected["username"]}
        })
    }

    let validateButton = document.createElement("button");
    validateButton.id = "validateButton";
    validateButton.textContent="validate"
    validateButton.addEventListener("click", validateEventFunction)
}



function addEventToAllPlayer(name, func)
{
    let players = document.getElementsByClassName("player");
    for (let i = 0; i < players.length; i++)
    {
        players[i].addEventListener(name, func);
    }    
}
function removeEventToAllPlayer(name, func)
{
    let players = document.getElementsByClassName("player");
    for (let i = 0; i < players.length; i++)
    {
        players[i].removeEventListener(name, func);
    }    
}






function addClickEvent(element)
{
    const clickEventFunction = function() {
        if (!element.classList.contains("clicked"))
        {
            element.classList.add("clicked");
            element.style.outline = "6px solid green";
        }
        else
        {
            element.classList.remove("clicked");
            element.style.outline = "none";
        }
    };
    element.addEventListener("click", clickEventFunction);
}
function addHoverEvent(element)
{
    hoverEventFunction = function()
    {
        if (!element.classList.contains("clicked"))
        {
            element.style.outline = "3px solid red"
        }
    }
    outEventFunction = function()
    {
        if (!element.classList.contains("clicked"))
        {
            element.style.outline = "none";
        }
    }

    element.addEventListener("mouseover", hoverEventFunction);
    element.addEventListener("mouseout", outEventFunction)
}

function removeClickEvent(element)
{
    element.removeEventListener("click", clickEventFunction);
}
function removeHoverEvent(element)
{
    element.removeEventListener("mouseover", hoverEventFunction);
    element.removeEventListener("mouseout", outEventFunction);
}





function createPlayers(n, usernames)
{
    let gameSection = document.getElementById("gameSection");

    for (let i = 0; i < n; i++)
    {
        let img = document.createElement('img');
        img.src = "./images/cardBack.jpg"
        img.style.height = "75%"
        img.style.width = "100%"
          
        let username = document.createElement('p');
        username.classList.add("username");
        username.style.marginTop="5%";
        username.style.marginBottom="8%";
        username.style.marginLeft="0%";
        username.style.marginRight="0%";
        username.style.width = "100%"
        username.style.textAlign = "center"

        let additionalInfo = document.createElement('div');
        additionalInfo.classList.add("additionalInfo");
        additionalInfo.style.margin="0";
        additionalInfo.style.padding="0";
        additionalInfo.style.width = "100%"
        additionalInfo.style.textAlign = "center"
    
        let div = document.createElement('div');
        div.className = "player"
        div.style.backgroundColor = "black"
        div.style.position = "absolute"
        div.style.width = "11vh"
        div.style.height = "14vh"
        addHoverEvent(div);

        if (usernames[i] == playerName)
        {
            username.style.color = "red";
        }
        username.textContent = usernames[i];
        div.id = usernames[i];

        div.appendChild(img)
        div.appendChild(username)
        div.appendChild(additionalInfo)

        gameSection.appendChild(div);
    }
}

function drawPlayers()
{
    let players = document.getElementsByClassName("player");
    var ratio = window.innerWidth/window.innerHeight;

    for (let i = 0; i < players.length; i++)
    {
        players[i].style.top = Math.round(Math.sin(i/players.length * 2*Math.PI) * 40 + 50).toString()+"%"
        players[i].style.left = Math.round(Math.cos(i/players.length * 2*Math.PI) * 40 + 50).toString()+"%"
        players[i].style.transform = "translate(-50%, -50%)"
    }
    window.addEventListener("resize", drawPlayers);
}



function setupChat()
{
    const messagesDiv = document.getElementById('messagesList');
    const messageInput = document.getElementById('message');
    const sendButton = document.getElementById('send');
    
    let chatEnabled = true;
    
    function toggleChat(enable) {
        chatEnabled = enable;
        messageInput.disabled = !enable;
        sendButton.disabled = !enable;
    }
    
    sendButton.addEventListener('click', () => {
        const message = messageInput.value.trim();
        if (message && chatEnabled) {
            socket.emit('chatMessage', message);
            messageInput.value = '';
        }
    });

    messageInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            sendButton.click();
        }
    });

    socket.on('chatMessage', function (data) {
        const div = document.createElement('div');
        div.innerHTML = '<span style="color:red">'+data["username"]+": </span>";
        div.innerHTML += data["message"];
        messagesDiv.appendChild(div);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    });
    
    socket.on('toggleChat', (enable) => {
        toggleChat(enable);
    });
}







socket = io();

// socket.emit("addPlayer", "a");
// socket.emit("addPlayer", "b");
// socket.emit("addPlayer", "c");
// socket.emit("addPlayer", "d");
// socket.emit("addPlayer", "e");
// socket.emit("addPlayer", "f");

hideGame()
showForm()

waitForPlayer();
handleReset();





function serverDebug()
{
    socket.emit("debug", "")
}