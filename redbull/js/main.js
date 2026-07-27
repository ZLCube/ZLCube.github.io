const challenges = window.ZLCUBE_CHALLENGES || [];
const grid = document.getElementById("challengeGrid");
const template = document.getElementById("challengeTemplate");
const count = document.getElementById("challengeCount");

count.textContent = String(challenges.length).padStart(2, "0");

function runXssLab(value, output, card) {
  const originalAlert = window.alert;

  window.alert = function(message) {
    originalAlert(message);

    card.classList.add("is-completed");

    const action = card.querySelector(".challenge-action");
    action.innerHTML = "COMPLETED ✓";

    const tag = card.querySelector(".challenge-tag");
    tag.textContent = "PWNED";

    setTimeout(() => {
      output.innerHTML = `
        <div class="challenge-completed">
          <strong>✓ CHALLENGE COMPLETED</strong>
          <span>JavaScript execution achieved.</span>
        </div>
      `;
    }, 100);
  };

  output.innerHTML = value;

  output.querySelectorAll("script").forEach((oldScript) => {
    const executableScript = document.createElement("script");

    for (const attribute of oldScript.attributes) {
      executableScript.setAttribute(attribute.name, attribute.value);
    }

    executableScript.textContent = oldScript.textContent;
    oldScript.replaceWith(executableScript);
  });
}

function runChallenge(challenge, value, output, card) {
  if (challenge.type === "xss") {
    runXssLab(value, output, card);
    return;
  }

  output.textContent = "> challenge no implementado";
}

function createChallengeCard(challenge) {
  const node = template.content.cloneNode(true);

  const card = node.querySelector(".challenge-card");
  const summary = node.querySelector(".challenge-summary");
  const content = node.querySelector(".challenge-content");

  node.querySelector(".challenge-day").textContent =
    `DAY ${String(challenge.day).padStart(2, "0")}`;

  node.querySelector(".challenge-tag").textContent = challenge.tag;
  node.querySelector(".challenge-title").textContent = challenge.title;
  node.querySelector(".challenge-description").textContent = challenge.description;

  const action = node.querySelector(".challenge-action");

  if (!challenge.unlocked) {
    card.classList.add("is-locked");
    action.textContent = "LOCKED";
    summary.disabled = true;
    return node;
  }

  node.querySelector(".challenge-objective-text").textContent =
    challenge.objective;

  const hintText = node.querySelector(".hint-text");
  hintText.textContent = challenge.hint;

  summary.addEventListener("click", () => {
    const opening = content.hidden;

    content.hidden = !opening;
    summary.setAttribute("aria-expanded", String(opening));
    card.classList.toggle("is-open", opening);
    action.innerHTML = opening ? 'CERRAR <b>↑</b>' : 'ABRIR <b>→</b>';
  });

  const form = node.querySelector(".lab-form");
  const input = node.querySelector(".lab-input");
  const output = node.querySelector(".output-content");

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    const value = input.value;

    if (!value.trim()) {
      output.textContent = "> introduce un payload";
      return;
    }

    runChallenge(challenge, value, output, card);
  });

  const hintButton = node.querySelector(".hint-button");

  hintButton.addEventListener("click", () => {
    const hidden = hintText.hidden;
    hintText.hidden = !hidden;
    hintButton.textContent = hidden ? "OCULTAR PISTA" : "MOSTRAR PISTA";
  });

  return node;
}

challenges.forEach((challenge) => {
  grid.appendChild(createChallengeCard(challenge));
});
