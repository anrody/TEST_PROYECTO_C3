"""
Interfaz para gestión de asignaciones
"""

from modulo_asignaciones import GestorAsignaciones, Asignacion
from modulo_implementos import AdministradorImplementos
from modulo_miembros import ControladorMiembros
from nucleo_sistema import Utilidades, RegistroActividad


class PantallasAsignaciones:
    """Interfaz para gestión de asignaciones"""
    
    def __init__(self, gestor, admin_impl, ctrl_miembros):
        self.gestor = gestor
        self.admin_impl = admin_impl
        self.ctrl_miembros = ctrl_miembros
    
    def menu(self):
        print("\n" + "╔" + "═" * 50 + "╗")
        print("║" + " " * 14 + "GESTIÓN DE ASIGNACIONES" + " " * 13 + "║")
        print("╚" + "═" * 50 + "╝")
        print("  [1] Ver todas las asignaciones")
        print("  [2] Crear nueva asignación")
        print("  [3] Procesar devolución")
        print("  [4] Cancelar asignación")
        print("  [5] Extender fecha de retorno")
        print("  [6] Guardar cambios")
        print("  [7] Retornar")
        print("─" * 52)
    
    def listar_todas(self):
        asigs = self.gestor.obtener_todas()
        if not asigs:
            print("\n⚠ No hay asignaciones registradas")
            return
        
        print("\n" + "─" * 110)
        print(f"{'ID':<12}{'Miembro':<28}{'Implemento':<28}{'Cant':<8}{'Retorno':<18}{'Estado'}")
        print("─" * 110)
        
        for a in asigs:
            miembro = self.ctrl_miembros.localizar(a.codigo_miembro)
            impl = self.admin_impl.buscar_por_id(a.codigo_implemento)
            
            nombre_m = miembro.nombre_completo() if miembro else "Desconocido"
            nombre_i = impl.titulo if impl else "Desconocido"
            
            print(f"{a.identificador:<12}{nombre_m:<28}{nombre_i:<28}"
                  f"{a.unidades:<8}{a.fecha_retorno:<18}{a.estado}")
        print("─" * 110)
    
    def proceso_creacion(self):
        print("\n→ NUEVA ASIGNACIÓN")
        
        id_asig = input("  ID de la asignación: ").strip()
        if id_asig in self.gestor.ids_usados:
            print("  ✗ Este ID ya existe")
            return
        
        codigo_miembro = input("  Código del miembro: ").strip()
        miembro = self.ctrl_miembros.localizar(codigo_miembro)
        if not miembro:
            print("  ✗ Miembro no encontrado")
            RegistroActividad.registrar_fallo(f"Asignación fallida: miembro {codigo_miembro} no existe")
            return
        
        codigo_impl = input("  Código del implemento: ").strip()
        impl = self.admin_impl.buscar_por_id(codigo_impl)
        if not impl:
            print("  ✗ Implemento no encontrado")
            RegistroActividad.registrar_fallo(f"Asignación fallida: implemento {codigo_impl} no existe")
            return
        
        try:
            unidades = int(input("  Cantidad a asignar: "))
            if unidades <= 0:
                print("  ✗ Cantidad inválida")
                return
        except ValueError:
            print("  ✗ Debe ingresar un número")
            return
        
        if not impl.hay_disponibilidad(unidades):
            print(f"  ✗ Stock insuficiente. Disponible: {impl.stock}")
            RegistroActividad.registrar_fallo(
                f"Stock insuficiente: {impl.titulo} - Solicitado: {unidades}, Disponible: {impl.stock}"
            )
            return
        
        fecha_salida = input("  Fecha de salida (YYYY-MM-DD): ").strip()
        fecha_retorno = input("  Fecha de retorno (YYYY-MM-DD): ").strip()
        
        if not Utilidades.validar_fecha(fecha_salida) or not Utilidades.validar_fecha(fecha_retorno):
            print("  ✗ Formato de fecha inválido")
            return
        
        asignacion = Asignacion(
            id_asig, codigo_miembro, codigo_impl,
            unidades, fecha_salida, fecha_retorno, "activo"
        )
        
        if self.gestor.crear(asignacion):
            impl.ajustar_stock(-unidades)
            print("  ✓ Asignación registrada correctamente")
            RegistroActividad.registrar_accion(
                f"Asignación creada: {id_asig} - {miembro.nombre_completo()} - {impl.titulo}"
            )
        else:
            print("  ✗ Error al crear asignación")
    
    def proceso_devolucion(self):
        id_asig = input("\n  ID de la asignación a devolver: ").strip()
        asignacion = self.gestor.buscar(id_asig)
        
        if not asignacion or asignacion.estado != "activo":
            print("  ✗ Asignación no encontrada o ya procesada")
            return
        
        impl = self.admin_impl.buscar_por_id(asignacion.codigo_implemento)
        if impl:
            impl.ajustar_stock(asignacion.unidades)
            asignacion.estado = "devuelto"
            print("  ✓ Devolución procesada correctamente")
            RegistroActividad.registrar_accion(
                f"Devolución procesada: {id_asig} - {impl.titulo}"
            )
        else:
            print("  ✗ Error al procesar devolución")
    
    def proceso_cancelacion(self):
        id_asig = input("\n  ID de la asignación: ").strip()
        asignacion = self.gestor.buscar(id_asig)
        
        if not asignacion or asignacion.estado != "activo":
            print("  ✗ Asignación no encontrada o no está activa")
            return
        
        impl = self.admin_impl.buscar_por_id(asignacion.codigo_implemento)
        if impl:
            impl.ajustar_stock(asignacion.unidades)
            asignacion.estado = "cancelado"
            print("  ✓ Asignación cancelada")
            RegistroActividad.registrar_accion(f"Asignación cancelada: {id_asig}")
        else:
            print("  ✗ Error al cancelar")
    
    def proceso_extension(self):
        id_asig = input("\n  ID de la asignación: ").strip()
        asignacion = self.gestor.buscar(id_asig)
        
        if not asignacion or asignacion.estado != "activo":
            print("  ✗ Asignación no encontrada o no está activa")
            return
        
        nueva_fecha = input("  Nueva fecha de retorno (YYYY-MM-DD): ").strip()
        
        if not Utilidades.validar_fecha(nueva_fecha):
            print("  ✗ Fecha inválida")
            return
        
        if Utilidades.comparar_fechas(nueva_fecha, asignacion.fecha_retorno) <= 0:
            print("  ✗ La nueva fecha debe ser posterior a la actual")
            return
        
        asignacion.fecha_retorno = nueva_fecha
        print("  ✓ Fecha de retorno extendida")
        RegistroActividad.registrar_accion(
            f"Fecha extendida: {id_asig} - Nueva fecha: {nueva_fecha}"
        )
    
    def ejecutar(self):
        while True:
            self.menu()
            opcion = input("\n  Opción: ").strip()
            
            if opcion == '1':
                self.listar_todas()
            elif opcion == '2':
                self.proceso_creacion()
            elif opcion == '3':
                self.proceso_devolucion()
            elif opcion == '4':
                self.proceso_cancelacion()
            elif opcion == '5':
                self.proceso_extension()
            elif opcion == '6':
                resultado = self.gestor.persistir()
                self.admin_impl.persistir_cambios()
                if all(resultado.values()):
                    print("\n  ✓ Cambios guardados")
                else:
                    print("\n  ⚠ Algunos archivos no se guardaron")
            elif opcion == '7':
                guardar = input("\n  ¿Guardar antes de salir? (s/n): ").lower().strip()
                if guardar == 's':
                    self.gestor.persistir()
                    self.admin_impl.persistir_cambios()
                print("  → Saliendo...")
                break
            else:
                print("  ✗ Opción inválida")