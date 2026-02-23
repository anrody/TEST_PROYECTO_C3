"""
Módulo para gestión de implementos del sistema
"""

from nucleo_sistema import ElementoSistema, RepositorioBase, RegistroActividad
from typing import List, Dict, Optional, Set
from pathlib import Path


class Implemento(ElementoSistema):
    """Representa un implemento disponible para préstamo"""
    
    ESTADOS_VALIDOS = ['disponible', 'prestado', 'dañado', 'mantenimiento']
    
    def __init__(self, identificador: str, titulo: str, tipo: str, 
                 stock: int, condicion: str, precio_estimado: float):
        super().__init__(identificador)
        self.titulo = titulo
        self.tipo = tipo
        self.stock = stock
        self.condicion = condicion
        self.precio_estimado = precio_estimado
    
    def a_diccionario(self) -> Dict:
        return {
            'id': self.identificador,
            'titulo': self.titulo,
            'tipo': self.tipo,
            'stock': self.stock,
            'condicion': self.condicion,
            'precio_estimado': self.precio_estimado
        }
    
    @classmethod
    def desde_diccionario(cls, datos: Dict):
        return cls(
            identificador=datos['id'],
            titulo=datos['titulo'],
            tipo=datos['tipo'],
            stock=int(datos['stock']),
            condicion=datos['condicion'],
            precio_estimado=float(datos['precio_estimado'])
        )
    
    def ajustar_stock(self, cantidad: int) -> bool:
        """Ajusta el stock del implemento"""
        nuevo_stock = self.stock + cantidad
        if nuevo_stock < 0:
            return False
        self.stock = nuevo_stock
        return True
    
    def hay_disponibilidad(self, cantidad_solicitada: int) -> bool:
        """Verifica si hay suficiente stock"""
        return self.stock >= cantidad_solicitada and self.condicion == 'disponible'
    
    def marcar_condicion(self, nueva_condicion: str):
        """Cambia el estado del implemento"""
        if nueva_condicion in self.ESTADOS_VALIDOS:
            self.condicion = nueva_condicion


