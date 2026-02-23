import json
from datetime import datetime


def cargar_datos(archivo):
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def obtener_nombre_usuario(id_usuario, usuarios):
    for u in usuarios:
        if u["id"] == id_usuario:
            return u["nombres"] + " " + u["apellidos"]
    return "Desconocido"


def obtener_nombre_herramienta(id_herramienta, herramientas):
    for h in herramientas:
        if h["id"] == id_herramienta:
            return h["titulo"]
    return "Desconocida"


def generar_reporte():

    prestamos = cargar_datos("asignaciones.json")
    usuarios = cargar_datos("miembros.json")
    herramientas = cargar_datos("inventario.json")

    hoy = datetime.now().date()

    vencidos = []
    total_herramientas = 0

    for p in prestamos:

        if p["estado"] == "activo":

            fecha_estimada = datetime.strptime(
                p["fecha_retorno"], "%Y-%m-%d"
            ).date()

            if fecha_estimada < hoy:

                dias_atraso = (hoy - fecha_estimada).days

                nombre_usuario = obtener_nombre_usuario(
                    p["codigo_miembro"], usuarios
                )

                nombre_herramienta = obtener_nombre_herramienta(
                    p["codigo_implemento"], herramientas
                )

                vencidos.append({
                    "id": p["id"],
                    "usuario": nombre_usuario,
                    "herramienta": nombre_herramienta,
                    "cantidad": p["unidades"],
                    "fecha_inicio": p["fecha_salida"],
                    "fecha_estimada": p["fecha_retorno"],
                    "dias_atraso": dias_atraso
                })

                total_herramientas += p["unidades"]

    # ✅ VALIDAR SI NO HAY VENCIDOS
    if not vencidos:
        print("No existen préstamos vencidos.")
        return

    # ✅ GENERAR ARCHIVO MARKDOWN
    with open("prestamos_vencidos.md", "w", encoding="utf-8") as f:

        f.write("# Préstamos Vencidos - Junta Comunal\n\n")

        f.write("| id_prestamo | usuario | herramienta | cantidad | fecha_inicio | fecha_estimada | dias_atraso |\n")
        f.write("|-------------|---------|-------------|----------|--------------|----------------|-------------|\n")

        for v in vencidos:
            f.write(f"| {v['id']} | {v['usuario']} | {v['herramienta']} | {v['cantidad']} | {v['fecha_inicio']} | {v['fecha_estimada']} | {v['dias_atraso']} |\n")

        f.write("\n")
        f.write(f"**Total de préstamos vencidos:** {len(vencidos)}\n\n")
        f.write(f"**Total de herramientas comprometidas:** {total_herramientas}\n")

    print("✅ Archivo prestamos_vencidos.md generado correctamente.")


# Permite ejecutar el módulo directamente
if __name__ == "__main__":
    generar_reporte()