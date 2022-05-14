"""Gabriela Beatriz Solorzano Nuila"""

from flask import (
    Flask,
    render_template,
    request,
    Response,
)
import firebase_admin
from firebase_admin import credentials, firestore
import datetime


app = Flask(__name__)

app.config["SECRET_KEY"] = "123456"

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
users_ref = db.collection("orders")


# CREATE
def create_orden(ref, cliente, cantidad):
    new_orden = {
        "cliente": cliente,
        "cantidad": cantidad,
        "check": False,
        "fecha": datetime.datetime.now(),
    }
    ref.document().set(new_orden)


# READ
def read_ordenes(ref):
    docs = ref.get()
    orders = []
    for doc in docs:
        order = doc.to_dict()
        order["id"] = doc.id
        orders.append(order)
    return orders


def ordenes_completadas(ref):
    docs = ref.get()
    completadas = []
    for doc in docs:
        completada = doc.to_dict()
        if completada["check"] == True:
            completadas.append(completada)
    return completadas


def repetidos(x):
    return list(dict.fromkeys(x))


def clientes(ref):
    docs = ref.get()
    clientes = []
    for doc in docs:
        cliente = doc.to_dict()
        clientes.append(cliente["cliente"])
    return clientes


# UPDATE
def update_orden(ref, id):
    orden_ref = ref.document(id).get()
    check = orden_ref.to_dict()["check"]
    print(check)
    if check:
        ref.document(id).update({"check": False})
    else:
        ref.document(id).update({"check": True})


def update_orden_name(ref, id, cantidad):
    ref.document(id).update({"cantidad": cantidad})


# DELETE
def delete_orden(ref, id):
    ref.document(id).delete()


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        ordenes = read_ordenes(users_ref)
        completadas = len(ordenes_completadas(users_ref))
        clients = repetidos(clientes(users_ref))
        response = {
            "ordenes": ordenes,
            "pendientes": len(ordenes) - completadas,
            "completadas": completadas,
            "clientes": len(clients),
        }
        return render_template("index.html", response=response)
    elif request.method == "POST":
        new_orden = request.form["Orden"]
        cant = request.form["Cantidad"]
        create_orden(users_ref, new_orden, int(cant))
        return Response(status=200)


@app.route("/update-check", methods=["POST"])
def check_orden():
    id = request.form["id"]
    try:
        update_orden(users_ref, id)
        return Response(status=200)
    except:
        return Response(status=400)


@app.route("/update-order-cantidad", methods=["POST"])
def update_orden_cantidad():
    id = request.form["id"]
    cantidad = request.form["cantidadModificada"]
    try:
        update_orden_name(users_ref, id, int(cantidad))
        return Response(status=200)
    except:
        return Response(status=400)


@app.route("/delete", methods=["POST"])
def delete():
    id = request.form["id"]
    try:
        delete_orden(users_ref, id)
        return Response(status=200)
    except:
        return Response(status=400)


# Main
if __name__ == "__main__":
    app.run(debug=True)