class AdministradorImplementos:
    """Gestiona el inventario de implementos"""
    
    def __init__(self, nombre_archivo: str = "inventario.txt"):
        self.repositorio = RepositorioBase(nombre_archivo)
        self.coleccion: List[Implemento] = []
        self.ids_en_uso: Set[str] = set()
        self.categorias_registradas: Set[str] = set()
        self._cargar_desde_archivo()
    
    def _cargar_desde_archivo(self):
        """Lee implementos del archivo"""
        self.repositorio.asegurar_archivo_existe()
        
        try:
            with open(self.repositorio.ruta_txt, 'r', encoding='utf-8') as f:
                for linea in f:
                    partes = linea.strip().split(',')
                    if len(partes) == 6:
                        try:
                            implemento = Implemento(
                                identificador=partes[0],
                                titulo=partes[1],
                                tipo=partes[2],
                                stock=int(partes[3]),
                                condicion=partes[4],
                                precio_estimado=float(partes[5])
                            )
                            self.coleccion.append(implemento)
                            self.ids_en_uso.add(partes[0])
                            self.categorias_registradas.add(partes[2])
                        except (ValueError, IndexError):
                            continue
        except FileNotFoundError:
            print("→ Archivo de inventario no encontrado. Se creará al guardar.")
    
    def agregar_nuevo(self, implemento: Implemento) -> bool:
        """Añade un nuevo implemento al inventario"""
        if implemento.identificador in self.ids_en_uso:
            RegistroActividad.registrar_fallo(
                f"ID duplicado al crear implemento: {implemento.identificador}"
            )
            return False
        
        self.coleccion.append(implemento)
        self.ids_en_uso.add(implemento.identificador)
        self.categorias_registradas.add(implemento.tipo)
        
        RegistroActividad.registrar_accion(
            f"Implemento creado: {implemento.titulo} (ID: {implemento.identificador})"
        )
        return True
    
    def buscar_por_id(self, identificador: str) -> Optional[Implemento]:
        """Busca un implemento por su ID"""
        for item in self.coleccion:
            if item.identificador == identificador:
                return item
        return None
    
    def obtener_todos(self) -> List[Implemento]:
        """Retorna todos los implementos"""
        return self.coleccion.copy()
    
    def filtrar_por_tipo(self, tipo: str) -> List[Implemento]:
        """Retorna implementos de un tipo específico"""
        return [item for item in self.coleccion if item.tipo.lower() == tipo.lower()]
    
    def filtrar_stock_bajo(self, limite: int = 3) -> List[Implemento]:
        """Retorna implementos con stock menor al límite"""
        return [item for item in self.coleccion if item.stock < limite]
    
    def modificar_existente(self, identificador: str, nuevos_datos: Dict) -> bool:
        """Actualiza los datos de un implemento"""
        implemento = self.buscar_por_id(identificador)
        if not implemento:
            return False
        
        if 'titulo' in nuevos_datos:
            implemento.titulo = nuevos_datos['titulo']
        if 'tipo' in nuevos_datos:
            implemento.tipo = nuevos_datos['tipo']
            self.categorias_registradas.add(nuevos_datos['tipo'])
        if 'stock' in nuevos_datos:
            implemento.stock = int(nuevos_datos['stock'])
        if 'condicion' in nuevos_datos:
            implemento.condicion = nuevos_datos['condicion']
        if 'precio_estimado' in nuevos_datos:
            implemento.precio_estimado = float(nuevos_datos['precio_estimado'])
        
        RegistroActividad.registrar_accion(
            f"Implemento actualizado: {implemento.titulo} (ID: {identificador})"
        )
        return True
    
    def eliminar_del_sistema(self, identificador: str) -> bool:
        """Elimina un implemento del inventario"""
        implemento = self.buscar_por_id(identificador)
        if not implemento:
            return False
        
        self.coleccion.remove(implemento)
        self.ids_en_uso.discard(identificador)
        
        RegistroActividad.registrar_accion(
            f"Implemento eliminado: {implemento.titulo} (ID: {identificador})"
        )
        return True
    
    def persistir_cambios(self):
        """Guarda todos los cambios en los archivos"""
        datos = [item.a_diccionario() for item in self.coleccion]
        campos = ['id', 'titulo', 'tipo', 'stock', 'condicion', 'precio_estimado']
        resultado = self.repositorio.persistir_multiformato(datos, campos)
        return resultado


