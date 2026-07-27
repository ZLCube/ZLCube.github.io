# ZLCube Daily Hacking Challenges

Hub estático pensado para:

    zlcube.com/redbull/

## Estructura

```text
redbull/
├── index.html
├── assets/
│   └── background.png
├── css/
│   └── style.css
└── js/
    ├── challenges.js
    └── main.js
```

## Día 1 — XSS

El primer reto es deliberadamente vulnerable y funciona únicamente en el navegador.

La demo acepta:

```html
<script>alert(1)</script>
```

y también payloads basados en eventos HTML.

No existe flag. El reto termina cuando el usuario consigue ejecución de JavaScript.

## Agregar un nuevo día

Edita `js/challenges.js` y agrega otro objeto al arreglo:

```js
{
  day: 4,
  tag: "NUEVO",
  title: "Nombre del reto",
  description: "Descripción corta.",
  objective: "Qué tiene que conseguir el jugador.",
  hint: "Una pista.",
  unlocked: true,
  type: "nombre-del-handler"
}
```

Después implementa el comportamiento correspondiente en `runChallenge()` dentro de `js/main.js`.

## Publicación en GitHub Pages

Copia la carpeta completa dentro de tu repositorio, por ejemplo:

```text
/redbull/
```

y enlázala desde tu página principal.

El header usa `../` para volver a la página anterior. Si deseas volver a una URL concreta, cambia:

```html
<a class="back-link" href="../">
```

por la ruta deseada.

## Seguridad

Este proyecto está diseñado como laboratorio educativo estático.

No añadas:
- tokens;
- secretos;
- cookies sensibles;
- autenticación real;
- endpoints privilegiados;
- información de terceros.

El código vulnerable de `main.js` está ahí de forma intencional.
