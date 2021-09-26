import re

import requests
from bs4 import BeautifulSoup
from flask import Flask, request

HOST = "https://www.cuitonline.com"


class CuitOnlineNotFound(Exception):
    pass


def search(cuit):
    s = requests.Session()

    response = s.get(f"{HOST}/detalle/{cuit}/")
    print(f"[{response.status_code}] {response.request.url}")

    if not response.ok:
        raise CuitOnlineNotFound

    soup = BeautifulSoup(response.text, "html.parser")

    titular = soup.select_one("[itemprop='name']")
    persona = soup.select_one("[itemprop='jobTitle']").attrs.get("content")
    direccion = soup.select_one("[itemprop='streetAddress']")
    provincia = soup.select_one("[itemprop='addressRegion']")
    localidad = soup.select_one("[itemprop='addressLocality']")
    actividades = []

    for elem in soup.select(".activity-order"):
        match = re.search(r"]\s(?P<codigo>\d+)\s-\s(?P<descripcion>.+)", elem.parent.text)
        if not match:
            continue
        actividades.append(match.groupdict())

    return {
        "persona": persona,
        "titular": titular and titular.text,
        "direccion": direccion and direccion.text,
        "provincia": provincia and provincia.text,
        "localidad": localidad and localidad.text,
        "actividades": actividades
    }


app = Flask(__name__)


@app.route("/api/cuit")
def cuit():
    q = request.args.get("q", "")

    if len(q) != 11:
        return {"error": "CUIT inválido"}, 400

    try:
        data = search(q)
    except CuitOnlineNotFound:
        return {"error": "CUIT no encontrado"}, 404

    return data