class InterfazImplementos:
    """Interfaz de usuario para gestión de implementos"""
    
    def __init__(self, administrador: AdministradorImplementos):
        self.admin = administrador
    
    def mostrar_menu_principal(self):
        """Muestra el menú de opciones"""
        print("\n" + "╔" + "═" * 48 + "╗")
        print("║" + " " * 12 + "GESTIÓN DE IMPLEMENTOS" + " " * 14 + "║")
        print("╚" + "═" * 48 + "╝")
        print("  [1] Mostrar inventario completo")
        print("  [2] Registrar nuevo implemento")
        print("  [3] Localizar implemento por ID")
        print("  [4] Modificar implemento existente")
        print("  [5] Dar de baja implemento")
        print("  [6] Marcar como dañado")
        print("  [7] Persistir cambios en disco")
        print("  [8] Regresar")
        print("─" * 50)
    
    def mostrar_listado_completo(self):
        """Muestra todos los implementos en tabla"""
        implementos = self.admin.obtener_todos()
        
        if not implementos:
            print("\n⚠ No hay implementos registrados en el sistema")
            return
        
        print("\n" + "─" * 95)
        print(f"{'ID':<12}{'Nombre':<22}{'Categoría':<18}{'Stock':<10}{'Estado':<18}{'Valor ($)'}")
        print("─" * 95)
        
        for impl in implementos:
            print(
                f"{impl.identificador:<12}"
                f"{impl.titulo:<22}"
                f"{impl.tipo:<18}"
                f"{impl.stock:<10}"
                f"{impl.condicion:<18}"
                f"{impl.precio_estimado:>10.2f}"
            )
        print("─" * 95)
    
    def proceso_creacion(self):
        """Proceso interactivo para crear implemento"""
        print("\n→ REGISTRO DE NUEVO IMPLEMENTO")
        
        id_impl = input("  Código identificador: ").strip()
        if id_impl in self.admin.ids_en_uso:
            print("  ✗ Este código ya está en uso")
            RegistroActividad.registrar_fallo(f"Intento de crear implemento con ID duplicado: {id_impl}")
            return
        
        nombre = input("  Nombre del implemento: ").strip()
        categoria = input("  Categoría (ej. construcción/jardinería): ").strip()
        
        try:
            cantidad = int(input("  Cantidad inicial: "))
            if cantidad < 0:
                print("  ✗ La cantidad no puede ser negativa")
                return
        except ValueError:
            print("  ✗ Cantidad inválida")
            return
        
        print("\n  Estado del implemento:")
        print("    [1] Disponible")
        print("    [2] Prestado")
        print("    [3] Dañado")
        print("    [4] En mantenimiento")
        
        opcion_estado = input("  Selección: ").strip()
        estados_map = {
            '1': 'disponible',
            '2': 'prestado',
            '3': 'dañado',
            '4': 'mantenimiento'
        }
        estado = estados_map.get(opcion_estado, 'disponible')
        
        try:
            valor = float(input("  Valor estimado ($): "))
            if valor < 0:
                print("  ✗ El valor no puede ser negativo")
                return
        except ValueError:
            print("  ✗ Valor inválido")
            return
        
        implemento = Implemento(id_impl, nombre, categoria, cantidad, estado, valor)
        
        if self.admin.agregar_nuevo(implemento):
            print("  ✓ Implemento registrado exitosamente")
        else:
            print("  ✗ No se pudo registrar el implemento")
    
    def proceso_busqueda(self):
        """Busca y muestra información de un implemento"""
        id_buscar = input("\n  Ingrese ID del implemento: ").strip()
        implemento = self.admin.buscar_por_id(id_buscar)
        
        if implemento:
            print("\n" + "┌" + "─" * 48 + "┐")
            print(f"  ID: {implemento.identificador}")
            print(f"  Nombre: {implemento.titulo}")
            print(f"  Categoría: {implemento.tipo}")
            print(f"  Stock disponible: {implemento.stock} unidades")
            print(f"  Condición: {implemento.condicion}")
            print(f"  Valor estimado: ${implemento.precio_estimado:.2f}")
            print("└" + "─" * 48 + "┘")
        else:
            print("  ✗ Implemento no encontrado")
    
    def proceso_modificacion(self):
        """Modifica un implemento existente"""
        id_modificar = input("\n  ID del implemento a modificar: ").strip()
        implemento = self.admin.buscar_por_id(id_modificar)
        
        if not implemento:
            print("  ✗ Implemento no encontrado")
            return
        
        print(f"\n  Modificando: {implemento.titulo}")
        print("  (Presione Enter para mantener el valor actual)")
        
        nuevo_nombre = input(f"  Nuevo nombre [{implemento.titulo}]: ").strip()
        nueva_categoria = input(f"  Nueva categoría [{implemento.tipo}]: ").strip()
        
        nuevo_stock_str = input(f"  Nuevo stock [{implemento.stock}]: ").strip()
        nuevo_stock = None
        if nuevo_stock_str:
            try:
                nuevo_stock = int(nuevo_stock_str)
            except ValueError:
                print("  ⚠ Stock inválido, se mantendrá el actual")
        
        print("\n  Estado:")
        print("    [1] Disponible")
        print("    [2] Prestado")
        print("    [3] Dañado")
        print("    [4] En mantenimiento")
        opcion_estado = input("  Selección (Enter para mantener): ").strip()
        
        estados_map = {
            '1': 'disponible',
            '2': 'prestado',
            '3': 'dañado',
            '4': 'mantenimiento'
        }
        nuevo_estado = estados_map.get(opcion_estado)
        
        nuevo_valor_str = input(f"  Nuevo valor [{implemento.precio_estimado}]: ").strip()
        nuevo_valor = None
        if nuevo_valor_str:
            try:
                nuevo_valor = float(nuevo_valor_str)
            except ValueError:
                print("  ⚠ Valor inválido, se mantendrá el actual")
        
        # Aplicar cambios
        datos_actualizados = {}
        if nuevo_nombre:
            datos_actualizados['titulo'] = nuevo_nombre
        if nueva_categoria:
            datos_actualizados['tipo'] = nueva_categoria
        if nuevo_stock is not None:
            datos_actualizados['stock'] = nuevo_stock
        if nuevo_estado:
            datos_actualizados['condicion'] = nuevo_estado
        if nuevo_valor is not None:
            datos_actualizados['precio_estimado'] = nuevo_valor
        
        if self.admin.modificar_existente(id_modificar, datos_actualizados):
            print("  ✓ Implemento actualizado correctamente")
        else:
            print("  ✗ Error al actualizar")
    
    def proceso_eliminacion(self):
        """Elimina un implemento del sistema"""
        id_eliminar = input("\n  ID del implemento a eliminar: ").strip()
        implemento = self.admin.buscar_por_id(id_eliminar)
        
        if not implemento:
            print("  ✗ Implemento no encontrado")
            return
        
        confirmacion = input(f"  ¿Confirmar eliminación de '{implemento.titulo}'? (s/n): ").lower().strip()
        
        if confirmacion == 's':
            if self.admin.eliminar_del_sistema(id_eliminar):
                print("  ✓ Implemento eliminado del sistema")
            else:
                print("  ✗ Error al eliminar")
        else:
            print("  ⚠ Operación cancelada")
    
    def proceso_marcar_danado(self):
        """Marca un implemento como dañado"""
        id_impl = input("\n  ID del implemento dañado: ").strip()
        implemento = self.admin.buscar_por_id(id_impl)
        
        if not implemento:
            print("  ✗ Implemento no encontrado")
            return
        
        implemento.marcar_condicion('dañado')
        print(f"  ✓ '{implemento.titulo}' marcado como dañado")
        RegistroActividad.registrar_accion(
            f"Implemento marcado como dañado: {implemento.titulo} (ID: {id_impl})"
        )
    
    def ejecutar(self):
        """Ejecuta el menú interactivo"""
        while True:
            self.mostrar_menu_principal()
            seleccion = input("\n  Opción: ").strip()
            
            if seleccion == '1':
                self.mostrar_listado_completo()
            elif seleccion == '2':
                self.proceso_creacion()
            elif seleccion == '3':
                self.proceso_busqueda()
            elif seleccion == '4':
                self.proceso_modificacion()
            elif seleccion == '5':
                self.proceso_eliminacion()
            elif seleccion == '6':
                self.proceso_marcar_danado()
            elif seleccion == '7':
                resultado = self.admin.persistir_cambios()
                if all(resultado.values()):
                    print("\n  ✓ Cambios guardados en todos los formatos")
                else:
                    print("\n  ⚠ Algunos archivos no se pudieron guardar")
            elif seleccion == '8':
                respuesta = input("\n  ¿Guardar cambios antes de salir? (s/n): ").lower().strip()
                if respuesta == 's':
                    self.admin.persistir_cambios()
                print("  → Saliendo del gestor de implementos...")
                break
            else:
                print("  ✗ Opción inválida")