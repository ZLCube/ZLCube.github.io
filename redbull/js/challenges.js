/*
 * Agrega un objeto nuevo por cada día.
 * El HTML se genera dinámicamente.
 */

window.ZLCUBE_CHALLENGES = [
  {
    day: 1,
    tag: "XSS",
    title: "Cross-Site Scripting",
    description:
      "Este reto consta de conseguir que el navegador ejecute JavaScript desde una entrada controlada por el usuario.",
    objective:
      "Encuentra una forma de hacer que el contenido introducido en el campo termine ejecutándose como JavaScript.",
    hint:
      "Tu input termina dentro del DOM. Prueba primero con HTML y después busca una forma de disparar JavaScript.",
    unlocked: true,
    type: "xss"
  },
  {
    day: 2,
    tag: "SQLi",
    title: "SQL Injection",
    description:
      "Manipula la lógica de una consulta SQL utilizando una entrada controlada por el usuario.",
    objective:
      "Consigue que la consulta resulte verdadera sin conocer la contraseña.",
    hint:
      "Observa dónde aparecen las comillas de tu entrada dentro del query.",
    unlocked: true,
    type: "sqli"
  },
  {
    day: 3,
    tag: "LOCKED",
    title: "Próximamente",
    description:
      "Nuevo día, nueva vulnerabilidad. Todavía no disponible.",
    objective: "",
    hint: "",
    unlocked: false,
    type: null
  }
];
