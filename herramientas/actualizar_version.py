#!/usr/bin/env python3
"""Actualiza la web con los datos de la última release de ExtMusic.

Lee la última release de GitHub (Comunicaa2/ExtMusic) y reescribe solo las
zonas marcadas con <!-- auto:nombre -->…<!-- /auto:nombre --> en las páginas:
cabecera, Tabla 1 y historial de Versiones, novedades y Tabla 2 de la portada,
más softwareVersion/fileSize del JSON-LD y los lastmod del sitemap.

Notas en español: el texto de la release. Notas en inglés: el changelog oficial
fastlane/metadata/android/en-US/changelogs/<versionCode>.txt de esa etiqueta.

La release debe tener un único APK llamado exactamente ExtMusic.apk, con su
digest sha256; si no, el script termina con error y no escribe nada.

Uso:
  python3 herramientas/actualizar_version.py
  python3 herramientas/actualizar_version.py --release-json r.json [--changelog-en en.txt]   (pruebas sin red)

Solo biblioteca estándar.
"""
import argparse
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_APP = "Comunicaa2/ExtMusic"
API = "https://api.github.com"
GH = f"https://github.com/{REPO_APP}"
APK = "ExtMusic.apk"
RAIZ = Path(__file__).resolve().parent.parent


class ErrorRelease(Exception):
    pass


# ---------------------------------------------------------------- red

