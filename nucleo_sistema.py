"""
Módulo principal del sistema - Contiene las clases base
Autor: Sistema refactorizado
"""

from datetime import datetime
import json
import csv
from pathlib import Path
from typing import List, Dict, Optional, Set


class Utilidades:
    """Clase con métodos auxiliares para operaciones comunes"""
    
    @staticmethod
    def validar_fecha(texto_fecha: str) -> bool:
        """Verifica si una fecha tiene el formato correcto"""
        try:
            datetime.strptime(texto_fecha, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    @staticmethod
    def obtener_fecha_actual() -> str:
        """Retorna la fecha actual en formato YYYY-MM-DD"""
        return datetime.now().strftime("%Y-%m-%d")
    
    @staticmethod
    def comparar_fechas(fecha1: str, fecha2: str) -> int:
        """Compara dos fechas. Retorna: -1 si fecha1 < fecha2, 0 si iguales, 1 si fecha1 > fecha2"""
        f1 = datetime.strptime(fecha1, "%Y-%m-%d").date()
        f2 = datetime.strptime(fecha2, "%Y-%m-%d").date()
        
        if f1 < f2:
            return -1
        elif f1 > f2:
            return 1
        return 0


class RepositorioBase:
    """Clase base para manejar persistencia de datos"""
    
    def __init__(self, nombre_archivo: str):
        self.ruta_txt = Path(nombre_archivo)
        self.ruta_json = self.ruta_txt.with_suffix('.json')
        self.ruta_csv = self.ruta_txt.with_suffix('.csv')
    
    def asegurar_archivo_existe(self):
        """Crea el archivo si no existe"""
        if not self.ruta_txt.exists():
            self.ruta_txt.touch()
    
    def persistir_multiformato(self, datos: List[Dict], campos: List[str]):
        """Guarda datos en formatos TXT, JSON y CSV"""
        resultado = {'txt': False, 'json': False, 'csv': False}
        
        # Guardar TXT
        try:
            with open(self.ruta_txt, 'w', encoding='utf-8') as f:
                for registro in datos:
                    linea = ','.join(str(registro.get(c, '')) for c in campos)
                    f.write(f"{linea}\n")
            resultado['txt'] = True
        except Exception as e:
            print(f"[ERROR TXT] {e}")
        
        # Guardar JSON
        try:
            with open(self.ruta_json, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            resultado['json'] = True
        except Exception as e:
            print(f"[ERROR JSON] {e}")
        
        # Guardar CSV
        try:
            with open(self.ruta_csv, 'w', newline='', encoding='utf-8') as f:
                if datos:
                    escritor = csv.DictWriter(f, fieldnames=campos)
                    escritor.writeheader()
                    escritor.writerows(datos)
            resultado['csv'] = True
        except Exception as e:
            print(f"[ERROR CSV] {e}")
        
        return resultado


class ElementoSistema:
    """Clase base para elementos del sistema"""
    
    def __init__(self, identificador: str):
        self.identificador = identificador
    
    def a_diccionario(self) -> Dict:
        """Convierte el objeto a diccionario"""
        raise NotImplementedError("Método debe ser implementado por subclases")
    
    @classmethod
    def desde_diccionario(cls, datos: Dict):
        """Crea una instancia desde un diccionario"""
        raise NotImplementedError("Método debe ser implementado por subclases")


class RegistroActividad:
    """Maneja el registro de eventos del sistema"""
    
    RUTA_LOG_TXT = Path("eventos_sistema.txt")
    RUTA_LOG_JSON = Path("eventos_sistema.json")
    RUTA_LOG_CSV = Path("eventos_sistema.csv")
    
    @classmethod
    def escribir_entrada(cls, tipo: str, descripcion: str):
        """Escribe una entrada en el log en múltiples formatos"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entrada = f"[{timestamp}] [{tipo.upper()}] {descripcion}\n"
        
        # Guardar en TXT
        try:
            with open(cls.RUTA_LOG_TXT, 'a', encoding='utf-8') as f:
                f.write(entrada)
        except Exception:
            pass
        
        # Guardar en JSON
        try:
            registros = []
            if cls.RUTA_LOG_JSON.exists():
                with open(cls.RUTA_LOG_JSON, 'r', encoding='utf-8') as f:
                    registros = json.load(f)
            
            registros.append({
                'timestamp': timestamp,
                'tipo': tipo.upper(),
                'descripcion': descripcion
            })
            
            with open(cls.RUTA_LOG_JSON, 'w', encoding='utf-8') as f:
                json.dump(registros, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
        
        # Guardar en CSV
        try:
            archivo_existe = cls.RUTA_LOG_CSV.exists()
            with open(cls.RUTA_LOG_CSV, 'a', newline='', encoding='utf-8') as f:
                escritor = csv.writer(f)
                if not archivo_existe:
                    escritor.writerow(['timestamp', 'tipo', 'descripcion'])
                escritor.writerow([timestamp, tipo.upper(), descripcion])
        except Exception:
            pass
    
    @classmethod
    def registrar_accion(cls, mensaje: str):
        """Registra una acción exitosa"""
        cls.escribir_entrada("ACCION", mensaje)
    
    @classmethod
    def registrar_fallo(cls, mensaje: str):
        """Registra un error o fallo"""
        cls.escribir_entrada("ERROR", mensaje)
    
    @classmethod
    def registrar_advertencia(cls, mensaje: str):
        """Registra una advertencia"""
        cls.escribir_entrada("ADVERTENCIA", mensaje)