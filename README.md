# ExtMusic · web

Sitio web de [ExtMusic](https://github.com/Comunicaa2/ExtMusic), un reproductor de música libre para Android.
Es un sitio estático para GitHub Pages: HTML y CSS escritos a mano, sin dependencias y sin paso de construcción.

> Estado: **prototipo de la página principal** (Fase 4). Todavía no está publicado.

## Estructura

```
index.html                  Página principal (español)
.nojekyll                   GitHub Pages sirve los archivos tal cual, sin Jekyll
assets/css/extmusic.css     Sistema de diseño «Datasheet»: tokens + componentes, claro y oscuro automático
assets/fonts/               Hanken Grotesk y JetBrains Mono (SIL OFL 1.1, subconjunto latino) + licencias
assets/img/icono.svg        Icono de la app; icono-32/192/512.png y apple-touch-icon.png derivados de él
assets/img/capturas/        Capturas reales de la app en WebP (360, 540 y 720 px de ancho)
```

## Reglas

- **Rutas siempre relativas** (`assets/...`). El sitio se publica en `https://comunicaa2.github.io/ExtMusic-web/`, no en la raíz de un dominio.
- **Sin recursos externos.** Las fuentes y las imágenes se sirven desde el propio sitio, y no hay analíticas ni scripts de terceros.
- **Capturas reales y sin editar.** Se generan desde los PNG originales con ImageMagick:
  `magick captura.png -resize 720x -quality 82 -define webp:method=6 nombre-720.webp` (y lo mismo a 540 y 360).
- **Solo datos verificables** (versión, tamaño, huella SHA-256, permisos…), sacados del repositorio de la app y de sus releases.

## Previsualizar

Abre `index.html` en el navegador. Como todas las rutas son relativas, se ve igual que publicado.

## Publicar (pendiente de aprobación)

Se publicará desde la rama `main` con GitHub Pages (*Settings → Pages → Deploy from a branch → main / root*).
Antes de publicar hay que revisar los cambios y comprobar la web ya desplegada.

## Al publicar una versión nueva de la app

Actualiza en `index.html` la versión, la fecha, el tamaño del APK, la huella SHA-256, las URL de descarga y la lista de novedades.
La huella se obtiene así:

```sh
gh api repos/Comunicaa2/ExtMusic/releases/latest --jq '.assets[] | .name + " " + .digest'
```

## Licencias

- Fuentes: SIL Open Font License 1.1 (ver `assets/fonts/OFL-*.txt`).
- Las portadas y fotos que aparecen en las capturas pertenecen a sus respectivos autores.
