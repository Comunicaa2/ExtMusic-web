# ExtMusic · web

Sitio web de [ExtMusic](https://github.com/Comunicaa2/ExtMusic), un reproductor de música libre para Android.
Es un sitio estático para GitHub Pages: HTML y CSS escritos a mano, sin dependencias y sin paso de construcción.

> Estado: **prototipo de la página principal** (Fase 4). Todavía no está publicado.

## Estructura

```
index.html                  Página principal (español)
versiones.html              Versión actual, instalación, comprobación y historial
privacidad.html             Privacidad y seguridad (hechos comprobados en el código)
documentacion.html          Documentación de uso, solución de problemas y FAQ (textos literales de la app)
en/                         Versión en inglés: index.html, versions.html, privacy.html, docs.html
404.html                    Página de error bilingüe (GitHub Pages la sirve en cualquier ruta inexistente)
sitemap.xml, robots.txt     Para buscadores: las 8 páginas con sus alternativas de idioma
.nojekyll                   GitHub Pages sirve los archivos tal cual, sin Jekyll
assets/css/extmusic.css     Sistema de diseño «Datasheet»: tokens + componentes, claro y oscuro automático
assets/fonts/               Hanken Grotesk y JetBrains Mono (SIL OFL 1.1, subconjunto latino) + licencias
assets/img/icono.svg        Icono de la app; icono-32/192/512.png y apple-touch-icon.png derivados de él
assets/img/capturas/        Capturas reales de la app en WebP (360, 540 y 720 px de ancho)
```

## Reglas

- **Rutas siempre relativas** (`assets/...`). El sitio se publica en `https://comunicaa2.github.io/ExtMusic-web/`, no en la raíz de un dominio. **Única excepción: `404.html`**, que usa rutas absolutas `/ExtMusic-web/...` porque GitHub Pages la sirve en cualquier ruta (también dentro de `en/`).
- **Sin recursos externos.** Las fuentes y las imágenes se sirven desde el propio sitio, y no hay analíticas ni scripts de terceros.
- **Dos idiomas sincronizados.** Cada página en español tiene su equivalente en `en/` (index↔index, versiones↔versions, privacidad↔privacy, documentacion↔docs), enlazadas con el selector ES/EN y con `hreflang`. Cualquier dato que cambie (versión, tamaño, huella, permisos…) se cambia en los dos idiomas. Formato: «4,8 MB» y «25-11-2026» en español; «4.8 MB» y «2026-11-25» en inglés.
- **La app solo está en español.** En inglés, cada opción se cita con su nombre en español y la traducción entre paréntesis; las notas de versión en inglés son las oficiales de `fastlane/metadata/android/en-US/changelogs/` del repositorio de la app.
- **JavaScript mínimo y opcional.** Solo hay un script en línea (una línea) que cierra el menú móvil al elegir una sección; sin JavaScript todo funciona igual.
- **Cabecera, menú, script y pie son iguales en todas las páginas** (copiados a mano, sin paso de construcción). Si cambias uno, cambia todos; en cada página solo varía qué enlace lleva `aria-current="page"`.
- **Capturas reales y sin editar.** Se generan desde los PNG originales con ImageMagick:
  `magick captura.png -resize 720x -quality 82 -define webp:method=6 nombre-720.webp` (y lo mismo a 540 y 360).
- **Solo datos verificables** (versión, tamaño, huella SHA-256, permisos…), sacados del repositorio de la app y de sus releases.

## Previsualizar

Abre `index.html` en el navegador. Como todas las rutas son relativas, se ve igual que publicado.

## Publicar

La web está publicada en <https://comunicaa2.github.io/ExtMusic-web/> desde la rama `main` con GitHub Pages (*Deploy from a branch → main / root*). Cada push a `main` la actualiza en uno o dos minutos.
Antes de subir, revisa los cambios; después, comprueba la web ya desplegada.

## Al publicar una versión nueva de la app

**La descarga se actualiza sola.** Todos los botones apuntan a `https://github.com/Comunicaa2/ExtMusic/releases/latest/download/ExtMusic.apk`, que GitHub redirige al APK de la última release. Para que funcione, la release debe tener **un único APK llamado exactamente `ExtMusic.apk`**. Si se llama de otra forma, los botones dan error 404.

El resto de la web describe la versión 1.4.2 y lo dice (fecha y número), así que no queda falso. Actualizarlo es opcional, en español y en `en/`:

- la cabecera de todas las páginas (`v1.4.2 · 25-11-2026`), incluida `404.html`;
- en `index.html`: las Tablas 1 y 2, las novedades, `softwareVersion` en el JSON-LD y el pie de la Figura 1;
- en `versiones.html`: la Tabla 1 y una entrada nueva en el historial, con su enlace exacto `releases/download/vX.Y.Z/ExtMusic.apk`;
- el alcance en `privacidad.html` y el subtítulo de `documentacion.html`, si se revisan de nuevo.

La huella se obtiene así:

```sh
gh api repos/Comunicaa2/ExtMusic/releases/latest --jq '.assets[] | .name + " " + .digest'
```

## Licencias

- Fuentes: SIL Open Font License 1.1 (ver `assets/fonts/OFL-*.txt`).
- Las portadas y fotos que aparecen en las capturas pertenecen a sus respectivos autores.
