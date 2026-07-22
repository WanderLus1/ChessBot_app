// -----------------------------------------------------
// Chess objects
// -----------------------------------------------------

let game = new Chess();

let board = null;


// -----------------------------------------------------
// Replay
// -----------------------------------------------------

let replayGame = new Chess();

let replayMoves = [];

let replayIndex = 0;


// -----------------------------------------------------
// Current side
// -----------------------------------------------------

let playerColor = "white";


// -----------------------------------------------------
// Create chessboard
// -----------------------------------------------------

board = Chessboard("board", {

    draggable: true,

    position: "start",

    pieceTheme:
        "https://chessboardjs.com/img/chesspieces/wikipedia/{piece}.png",

    onDrop: onDrop

});


// -----------------------------------------------------
// Buttons
// -----------------------------------------------------

document
    .getElementById("play-white")
    .addEventListener("click", function () {

        playerColor = "white";

        startNewGame();

    });


document
    .getElementById("play-black")
    .addEventListener("click", function () {

        playerColor = "black";

        startNewGame();

    });


document
    .getElementById("new-game")
    .addEventListener("click", function () {

        startNewGame();

    });


document
    .getElementById("flip-board")
    .addEventListener("click", function () {

        board.flip();

    });


// -----------------------------------------------------
// Start game
// -----------------------------------------------------

function startNewGame() {

    $("#status").text("Starting game...");

    $.ajax({

        url: "/new_game",

        type: "POST",

        contentType: "application/json",

        data: JSON.stringify({

            color:
                playerColor === "white"
                    ? "black"
                    : "white"

        }),

        success: function (response) {

            game.load(response.fen);

            board.position(response.fen);

            replayGame.load(response.fen);

            replayMoves = [];

            replayIndex = 0;

            updateHistory(response.history);

            updateDecision(
                response.sources
            );

            $("#status").text("Your move.");

        }

    });

}


// -----------------------------------------------------
// Player move
// -----------------------------------------------------

function onDrop(source, target) {
    if (game.game_over())
    return "snapback";
    let piece = game.get(source);

    if (!piece)
        return "snapback";

    let move = {
        from: source,
        to: target
    };

    // Promotion
    if (
        piece.type === "p" &&
        (
            (piece.color === "w" && target[1] === "8") ||
            (piece.color === "b" && target[1] === "1")
        )
    ) {

        let promotion = prompt(
            "Promote to (q, r, b, n):",
            "q"
        );

        if (!promotion)
            return "snapback";

        promotion = promotion.toLowerCase();

        if (!["q", "r", "b", "n"].includes(promotion))
            promotion = "q";

        move.promotion = promotion;
    }

    let result = game.move(move);

    if (result === null)
        return "snapback";

    board.position(game.fen());

    $("#status").text("Model thinking...");

    let uci = result.from + result.to;

    if (result.promotion)
        uci += result.promotion;

    sendMove(uci);

}


// -----------------------------------------------------
// Send move to Flask
// -----------------------------------------------------

function sendMove(move) {

    $.ajax({

        url: "/move",

        type: "POST",

        contentType: "application/json",

        data: JSON.stringify({

            move: move

        }),

        success: function (response) {

            if (!response.success) {

                alert(response.message);

                return;

            }

            game.load(response.fen);

            board.position(response.fen);

            replayMoves = response.moves;

            resetReplay();

            updateHistory(response.history);

            updateDecision(response.sources);

            if (response.game_over) {

    let text = "";

    switch(response.termination){

        case "CHECKMATE":
            text = "Checkmate • " + response.result;
            break;

        case "STALEMATE":
            text = "Draw by Stalemate";
            break;

        case "INSUFFICIENT_MATERIAL":
            text = "Draw by Insufficient Material";
            break;

        case "THREEFOLD_REPETITION":
            text = "Draw by Threefold Repetition";
            break;

        case "FIFTY_MOVES":
            text = "Draw by Fifty-Move Rule";
            break;

        default:
            text = "Game Over • " + response.result;

    }

    $("#status").text(text);

    board.draggable = false;

    return;

}

            else {

                $("#status").text(

                    "Your move."

                );

            }

        }

    });

}
// -----------------------------------------------------
// Move History
// -----------------------------------------------------

function updateHistory(history) {

    let html = "";

    for (let i = 0; i < history.length; i += 2) {

        let moveNo = Math.floor(i / 2) + 1;

        let white = history[i] || "";

        let black = history[i + 1] || "";

        html += `
            <div class="move-row">
                <span class="move-number">${moveNo}.</span>
                <span class="white-move">${white}</span>
                <span class="black-move">${black}</span>
            </div>
        `;
    }

    if (html === "")
        html = "No moves yet.";

    $("#move-history").html(html);

}


// -----------------------------------------------------
// MODEL / OVERRIDE
// -----------------------------------------------------

function updateDecision(sourceHistory) {

    if (sourceHistory.length === 0) {

        $("#decision").text("-");

        return;

    }

    let last = sourceHistory[sourceHistory.length - 1];

    if (last === "MODEL") {

        $("#decision").html("✔ MODEL");

    }

    else if (last === "OVERRIDE") {

        $("#decision").html("⚙ STOCKFISH OVERRIDE");

    }

    else {

        $("#decision").html("♔ ENDGAME");

    }

}


// -----------------------------------------------------
// Replay
// -----------------------------------------------------

function showReplayPosition(index) {

    let replay = new Chess();

    for (let i = 0; i < index; i++) {

        replay.move({

            from: replayMoves[i].substring(0, 2),

            to: replayMoves[i].substring(2, 4),

            promotion: "q"

        });

    }

    board.position(replay.fen());

}


// -----------------------------------------------------
// Keyboard
// -----------------------------------------------------

document.addEventListener("keydown", function (event) {

    if (replayMoves.length === 0)
        return;

    if (event.key === "ArrowLeft") {

        if (replayIndex > 0) {

            replayIndex--;

            showReplayPosition(replayIndex);

        }

    }

    if (event.key === "ArrowRight") {

        if (replayIndex < replayMoves.length) {

            replayIndex++;

            showReplayPosition(replayIndex);

        }

    }

});


// -----------------------------------------------------
// Sync replay after every move
// -----------------------------------------------------

function resetReplay() {

    replayIndex = replayMoves.length;

}