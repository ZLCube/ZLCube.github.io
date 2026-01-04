const FRACTIONS = [
  { text: "1/2", value: 0.5 },
  { text: "1/3", value: 1 / 3 },
  { text: "2/3", value: 2 / 3 },
  { text: "1/4", value: 0.25 },
  { text: "3/4", value: 0.75 }
];

let deck = [];
let player = [];
let board = [];
let selectedIndex = null;
let turn = "player";

// ---------- SETUP ----------
function createTile() {
  const frac = FRACTIONS[Math.floor(Math.random() * FRACTIONS.length)];
  const pie = FRACTIONS[Math.floor(Math.random() * FRACTIONS.length)];

  return {
    frac,
    pie
  };
}

function createDeck() {
  deck = [];
  for (let i = 0; i < 20; i++) {
    deck.push(createTile());
  }
  deck.sort(() => Math.random() - 0.5);
}

function draw(hand) {
  if (deck.length > 0) hand.push(deck.pop());
}

function startGame() {
  createDeck();
  player = [];
  board = [];
  selectedIndex = null;

  for (let i = 0; i < 6; i++) draw(player);

  update("Tu turno");
  render();
}

// ---------- RENDER ----------
function renderTile(tile) {
  const div = document.createElement("div");
  div.className = "tile";

  const left = document.createElement("div");
  left.className = "half";
  left.textContent = tile.frac.text;

  const right = document.createElement("div");
  right.className = "half";

  const pie = document.createElement("div");
  pie.className = "pie";
  pie.style.setProperty("--angle", `${tile.pie.value * 360}deg`);

  right.appendChild(pie);

  div.appendChild(left);
  div.appendChild(right);

  return div;
}

function render() {
  const hand = document.getElementById("player-hand");
  const boardDiv = document.getElementById("board");
  hand.innerHTML = "";
  boardDiv.innerHTML = "";

  player.forEach((tile, i) => {
    const t = renderTile(tile);
    if (i === selectedIndex) t.classList.add("selected");
    t.onclick = () => {
      selectedIndex = i;
      render();
    };
    hand.appendChild(t);
  });

  board.forEach(tile => {
    boardDiv.appendChild(renderTile(tile));
  });
}

// ---------- GAME LOGIC ----------
function matches(tile, boardTile, side) {
  if (side === "left") {
    return tile.frac.value === boardTile.frac.value ||
           tile.pie.value === boardTile.frac.value;
  } else {
    return tile.frac.value === boardTile.pie.value ||
           tile.pie.value === boardTile.pie.value;
  }
}

function flip(tile) {
  return {
    frac: tile.pie,
    pie: tile.frac
  };
}

function play(side) {
  if (selectedIndex === null) return;

  let tile = player[selectedIndex];

  if (board.length === 0) {
    board.push(tile);
  } else {
    const ref = side === "left" ? board[0] : board[board.length - 1];

    if (matches(tile, ref, side)) {
      // ok
    } else if (matches(flip(tile), ref, side)) {
      tile = flip(tile);
    } else {
      update("Movimiento inválido");
      return;
    }

    side === "left" ? board.unshift(tile) : board.push(tile);
  }

  player.splice(selectedIndex, 1);
  selectedIndex = null;

  if (player.length === 0) {
    update("🎉 ¡Ganaste!");
  } else {
    update("Tu turno");
  }

  render();
}

function playLeft() { play("left"); }
function playRight() { play("right"); }

function drawPlayer() {
  draw(player);
  render();
}

// ---------- UI ----------
function update(msg) {
  document.getElementById("status").textContent = msg;
}

startGame();
