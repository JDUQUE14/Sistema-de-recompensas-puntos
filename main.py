import sqlite3
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()


# Crear tablas de forma simple al iniciar
def crear_tablas():
  conexion = sqlite3.connect("database.db")
  cursor = conexion.cursor()
  cursor.execute(
      "CREATE TABLE IF NOT EXISTS clientes (cedula TEXT PRIMARY KEY, nombre"
      " TEXT, puntos INTEGER)"
  )
  conexion.commit()
  conexion.close()


crear_tablas()


#Registrar Cliente
@app.post("/api/registrar_cliente")
def registrar_cliente(datos: dict):
  cedula = datos["cedula"]
  nombre = datos["nombre"]

  conexion = sqlite3.connect("database.db")
  cursor = conexion.cursor()
  try:
    cursor.execute(
        "INSERT INTO clientes VALUES (?, ?, 0)", (cedula, nombre)
    )
    conexion.commit()
    conexion.close()
    return {"status": "ok", "mensaje": "Cliente guardado"}
  except:
    conexion.close()
    return {"status": "error", "mensaje": "La cedula ya existe"}


#Consultar Saldo
@app.get("/api/consultar/{cedula}")
def consultar(cedula: str):
  conexion = sqlite3.connect("database.db")
  cursor = conexion.cursor()
  cursor.execute(
      "SELECT nombre, puntos FROM clientes WHERE cedula = ?", (cedula,)
  )
  cliente = cursor.fetchone()
  conexion.close()

  if cliente:
    puntos = cliente[1]
    pesos = puntos * 100  # 1 punto = $100
    return {
        "encontrado": True,
        "nombre": cliente[0],
        "puntos": puntos,
        "pesos": pesos,
    }
  else:
    return {"encontrado": False, "mensaje": "Cliente no encontrado"}


#Registrar Compra (1000 pesos = 1 punto)
@app.post("/api/compra")
def compra(datos: dict):
  cedula = datos["cedula"]
  monto = int(datos["monto"])

  puntos_nuevos = monto // 1000

  conexion = sqlite3.connect("database.db")
  cursor = conexion.cursor()
  cursor.execute("SELECT puntos FROM clientes WHERE cedula = ?", (cedula,))
  cliente = cursor.fetchone()

  if not cliente:
    conexion.close()
    return {"status": "error", "mensaje": "El cliente no existe"}

  puntos_actuales = cliente[0] + puntos_nuevos
  cursor.execute(
      "UPDATE clientes SET puntos = ? WHERE cedula = ?",
      (puntos_actuales, cedula),
  )
  conexion.commit()
  conexion.close()

  return {
      "status": "ok",
      "puntos_ganados": puntos_nuevos,
      "total_puntos": puntos_actuales,
  }


#Redimir Puntos
@app.post("/api/redimir")
def redimir(datos: dict):
  cedula = datos["cedula"]
  puntos_a_redimir = int(datos["puntos"])

  conexion = sqlite3.connect("database.db")
  cursor = conexion.cursor()
  cursor.execute("SELECT puntos FROM clientes WHERE cedula = ?", (cedula,))
  cliente = cursor.fetchone()

  if not cliente:
    conexion.close()
    return {"status": "error", "mensaje": "El cliente no existe"}

  puntos_actuales = cliente[0]

  # Error si no tiene puntos suficientes
  if puntos_actuales < puntos_a_redimir:
    conexion.close()
    return {
        "status": "error",
        "mensaje": (
            f"No tiene puntos suficientes. Solo tiene {puntos_actuales} puntos."
        ),
    }

  nuevos_puntos = puntos_actuales - puntos_a_redimir
  cursor.execute(
      "UPDATE clientes SET puntos = ? WHERE cedula = ?",
      (nuevos_puntos, cedula),
  )
  conexion.commit()
  conexion.close()

  return {
      "status": "ok",
      "mensaje": f"Redimio {puntos_a_redimir} puntos con exito",
      "saldo": nuevos_puntos,
  }


# Servir HTML estatico
app.mount("/", StaticFiles(directory="static", html=True), name="static")