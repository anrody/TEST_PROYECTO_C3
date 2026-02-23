"""
Módulo de reportes y consultas del sistema
"""

from modulo_implementos import AdministradorImplementos
from modulo_miembros import ControladorMiembros
from modulo_asignaciones import GestorAsignaciones
from typing import List, Tuple


class GeneradorReportes:
    """Genera reportes y estadísticas del sistema"""
    
    def __init__(self, admin_impl, ctrl_miembros, gestor_asig):
        self.admin_impl = admin_impl
        self.ctrl_miembros = ctrl_miembros
        self.gestor_asig = gestor_asig
    
    def implementos_stock_critico(self, umbral: int = 3):
        """Retorna implementos con stock bajo"""
        return self.admin_impl.filtrar_stock_bajo(umbral)
    
    def asignaciones_vigentes(self):
        """Retorna todas las asignaciones activas"""
        return self.gestor_asig.obtener_activas()
    
    def asignaciones_atrasadas(self):
        """Retorna asignaciones vencidas"""
        return self.gestor_asig.obtener_vencidas()
    
    def historial_miembro(self, codigo_miembro: str):
        """Historial de asignaciones de un miembro"""
        return self.gestor_asig.obtener_por_miembro(codigo_miembro)
    
    def implementos_populares(self) -> List[Tuple[str, int]]:
        """Retorna los implementos más solicitados"""
        contador = {}
        
        for asig in self.gestor_asig.obtener_todas():
            impl_id = asig.codigo_implemento
            contador[impl_id] = contador.get(impl_id, 0) + 1
        
        ranking = sorted(contador.items(), key=lambda x: x[1], reverse=True)
        return ranking[:10]
    
    def miembros_activos(self) -> List[Tuple[str, int]]:
        """Retorna miembros con más asignaciones"""
        contador = {}
        
        for asig in self.gestor_asig.obtener_todas():
            miembro_id = asig.codigo_miembro
            contador[miembro_id] = contador.get(miembro_id, 0) + 1
        
        ranking = sorted(contador.items(), key=lambda x: x[1], reverse=True)
        return ranking[:10]


class InterfazReportes:
    """Pantallas para consultas y reportes"""
    
    def __init__(self, generador: GeneradorReportes, admin_impl, ctrl_miembros):
        self.gen = generador
        self.admin_impl = admin_impl
        self.ctrl_miembros = ctrl_miembros
    
    def menu(self):
        print("\n" + "╔" + "═" * 45 + "╗")
        print("║" + " " * 12 + "CONSULTAS Y REPORTES" + " " * 13 + "║")
        print("╚" + "═" * 45 + "╝")
        print("  [1] Implementos con stock crítico")
        print("  [2] Asignaciones vigentes")
        print("  [3] Asignaciones vencidas")
        print("  [4] Historial de un miembro")
        print("  [5] Implementos más solicitados")
        print("  [6] Miembros más activos")
        print("  [7] Volver")
        print("─" * 47)
    
    def mostrar_stock_critico(self):
        items = self.gen.implementos_stock_critico()
        if not items:
            print("\n✓ No hay implementos con stock crítico")
            return
        
        print("\n⚠ IMPLEMENTOS CON STOCK BAJO:")
        print("─" * 60)
        for item in items:
            print(f"  {item.titulo}: {item.stock} unidades")
        print("─" * 60)
    
    def mostrar_vigentes(self):
        asigs = self.gen.asignaciones_vigentes()
        if not asigs:
            print("\n✓ No hay asignaciones vigentes")
            return
        
        print("\n→ ASIGNACIONES ACTIVAS:")
        print("─" * 80)
        for a in asigs:
            miembro = self.ctrl_miembros.localizar(a.codigo_miembro)
            impl = self.admin_impl.buscar_por_id(a.codigo_implemento)
            nombre_m = miembro.nombre_completo() if miembro else "Desconocido"
            nombre_i = impl.titulo if impl else "Desconocido"
            print(f"  ID: {a.identificador} | {nombre_m} | {nombre_i} | Retorno: {a.fecha_retorno}")
        print("─" * 80)
    
    def mostrar_vencidas(self):
        asigs = self.gen.asignaciones_atrasadas()
        if not asigs:
            print("\n✓ No hay asignaciones vencidas")
            return
        
        print("\n⚠ ASIGNACIONES VENCIDAS:")
        print("─" * 80)
        for a in asigs:
            miembro = self.ctrl_miembros.localizar(a.codigo_miembro)
            impl = self.admin_impl.buscar_por_id(a.codigo_implemento)
            nombre_m = miembro.nombre_completo() if miembro else "Desconocido"
            nombre_i = impl.titulo if impl else "Desconocido"
            print(f"  ID: {a.identificador} | {nombre_m} | {nombre_i} | Vencido: {a.fecha_retorno}")
        print("─" * 80)
    
    def mostrar_historial_miembro(self):
        codigo = input("\n  Código del miembro: ").strip()
        miembro = self.ctrl_miembros.localizar(codigo)
        
        if not miembro:
            print("  ✗ Miembro no encontrado")
            return
        
        asigs = self.gen.historial_miembro(codigo)
        if not asigs:
            print(f"\n  {miembro.nombre_completo()} no tiene historial")
            return
        
        print(f"\n→ HISTORIAL DE {miembro.nombre_completo().upper()}")
        print("─" * 80)
        for a in asigs:
            impl = self.admin_impl.buscar_por_id(a.codigo_implemento)
            nombre_i = impl.titulo if impl else "Desconocido"
            print(f"  {a.identificador} | {nombre_i} | {a.unidades} ud | Estado: {a.estado}")
        print("─" * 80)
    
    def mostrar_implementos_populares(self):
        ranking = self.gen.implementos_populares()
        if not ranking:
            print("\n  No hay datos")
            return
        
        print("\n→ IMPLEMENTOS MÁS SOLICITADOS:")
        print("─" * 60)
        for i, (impl_id, cantidad) in enumerate(ranking, 1):
            impl = self.admin_impl.buscar_por_id(impl_id)
            nombre = impl.titulo if impl else "Desconocido"
            print(f"  {i}. {nombre}: {cantidad} asignaciones")
        print("─" * 60)
    
    def mostrar_miembros_activos(self):
        ranking = self.gen.miembros_activos()
        if not ranking:
            print("\n  No hay datos")
            return
        
        print("\n→ MIEMBROS MÁS ACTIVOS:")
        print("─" * 60)
        for i, (miembro_id, cantidad) in enumerate(ranking, 1):
            miembro = self.ctrl_miembros.localizar(miembro_id)
            nombre = miembro.nombre_completo() if miembro else "Desconocido"
            print(f"  {i}. {nombre}: {cantidad} asignaciones")
        print("─" * 60)
    
    def ejecutar(self):
        while True:
            self.menu()
            opcion = input("\n  Opción: ").strip()
            
            if opcion == '1':
                self.mostrar_stock_critico()
            elif opcion == '2':
                self.mostrar_vigentes()
            elif opcion == '3':
                self.mostrar_vencidas()
            elif opcion == '4':
                self.mostrar_historial_miembro()
            elif opcion == '5':
                self.mostrar_implementos_populares()
            elif opcion == '6':
                self.mostrar_miembros_activos()
            elif opcion == '7':
                break
            else:
                print("  ✗ Opción inválida")