def _peticion(url, crudo=False):
    cab = {"Accept": "application/vnd.github.raw" if crudo else "application/vnd.github+json",
           "User-Agent": "extmusic-web-actualizador"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        cab["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=cab), timeout=30) as r:
        datos = r.read().decode("utf-8")
    return datos if crudo else json.loads(datos)


def _contenido(ruta, ref):
    try:
        return _peticion(f"{API}/repos/{REPO_APP}/contents/{ruta}?ref={ref}", crudo=True)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


# ---------------------------------------------------------------- datos

def validar(release):
    tag = release.get("tag_name", "")
    m = re.fullmatch(r"v(\d+\.\d+\.\d+)", tag)
    if not m:
        raise ErrorRelease(f"etiqueta no válida: {tag!r} (se espera vX.Y.Z)")
    apks = [a for a in release.get("assets", []) if a.get("name", "").lower().endswith(".apk")]
    if len(apks) != 1:
        raise ErrorRelease(f"la release {tag} tiene {len(apks)} APK; debe tener exactamente uno")
    a = apks[0]
    if a["name"] != APK:
        raise ErrorRelease(f"el APK de {tag} se llama {a['name']!r}; debe llamarse {APK!r}")
    digest = a.get("digest") or ""
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        raise ErrorRelease(f"el APK de {tag} no tiene digest sha256")
    fecha = release.get("published_at") or ""
    if not re.match(r"\d{4}-\d{2}-\d{2}", fecha):
        raise ErrorRelease(f"la release {tag} no tiene fecha de publicación")
    return {
        "version": m.group(1),
        "tag": tag,
        "fecha": fecha[:10],  # AAAA-MM-DD (UTC)
        "bytes": int(a["size"]),
        "sha": digest.split(":", 1)[1],
        "notas_es": notas(release.get("body") or ""),
    }


def notas(texto):
    """Lista de notas a partir de viñetas «• », «- » o «* » (o una por línea)."""
    lineas = [l.strip() for l in texto.replace("\r", "").split("\n") if l.strip()]
    return [re.sub(r"^[•\-*]\s+", "", l) for l in lineas]


def version_code(tag):
    gradle = _contenido("app/build.gradle.kts", tag)
    m = re.search(r"versionCode\s*=\s*(\d+)", gradle or "")
    return m.group(1) if m else None


# ---------------------------------------------------------------- formato

def fecha_es(iso):
    a, m, d = iso.split("-")
    return f"{d}-{m}-{a}"


def mb(n, coma):
    s = f"{n / 1_000_000:.1f}"
    return s.replace(".", ",") if coma else s


def miles(n, sep):
    return f"{n:,}".replace(",", sep)


def esc(t):
    return html.escape(t, quote=False)


def li_portada_es(nota):
    """Portada en español: prefijo en negrita y punto final (estilo de la web)."""
    m = re.match(r"^([A-ZÁÉÍÓÚÑ][\wáéíóúñ]*):\s+(.*)$", nota)
    cuerpo = f"<strong>{esc(m.group(1))}:</strong> {esc(m.group(2))}" if m else esc(nota)
    if not re.search(r"[.!?…]$", nota):
        cuerpo += "."
    return cuerpo


def ul(items, sangria, formato=esc, lang=""):
    ind = " " * sangria
    filas = "".join(f"{ind}  <li>{formato(i)}</li>\n" for i in items)
    attr = f' lang="{lang}"' if lang else ""
    return f"{ind}<ul class=\"novedades\"{attr}>\n{filas}{ind}</ul>"


# ---------------------------------------------------------------- bloques

def bloques(d, notas_en, en_solo_es):
    v, fe, fi = d["version"], fecha_es(d["fecha"]), d["fecha"]
    url_v = f"{GH}/releases/download/{d['tag']}/{APK}"
    url_tag = f"{GH}/releases/tag/{d['tag']}"
    aviso_en = '\n    <p class="texto-nota">Release notes available in Spanish only.</p>' if en_solo_es else ""
    aviso_en_h = '\n      <p class="texto-nota">Release notes available in Spanish only.</p>' if en_solo_es else ""
    lang_en = "es" if en_solo_es else ""
    b = {}
    b["es", "rev"] = f"v{v} · {fe}"
    b["en", "rev"] = f"v{v} · {fi}"
    b["es", "rev-corta"] = f"v{v}"
    b["es", "actual"] = f"""
        <caption>Tabla 1. ExtMusic {v}</caption>
        <thead><tr><th scope="col">Parámetro</th><th scope="col">Valor</th></tr></thead>
        <tbody>
          <tr><th scope="row">Versión</th><td>{v}</td></tr>
          <tr><th scope="row">Publicada</th><td>{fe}</td></tr>
          <tr><th scope="row">Archivo</th><td><code>{APK}</code></td></tr>
          <tr><th scope="row">Tamaño</th><td>{mb(d['bytes'], True)} MB <span class="nota">({miles(d['bytes'], '.')} bytes)</span></td></tr>
          <tr><th scope="row">Requisitos</th><td>Android 8.0 (API 26) o superior</td></tr>
          <tr><th scope="row">SHA-256</th><td><span class="hash">{d['sha']}</span></td></tr>
          <tr><th scope="row">Enlaces</th><td><a href="{url_v}">Descargar el APK de la {v}</a> · <a href="{url_tag}">Página de la versión en GitHub</a></td></tr>
        </tbody>
        """
    b["en", "actual"] = f"""
        <caption>Table 1. ExtMusic {v}</caption>
        <thead><tr><th scope="col">Parameter</th><th scope="col">Value</th></tr></thead>
        <tbody>
          <tr><th scope="row">Version</th><td>{v}</td></tr>
          <tr><th scope="row">Released</th><td>{fi}</td></tr>
          <tr><th scope="row">File</th><td><code>{APK}</code></td></tr>
          <tr><th scope="row">Size</th><td>{mb(d['bytes'], False)} MB <span class="nota">({miles(d['bytes'], ',')} bytes)</span></td></tr>
          <tr><th scope="row">Requirements</th><td>Android 8.0 (API 26) or later</td></tr>
          <tr><th scope="row">SHA-256</th><td><span class="hash">{d['sha']}</span></td></tr>
          <tr><th scope="row">Links</th><td><a href="{url_v}">Download the {v} APK</a> · <a href="{url_tag}">Release page on GitHub</a></td></tr>
        </tbody>
        """
    b["es", "novedades"] = f"""
    <h2 class="titulo-sec" id="t-novedades"><span class="titulo-sec__num">3</span>Novedades de la versión {v}</h2>
    <p class="etiqueta etiqueta--suave">Publicada el {fe} · notas oficiales de la versión</p>
{ul(d['notas_es'], 4, li_portada_es)}
    """
    b["en", "novedades"] = f"""
    <h2 class="titulo-sec" id="t-whats-new"><span class="titulo-sec__num">3</span>What's new in version {v}</h2>
    <p class="etiqueta etiqueta--suave">Released {fi} · official release notes</p>{aviso_en}
{ul(notas_en, 4, lang=lang_en)}
    """
    b["es", "t2-version"] = f'<tr><th scope="row">Versión</th><td>{v}</td><td class="nota">{fe}</td></tr>'
    b["en", "t2-version"] = f'<tr><th scope="row">Version</th><td>{v}</td><td class="nota">{fi}</td></tr>'
    b["es", "t2-tamano"] = f'<tr><th scope="row">Tamaño del APK</th><td>{mb(d["bytes"], True)} MB</td><td class="nota">{APK}</td></tr>'
    b["en", "t2-tamano"] = f'<tr><th scope="row">APK size</th><td>{mb(d["bytes"], False)} MB</td><td class="nota">{APK}</td></tr>'
    sha_fila = f'<tr><th scope="row">SHA-256</th><td colspan="2"><span class="hash">{d["sha"]}</span></td></tr>'
    b["es", "t2-sha"] = b["en", "t2-sha"] = sha_fila
    idv, idt = "v" + v.replace(".", "-"), "t-" + v.replace(".", "")
    hechos = lambda sep: (f'      <p class="hechos"><a href="{url_v}">{APK}</a> · {miles(d["bytes"], sep)} bytes · '
                          f'SHA-256 <span class="hash">{d["sha"]}</span></p>')
    b["es", "articulo"] = (f'    <article class="version" id="{idv}" aria-labelledby="{idt}">\n'
                           f'      <h3 id="{idt}">{v} · {fe}</h3>\n{ul(d["notas_es"], 6)}\n{hechos(".")}\n    </article>')
    b["en", "articulo"] = (f'    <article class="version" id="{idv}" aria-labelledby="{idt}">\n'
                           f'      <h3 id="{idt}">{v} · {fi}</h3>{aviso_en_h}\n{ul(notas_en, 6, lang=lang_en)}\n{hechos(",")}\n    </article>')
    b["id"] = idv
    return b


# ---------------------------------------------------------------- escritura

def reemplazar(texto, nombre, nuevo, archivo):
    patron = re.compile(rf"(<!-- auto:{re.escape(nombre)} -->)(.*?)(<!-- /auto:{re.escape(nombre)} -->)", re.S)
    if len(patron.findall(texto)) != 1:
        raise ErrorRelease(f"{archivo}: falta el marcador auto:{nombre} (o está repetido)")
    return patron.sub(lambda m: m.group(1) + nuevo + m.group(3), texto)


def json_ld(texto, v, bytes_, archivo):
    for campo, valor in (("softwareVersion", v), ("fileSize", f"{mb(bytes_, False)}MB")):
        texto, n = re.subn(rf'("{campo}": ")[^"]*(")', lambda m: m.group(1) + valor + m.group(2), texto)
        if n != 1:
            raise ErrorRelease(f"{archivo}: no encuentro {campo} en el JSON-LD")
    return texto


def historial(texto, b, idioma, archivo):
    marca = "    <!-- auto:historial -->\n"
    if texto.count(marca) != 1:
        raise ErrorRelease(f"{archivo}: falta el marcador auto:historial")
    if f'id="{b["id"]}"' in texto:
        return texto  # ya está en el historial
    sep = "\n\n" if idioma == "es" else "\n"
    return texto.replace(marca, marca + b[idioma, "articulo"] + sep)


PAGINAS = {
    "es": ["index.html", "versiones.html", "privacidad.html", "documentacion.html"],
    "en": ["en/index.html", "en/versions.html", "en/privacy.html", "en/docs.html"],
}


def generar(raiz, d, notas_en, en_solo_es):
    b = bloques(d, notas_en, en_solo_es)
    salida = {}
    for idioma, paginas in PAGINAS.items():
        for p in paginas:
            t = (raiz / p).read_text(encoding="utf-8")
            t = reemplazar(t, "rev", b[idioma, "rev"], p)
            if p.endswith(("index.html",)):
                t = reemplazar(t, "novedades", b[idioma, "novedades"], p)
                for fila in ("t2-version", "t2-tamano", "t2-sha"):
                    t = reemplazar(t, fila, b[idioma, fila], p)
                t = json_ld(t, d["version"], d["bytes"], p)
            if p.endswith(("versiones.html", "versions.html")):
                t = reemplazar(t, "actual", b[idioma, "actual"], p)
                t = historial(t, b, idioma, p)
            salida[p] = t
    t = (raiz / "404.html").read_text(encoding="utf-8")
    salida["404.html"] = reemplazar(t, "rev-corta", b["es", "rev-corta"], "404.html")
    t = (raiz / "sitemap.xml").read_text(encoding="utf-8")
    salida["sitemap.xml"] = re.sub(r"<lastmod>[^<]*</lastmod>", f"<lastmod>{d['fecha']}</lastmod>", t)
    return salida


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--raiz", type=Path, default=RAIZ, help="carpeta de la web (por defecto, la del repo)")
    ap.add_argument("--release-json", type=Path, help="release de prueba (JSON como el de la API), sin red")
    ap.add_argument("--changelog-en", type=Path, help="changelog en inglés de prueba, sin red")
    ap.add_argument("--reintentos", type=int, default=0, help="reintentos si la release aún no tiene el APK")
    ap.add_argument("--espera", type=int, default=30, help="segundos entre reintentos")
    args = ap.parse_args()

    intento = 0
    while True:
        try:
            release = (json.loads(args.release_json.read_text(encoding="utf-8")) if args.release_json
                       else _peticion(f"{API}/repos/{REPO_APP}/releases/latest"))
            d = validar(release)
            break
        except ErrorRelease as e:
            if intento >= args.reintentos or args.release_json:
                print(f"ERROR: {e}. No se ha cambiado nada.", file=sys.stderr)
                return 1
            intento += 1
            print(f"Aún no válida ({e}); reintento {intento}/{args.reintentos} en {args.espera} s", file=sys.stderr)
            time.sleep(args.espera)

    if args.release_json:
        en = args.changelog_en.read_text(encoding="utf-8") if args.changelog_en else None
    else:
        code = version_code(d["tag"])
        en = _contenido(f"fastlane/metadata/android/en-US/changelogs/{code}.txt", d["tag"]) if code else None
    notas_en = notas(en) if en and en.strip() else d["notas_es"]
    en_solo_es = not (en and en.strip())

    try:
        salida = generar(args.raiz, d, notas_en, en_solo_es)
    except ErrorRelease as e:
        print(f"ERROR: {e}. No se ha cambiado nada.", file=sys.stderr)
        return 1

    cambiados = []
    for p, t in salida.items():
        f = args.raiz / p
        if f.read_text(encoding="utf-8") != t:
            f.write_text(t, encoding="utf-8")
            cambiados.append(p)
    print(f"ExtMusic {d['version']} ({d['fecha']}): " + (", ".join(cambiados) if cambiados else "sin cambios"))
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as o:
            o.write(f"version={d['version']}\ncambios={'si' if cambiados else 'no'}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
