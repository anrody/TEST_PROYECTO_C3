"""
Módulo para gestión de miembros de la comunidad
"""

from nucleo_sistema import ElementoSistema, RepositorioBase, RegistroActividad
from typing import List, Dict, Optional, Set


class Miembro(ElementoSistema):
    """Representa un miembro de la comunidad"""
    
    ROLES_VALIDOS = ['residente', 'administrador']
    
    def __init__(self, identificador: str, nombres: str, apellidos: str,
                 telefono: str, ubicacion: str, rol: str):
        super().__init__(identificador)
        self.nombres = nombres
        self.apellidos = apellidos
        self.telefono = telefono
        self.ubicacion = ubicacion
        self.rol = rol
    
    def a_diccionario(self) -> Dict:
        return {
            'id': self.identificador,
            'nombres': self.nombres,
            'apellidos': self.apellidos,
            'telefono': self.telefono,
            'ubicacion': self.ubicacion,
            'rol': self.rol
        }
    
    @classmethod
    def desde_diccionario(cls, datos: Dict):
        return cls(
            identificador=datos['id'],
            nombres=datos['nombres'],
            apellidos=datos['apellidos'],
            telefono=datos['telefono'],
            ubicacion=datos['ubicacion'],
            rol=datos['rol']
        )
    
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del miembro"""
        return f"{self.nombres} {self.apellidos}"
    
    def es_admin(self) -> bool:
        """Verifica si el miembro es administrador"""
        return self.rol == 'administrador'


class ControladorMiembros:
    """Gestiona los miembros de la comunidad"""
    
    def __init__(self, nombre_archivo: str = "miembros.txt"):
        self.repositorio = RepositorioBase(nombre_archivo)
        self.registro: List[Miembro] = []
        self.codigos_usados: Set[str] = set()
        self._recuperar_datos()
    
    def _recuperar_datos(self):
        """Carga miembros desde el archivo"""
        self.repositorio.asegurar_archivo_existe()
        
        try:
            with open(self.repositorio.ruta_txt, 'r', encoding='utf-8') as f:
                for linea in f:
                    campos = linea.strip().split(',')
                    if len(campos) == 6:
                        try:
                            miembro = Miembro(
                                identificador=campos[0],
                                nombres=campos[1],
                                apellidos=campos[2],
                                telefono=campos[3],
                                ubicacion=campos[4],
                                rol=campos[5]
                            )
                            self.registro.append(miembro)
                            self.codigos_usados.add(campos[0])
                        except (ValueError, IndexError):
                            continue
        except FileNotFoundError:
            print("→ Archivo de miembros no encontrado. Se creará al guardar.")
    
    def inscribir(self, miembro: Miembro) -> bool:
        """Registra un nuevo miembro"""
        if miembro.identificador in self.codigos_usados:
            RegistroActividad.registrar_fallo(
                f"Código duplicado al registrar miembro: {miembro.identificador}"
            )
            return False
        
        self.registro.append(miembro)
        self.codigos_usados.add(miembro.identificador)
        
        RegistroActividad.registrar_accion(
            f"Miembro registrado: {miembro.nombre_completo()} (ID: {miembro.identificador})"
        )
        return True
    
    def localizar(self, identificador: str) -> Optional[Miembro]:
        """Busca un miembro por su código"""
        for persona in self.registro:
            if persona.identificador == identificador:
                return persona
        return None
    
    def listar_todos(self) -> List[Miembro]:
        """Retorna todos los miembros"""
        return self.registro.copy()
    
    def actualizar_info(self, identificador: str, nuevos_datos: Dict) -> bool:
        """Actualiza información de un miembro"""
        miembro = self.localizar(identificador)
        if not miembro:
            return False
        
        if 'nombres' in nuevos_datos:
            miembro.nombres = nuevos_datos['nombres']
        if 'apellidos' in nuevos_datos:
            miembro.apellidos = nuevos_datos['apellidos']
        if 'telefono' in nuevos_datos:
            miembro.telefono = nuevos_datos['telefono']
        if 'ubicacion' in nuevos_datos:
            miembro.ubicacion = nuevos_datos['ubicacion']
        if 'rol' in nuevos_datos and nuevos_datos['rol'] in Miembro.ROLES_VALIDOS:
            miembro.rol = nuevos_datos['rol']
        
        RegistroActividad.registrar_accion(
            f"Miembro actualizado: {miembro.nombre_completo()} (ID: {identificador})"
        )
        return True
    
    def dar_de_baja(self, identificador: str) -> bool:
        """Elimina un miembro del sistema"""
        miembro = self.localizar(identificador)
        if not miembro:
            return False
        
        self.registro.remove(miembro)
        self.codigos_usados.discard(identificador)
        
        RegistroActividad.registrar_accion(
            f"Miembro dado de baja: {miembro.nombre_completo()} (ID: {identificador})"
        )
        return True
    
    def guardar_datos(self):
        """Persiste los cambios en disco"""
        datos = [m.a_diccionario() for m in self.registro]
        campos = ['id', 'nombres', 'apellidos', 'telefono', 'ubicacion', 'rol']
        return self.repositorio.persistir_multiformato(datos, campos)


class PantallasMiembros:
    """Interfaz de usuario para gestión de miembros"""
    
    def __init__(self, controlador: ControladorMiembros):
        self.ctrl = controlador
    
    def display_menu(self):
        """Muestra el menú principal"""
        print("\n" + "╔" + "═" * 45 + "╗")
        print("║" + " " * 13 + "GESTIÓN DE MIEMBROS" + " " * 13 + "║")
        print("╚" + "═" * 45 + "╝")
        print("  [1] Ver todos los miembros")
        print("  [2] Inscribir nuevo miembro")
        print("  [3] Buscar miembro por código")
        print("  [4] Actualizar información")
        print("  [5] Dar de baja miembro")
        print("  [6] Guardar cambios")
        print("  [7] Retornar")
        print("─" * 47)
    
    def display_listado(self):
        """Muestra todos los miembros"""
        miembros = self.ctrl.listar_todos()
        
        if not miembros:
            print("\n⚠ No hay miembros registrados")
            return
        
        print("\n" + "─" * 100)
        print(f"{'Código':<12}{'Nombres':<20}{'Apellidos':<20}{'Teléfono':<15}{'Dirección':<22}{'Rol'}")
        print("─" * 100)
        
        for m in miembros:
            print(
                f"{m.identificador:<12}"
                f"{m.nombres:<20}"
                f"{m.apellidos:<20}"
                f"{m.telefono:<15}"
                f"{m.ubicacion:<22}"
                f"{m.rol}"
            )
        print("─" * 100)
    
    def flujo_inscripcion(self):
        """Proceso para inscribir nuevo miembro"""
        print("\n→ INSCRIPCIÓN DE NUEVO MIEMBRO")
        
        codigo = input("  Código de identificación: ").strip()
        if codigo in self.ctrl.codigos_usados:
            print("  ✗ Este código ya está registrado")
            RegistroActividad.registrar_fallo(f"Intento de registro con código duplicado: {codigo}")
            return
        
        nombres = input("  Nombres: ").strip()
        apellidos = input("  Apellidos: ").strip()
        telefono = input("  Teléfono de contacto: ").strip()
        direccion = input("  Dirección: ").strip()
        
        print("\n  Tipo de miembro:")
        print("    [1] Residente")
        print("    [2] Administrador")
        
        tipo_opcion = input("  Selección: ").strip()
        rol = 'residente' if tipo_opcion == '1' else 'administrador'
        
        miembro = Miembro(codigo, nombres, apellidos, telefono, direccion, rol)
        
        if self.ctrl.inscribir(miembro):
            print("  ✓ Miembro inscrito exitosamente")
        else:
            print("  ✗ No se pudo completar el registro")
    
    def flujo_busqueda(self):
        """Busca y muestra un miembro"""
        codigo = input("\n  Código del miembro: ").strip()
        miembro = self.ctrl.localizar(codigo)
        
        if miembro:
            print("\n" + "┌" + "─" * 48 + "┐")
            print(f"  Código: {miembro.identificador}")
            print(f"  Nombre: {miembro.nombre_completo()}")
            print(f"  Teléfono: {miembro.telefono}")
            print(f"  Dirección: {miembro.ubicacion}")
            print(f"  Rol: {miembro.rol}")
            print("└" + "─" * 48 + "┘")
        else:
            print("  ✗ Miembro no encontrado")
    
    def flujo_actualizacion(self):
        """Actualiza información de un miembro"""
        codigo = input("\n  Código del miembro: ").strip()
        miembro = self.ctrl.localizar(codigo)
        
        if not miembro:
            print("  ✗ Miembro no encontrado")
            return
        
        print(f"\n  Actualizando: {miembro.nombre_completo()}")
        
        nuevos_nombres = input("  Nuevos nombres: ").strip()
        nuevos_apellidos = input("  Nuevos apellidos: ").strip()
        nuevo_telefono = input("  Nuevo teléfono: ").strip()
        nueva_direccion = input("  Nueva dirección: ").strip()
        
        print("\n  Tipo de miembro:")
        print("    [1] Residente")
        print("    [2] Administrador")
        tipo_opcion = input("  Selección: ").strip()
        nuevo_rol = 'residente' if tipo_opcion == '1' else 'administrador'
        
        datos = {
            'nombres': nuevos_nombres,
            'apellidos': nuevos_apellidos,
            'telefono': nuevo_telefono,
            'ubicacion': nueva_direccion,
            'rol': nuevo_rol
        }
        
        if self.ctrl.actualizar_info(codigo, datos):
            print("  ✓ Información actualizada")
        else:
            print("  ✗ Error al actualizar")
    
    def flujo_baja(self):
        """Da de baja a un miembro"""
        codigo = input("\n  Código del miembro: ").strip()
        miembro = self.ctrl.localizar(codigo)
        
        if not miembro:
            print("  ✗ Miembro no encontrado")
            return
        
        confirmacion = input(f"  ¿Dar de baja a {miembro.nombre_completo()}? (s/n): ").lower().strip()
        
        if confirmacion == 's':
            if self.ctrl.dar_de_baja(codigo):
                print("  ✓ Miembro dado de baja")
            else:
                print("  ✗ Error")
        else:
            print("  ⚠ Operación cancelada")
    
    def iniciar(self):
        """Inicia el menú interactivo"""
        while True:
            self.display_menu()
            opcion = input("\n  Opción: ").strip()
            
            if opcion == '1':
                self.display_listado()
            elif opcion == '2':
                self.flujo_inscripcion()
            elif opcion == '3':
                self.flujo_busqueda()
            elif opcion == '4':
                self.flujo_actualizacion()
            elif opcion == '5':
                self.flujo_baja()
            elif opcion == '6':
                resultado = self.ctrl.guardar_datos()
                if all(resultado.values()):
                    print("\n  ✓ Datos guardados correctamente")
                else:
                    print("\n  ⚠ Algunos archivos no se guardaron")
            elif opcion == '7':
                guardar = input("\n  ¿Guardar antes de salir? (s/n): ").lower().strip()
                if guardar == 's':
                    self.ctrl.guardar_datos()
                print("  → Saliendo...")
                break
            else:
                print("  ✗ Opción inválida")