/*
 * Agrega un objeto nuevo por cada día.
 * El HTML se genera dinámicamente.
 *
 * IMPORTANTE:
 * Los retos de este proyecto son deliberadamente client-side.
 * No guardes tokens, cookies, credenciales o secretos reales aquí.
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
    tag: "LOCKED",
    title: "Próximamente",
    description:
      "El siguiente reto se desbloqueará con el próximo video de la serie.",
    objective: "",
    hint: "",
    unlocked: false,
    type: null
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
