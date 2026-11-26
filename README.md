# ExtMusic · web

Sitio web de [ExtMusic](https://github.com/Comunicaa2/ExtMusic), un reproductor de música libre para Android.
Es un sitio estático para GitHub Pages: HTML y CSS escritos a mano, sin dependencias y sin paso de construcción.

> Estado: **publicado** en <https://comunicaa2.github.io/ExtMusic-web/>.

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
herramientas/actualizar_version.py   Regenera los datos de versión desde la última release (ver abajo)
.github/workflows/actualizar-version.yml   Lo ejecuta automáticamente al publicarse una release
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

## Al publicar una versión nueva de la app (automático)

**No hay que hacer nada a mano.** Al publicar una release en `Comunicaa2/ExtMusic`:

1. El workflow `avisar-web.yml` del repo de la app avisa a este repo (`repository_dispatch` «nueva-version») con el secreto `WEB_DISPATCH_TOKEN`.
2. El workflow `actualizar-version.yml` de este repo ejecuta `herramientas/actualizar_version.py`. Si hay cambios, hace un commit como `github-actions[bot]` y GitHub Pages publica la web en uno o dos minutos.

**Regla:** la release debe tener **un único APK llamado exactamente `ExtMusic.apk`**. Si no, el workflow falla sin tocar la web y GitHub avisa por correo. Si el APK aún se está subiendo, el workflow reintenta durante 3 minutos.

**Qué se regenera.** Solo lo que está entre `<!-- auto:nombre -->` y `<!-- /auto:nombre -->`, en español y en `en/`:

- la cabecera de todas las páginas, incluida la 404;
- en Versiones, la Tabla 1 y una entrada nueva en el historial;
- en la portada, las novedades y las filas de versión, tamaño y SHA-256 de la Tabla 2;
- `softwareVersion` y `fileSize` del JSON-LD, y los `lastmod` del sitemap.

**De dónde salen los datos:**

- Notas en español: el texto de la release.
- Notas en inglés: `fastlane/metadata/android/en-US/changelogs/<versionCode>.txt` de esa etiqueta. Si no existe, se muestran las de español con el aviso «Release notes available in Spanish only».

**Qué NO se regenera.** La tabla de Funciones, la Documentación, la revisión de Privacidad, las capturas y el pie de la Figura 1 siguen diciendo «revisado en la versión 1.4.2». Se escribieron comprobando la app y hay que revisarlos a mano cuando una versión cambie algo de eso.

**Ejecutarlo a mano:**

- desde GitHub: pestaña *Actions* → «Actualizar versión» → *Run workflow*;
- en local: `python3 herramientas/actualizar_version.py`.

Para probar sin red: `--release-json release.json --changelog-en notas.txt --raiz copia/`.

**Si el aviso deja de funcionar** (por ejemplo, porque caducó el token): crea otro token *fine-grained* con acceso solo a `ExtMusic-web` y permiso *Contents: Read and write*, y guárdalo con `gh secret set WEB_DISPATCH_TOKEN -R Comunicaa2/ExtMusic`. Mientras tanto, la web se puede actualizar a mano con *Run workflow*.

## Licencias

- Fuentes: SIL Open Font License 1.1 (ver `assets/fonts/OFL-*.txt`).
- Las portadas y fotos que aparecen en las capturas pertenecen a sus respectivos autores.
