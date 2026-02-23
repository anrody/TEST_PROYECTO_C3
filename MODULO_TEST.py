#!/usr/bin/env python3
"""
Sistema de Gestión Comunitaria de Implementos
Archivo principal de ejecución
"""

from modulo_implementos import AdministradorImplementos, InterfazImplementos
from modulo_miembros import ControladorMiembros, PantallasMiembros
from modulo_asignaciones import GestorAsignaciones
from interfaz_asignaciones import PantallasAsignaciones
from modulo_reportes import GeneradorReportes, InterfazReportes


class SistemaPrincipal:
    """Controlador principal del sistema"""
    
    def __init__(self):
        # Inicializar componentes
        self.admin_impl = AdministradorImplementos("inventario.txt")
        self.ctrl_miembros = ControladorMiembros("miembros.txt")
        self.gestor_asig = GestorAsignaciones("asignaciones.txt")
        self.gen_reportes = GeneradorReportes(
            self.admin_impl,
            self.ctrl_miembros,
            self.gestor_asig
        )
    
    def menu_admin(self):
        """Menú para administradores"""
        while True:
            print("\n" + "╔" + "═" * 60 + "╗")
            print("║" + " " * 20 + "PANEL DE ADMINISTRACIÓN" + " " * 17 + "║")
            print("╚" + "═" * 60 + "╝")
            print("  [1] Gestión de Implementos")
            print("  [2] Gestión de Miembros")
            print("  [3] Gestión de Prestamos")
            print("  [4] Consultas y Reportes")
            print("  [5] Ver Prestamos vencidos")
            print("  [6] Regresar al menú principal")
            print("─" * 62)
            
            opcion = input("\n  Selección: ").strip()
            
            if opcion == '1':
                interfaz = InterfazImplementos(self.admin_impl)
                interfaz.ejecutar()
            elif opcion == '2':
                pantallas = PantallasMiembros(self.ctrl_miembros)
                pantallas.iniciar()
            elif opcion == '3':
                pantallas = PantallasAsignaciones(
                    self.gestor_asig,
                    self.admin_impl,
                    self.ctrl_miembros
                )
                pantallas.ejecutar()
            elif opcion == '4':
                interfaz = InterfazReportes(
                    self.gen_reportes,
                    self.admin_impl,
                    self.ctrl_miembros
                )
                interfaz.ejecutar()
            elif opcion == '5':
                self.mostrar_vencidas()
            elif opcion == '6':
                print("  → Regresando...")
                return
            else:
                print("  ✗ Opción inválida")
    
    def menu_residente(self):
        """Menú para residentes"""
        while True:
            print("\n" + "╔" + "═" * 60 + "╗")
            print("║" + " " * 22 + "PANEL DE RESIDENTE" + " " * 20 + "║")
            print("╚" + "═" * 60 + "╝")
            print("  [1] Ver implementos disponibles")
            print("  [2] Ver mis asignaciones")
            print("  [3] Consultar estado de un implemento")
            print("  [4] Ver historial personal")
            print("  [5] Regresar al menú principal")
            print("─" * 62)
            
            opcion = input("\n  Selección: ").strip()
            
            if opcion == '1':
                self.ver_implementos_disponibles()
            elif opcion == '2':
                self.ver_mis_asignaciones()
            elif opcion == '3':
                self.consultar_implemento()
            elif opcion == '4':
                self.ver_historial_personal()
            elif opcion == '5':
                print("  → Regresando...")
                return
            else:
                print("  ✗ Opción inválida")
    
    def ver_implementos_disponibles(self):
        """Muestra implementos con stock disponible"""
        implementos = self.admin_impl.obtener_todos()
        disponibles = [i for i in implementos if i.stock > 0 and i.condicion == 'disponible']
        
        if not disponibles:
            print("\n⚠ No hay implementos disponibles")
            return
        
        print("\n→ CATÁLOGO DE IMPLEMENTOS DISPONIBLES")
        print("─" * 70)
        print(f"{'ID':<12}{'Nombre':<30}{'Categoría':<18}{'Stock'}")
        print("─" * 70)
        for impl in disponibles:
            print(f"{impl.identificador:<12}{impl.titulo:<30}{impl.tipo:<18}{impl.stock}")
        print("─" * 70)
    
    def ver_mis_asignaciones(self):
        """Muestra asignaciones del residente"""
        codigo = input("\n  Ingrese su código: ").strip()
        miembro = self.ctrl_miembros.localizar(codigo)
        
        if not miembro:
            print("  ✗ Código no encontrado")
            return
        
        asignaciones = self.gestor_asig.obtener_por_miembro(codigo)
        activas = [a for a in asignaciones if a.estado == 'activo']
        
        if not activas:
            print(f"\n  {miembro.nombre_completo()} no tiene asignaciones activas")
            return
        
        print(f"\n→ ASIGNACIONES DE {miembro.nombre_completo().upper()}")
        print("─" * 85)
        print(f"{'ID':<12}{'Implemento':<30}{'Cantidad':<12}{'Retorno':<18}{'Estado'}")
        print("─" * 85)
        
        for a in activas:
            impl = self.admin_impl.buscar_por_id(a.codigo_implemento)
            nombre_impl = impl.titulo if impl else "Desconocido"
            print(f"{a.identificador:<12}{nombre_impl:<30}{a.unidades:<12}"
                  f"{a.fecha_retorno:<18}{a.estado}")
        print("─" * 85)
    
    def consultar_implemento(self):
        """Consulta estado de un implemento"""
        codigo = input("\n  Código del implemento: ").strip()
        impl = self.admin_impl.buscar_por_id(codigo)
        
        if not impl:
            print("  ✗ Implemento no encontrado")
            return
        
        print("\n" + "┌" + "─" * 48 + "┐")
        print(f"  Código: {impl.identificador}")
        print(f"  Nombre: {impl.titulo}")
        print(f"  Categoría: {impl.tipo}")
        print(f"  Stock disponible: {impl.stock} unidades")
        print(f"  Condición: {impl.condicion}")
        print(f"  Valor estimado: ${impl.precio_estimado:.2f}")
        print("└" + "─" * 48 + "┘")
    
    def ver_historial_personal(self):
        """Muestra historial completo del residente"""
        codigo = input("\n  Ingrese su código: ").strip()
        miembro = self.ctrl_miembros.localizar(codigo)
        
        if not miembro:
            print("  ✗ Código no encontrado")
            return
        
        historial = self.gestor_asig.obtener_por_miembro(codigo)
        
        if not historial:
            print(f"\n  {miembro.nombre_completo()} no tiene historial")
            return
        
        print(f"\n→ HISTORIAL COMPLETO DE {miembro.nombre_completo().upper()}")
        print("─" * 85)
        
        for a in historial:
            impl = self.admin_impl.buscar_por_id(a.codigo_implemento)
            nombre_impl = impl.titulo if impl else "Desconocido"
            print(f"  {a.identificador} | {nombre_impl} | {a.estado}")
        print("─" * 85)
    
    def mostrar_vencidas(self):
        """Muestra asignaciones vencidas"""
        vencidas = self.gen_reportes.asignaciones_atrasadas()
        
        if not vencidas:
            print("\n✓ No hay asignaciones vencidas")
            return
        
        print("\n⚠ ASIGNACIONES VENCIDAS")
        print("─" * 95)
        
        for a in vencidas:
            miembro = self.ctrl_miembros.localizar(a.codigo_miembro)
            impl = self.admin_impl.buscar_por_id(a.codigo_implemento)
            
            nombre_m = miembro.nombre_completo() if miembro else "Desconocido"
            nombre_i = impl.titulo if impl else "Desconocido"
            
            print(f"  {a.identificador} | {nombre_m} | {nombre_i} | Vencido: {a.fecha_retorno}")
        print("─" * 95)
    
    def menu_principal(self):
        """Menú de entrada principal"""
        while True:
            print("\n" + "╔" + "═" * 60 + "╗")
            print("║" + " " * 10 + "SISTEMA DE GESTIÓN COMUNITARIA" + " " * 19 + "║")
            print("║" + " " * 17 + "DE IMPLEMENTOS" + " " * 30 + "║")
            print("╚" + "═" * 60 + "╝")
            print("\n" + " " * 20 + "SELECCIONE UNA OPCIÓN")
            print("\n  [1] Panel de Residente")
            print("  [2] Panel de Administración")
            print("  [3] Salir del sistema")
            print("─" * 62)
            
            opcion = input("\n  Selección: ").strip()
            
            if opcion == '1':
                self.menu_residente()
            elif opcion == '2':
                self.menu_admin()
            elif opcion == '3':
                print("\n" + "─" * 62)
                print(" " * 18 + "Sistema finalizado")
                print(" " * 15 + "¡Hasta pronto!")
                print("─" * 62)
                break
            else:
                print("  ✗ Opción inválida. Seleccione 1, 2 o 3")
    
    def iniciar(self):
        """Inicia el sistema"""
        # Verificar que haya datos iniciales
        if not self.ctrl_miembros.listar_todos():
            print("\n⚠ ADVERTENCIA: No hay miembros registrados en el sistema")
            print("  El sistema funcionará, pero considere registrar miembros primero\n")
        
        self.menu_principal()


def main():
    """Punto de entrada del programa"""
    sistema = SistemaPrincipal()
    sistema.iniciar()


if __name__ == "__main__":
    main()