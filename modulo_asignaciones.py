"""
Módulo para gestión de asignaciones de implementos
"""

from nucleo_sistema import ElementoSistema, RepositorioBase, RegistroActividad, Utilidades
from typing import List, Dict, Optional, Set


class Asignacion(ElementoSistema):
    ESTADOS = ['activo', 'devuelto', 'vencido', 'cancelado']
    
    def __init__(self, identificador: str, codigo_miembro: str, codigo_implemento: str,
                 unidades: int, fecha_salida: str, fecha_retorno: str, estado: str):
        super().__init__(identificador)
        self.codigo_miembro = codigo_miembro
        self.codigo_implemento = codigo_implemento
        self.unidades = unidades
        self.fecha_salida = fecha_salida
        self.fecha_retorno = fecha_retorno
        self.estado = estado
    
    def a_diccionario(self) -> Dict:
        return {
            "id": self.identificador,
            "codigo_miembro": self.codigo_miembro,
            "codigo_implemento": self.codigo_implemento,
            "unidades": self.unidades,
            "fecha_salida": self.fecha_salida,
            "fecha_retorno": self.fecha_retorno,
            "estado": self.estado
        }
    
    @classmethod
    def desde_diccionario(cls, datos: Dict):
        return cls(
            identificador=datos["id"],
            codigo_miembro=datos["codigo_miembro"],
            codigo_implemento=datos["codigo_implemento"],
            unidades=int(datos["unidades"]),
            fecha_salida=datos["fecha_salida"],
            fecha_retorno=datos["fecha_retorno"],
            estado=datos["estado"]
        )
    
    def esta_vencido(self) -> bool:
        if self.estado != "activo":
            return False
        hoy = Utilidades.obtener_fecha_actual()
        return Utilidades.comparar_fechas(hoy, self.fecha_retorno) > 0


class GestorAsignaciones:
    def __init__(self, archivo: str = "asignaciones.txt"):
        self.repositorio = RepositorioBase(archivo)
        self.lista: List[Asignacion] = []
        self.ids_usados: Set[str] = set()
        self._cargar()
    
    def _cargar(self):
        self.repositorio.asegurar_archivo_existe()
        try:
            with open(self.repositorio.ruta_txt, "r", encoding="utf-8") as f:
                for linea in f:
                    partes = linea.strip().split(",")
                    if len(partes) == 7:
                        try:
                            asig = Asignacion(
                                partes[0], partes[1], partes[2],
                                int(partes[3]), partes[4], partes[5], partes[6]
                            )
                            self.lista.append(asig)
                            self.ids_usados.add(partes[0])
                        except:
                            continue
        except FileNotFoundError:
            print("→ Archivo de asignaciones no encontrado. Se creará al guardar.")
    
    def crear(self, asignacion: Asignacion) -> bool:
        if asignacion.identificador in self.ids_usados:
            return False
        self.lista.append(asignacion)
        self.ids_usados.add(asignacion.identificador)
        RegistroActividad.registrar_accion(f"Asignación creada: {asignacion.identificador}")
        return True
    
    def buscar(self, identificador: str) -> Optional[Asignacion]:
        for a in self.lista:
            if a.identificador == identificador:
                return a
        return None
    
    def obtener_todas(self) -> List[Asignacion]:
        return self.lista.copy()
    
    def obtener_activas(self) -> List[Asignacion]:
        return [a for a in self.lista if a.estado == "activo"]
    
    def obtener_vencidas(self) -> List[Asignacion]:
        return [a for a in self.lista if a.esta_vencido()]
    
    def obtener_por_miembro(self, codigo_miembro: str) -> List[Asignacion]:
        return [a for a in self.lista if a.codigo_miembro == codigo_miembro]
    
    def persistir(self):
        datos = [a.a_diccionario() for a in self.lista]
        campos = ["id", "codigo_miembro", "codigo_implemento", "unidades", 
                  "fecha_salida", "fecha_retorno", "estado"]
        return self.repositorio.persistir_multiformato(datos, campos)