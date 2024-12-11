# Sistema de Gestión de Tareas

import heapq
import json
from datetime import datetime

class Tarea:
    def __init__(self, nombre, prioridad, fecha_vencimiento, dependencias=None):
        self.nombre = nombre
        self.prioridad = prioridad
        # Asegurarse de que fecha_vencimiento sea un objeto datetime o convertir si es una cadena
        if isinstance(fecha_vencimiento, str):
            try:
                self.fecha_vencimiento = datetime.strptime(fecha_vencimiento, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Error: La fecha de vencimiento debe tener el formato válido (YYYY-MM-DD).")
        else:
            self.fecha_vencimiento = fecha_vencimiento
        self.dependencias = dependencias if dependencias else []
        self.completada = False

    def __lt__(self, other):
        if self.prioridad == other.prioridad:
            return self.fecha_vencimiento < other.fecha_vencimiento
        return self.prioridad < other.prioridad

    def es_ejecutable(self, tareas_completadas):
        return all(dep in tareas_completadas for dep in self.dependencias)

class SistemaTareas:
    def __init__(self):
        self.heap = []
        self.tareas = {}
        self.tareas_completadas = set()
        self.ordenar_por = "prioridad"  # Por defecto, ordenar por prioridad
        self.cargar_datos()

    # Cambiar el criterio de ordenación
    def cambiar_criterio_ordenacion(self, criterio):
        if criterio not in ["prioridad", "fecha"]:
            print("Error: Criterio no válido. Usa 'prioridad' o 'fecha'.")
            return
        self.ordenar_por = criterio
        print(f"Criterio de ordenación cambiado a: {criterio}")

    # Agregar una nueva tarea
    def agregar_tarea(self, nombre, prioridad, fecha_vencimiento, dependencias=None):
        if isinstance(fecha_vencimiento, str):
            try:
                fecha_vencimiento = fecha_vencimiento.strip() if fecha_vencimiento else None
                if fecha_vencimiento:
                    fecha_vencimiento = datetime.strptime(fecha_vencimiento, "%Y-%m-%d")
            except ValueError:
                print("Error: La fecha de vencimiento debe tener el formato válido (YYYY-MM-DD).")
                return

        if not isinstance(prioridad, int) or not nombre:
            print("Error: Prioridad debe ser un número entero y el nombre no debe estar vacío.")
            return

        if nombre in self.tareas:
            print("Error: La tarea ya existe.")
            return

        if dependencias == ["no"]:  # Permitir la opción "no" para indicar que no hay dependencias
            dependencias = []

        nueva_tarea = Tarea(nombre, prioridad, fecha_vencimiento, dependencias)
        self.tareas[nombre] = nueva_tarea
        heapq.heappush(self.heap, nueva_tarea)
        print(f"Tarea '{nombre}' agregada correctamente.")

    # Mostrar tareas pendientes
    def mostrar_tareas(self):
        tareas_pendientes = [t for t in self.heap if not t.completada]
        if self.ordenar_por == "fecha":
            tareas_pendientes.sort(key=lambda t: (t.fecha_vencimiento, t.prioridad))
        else:
            tareas_pendientes.sort()
        print(f"Tareas pendientes en orden de {self.ordenar_por}:")
        for tarea in tareas_pendientes:
            fecha_vencimiento = tarea.fecha_vencimiento.strftime("%Y-%m-%d") if tarea.fecha_vencimiento else "Sin fecha"
            print(f"- {tarea.nombre} (Prioridad: {tarea.prioridad}, Fecha de vencimiento: {fecha_vencimiento}, Dependencias: {', '.join(tarea.dependencias)})")

    # Completar una tarea
    def completar_tarea(self, nombre):
        if nombre not in self.tareas:
            print("Error: La tarea no existe.")
            return

        tarea = self.tareas[nombre]
        dependencias_incompletas = [dep for dep in tarea.dependencias if dep not in self.tareas_completadas]

        if dependencias_incompletas:
            print(f"Error: No se puede completar la tarea '{nombre}' porque depende de las siguientes tareas no completadas: {', '.join(dependencias_incompletas)}.")
            return

        tarea.completada = True
        self.tareas_completadas.add(nombre)
        print(f"Tarea '{nombre}' completada.")

    # Obtener la tarea de mayor prioridad
    def obtener_tarea_mayor_prioridad(self):
        while self.heap:
            tarea = heapq.heappop(self.heap)
            if not tarea.completada:
                heapq.heappush(self.heap, tarea)
                fecha_vencimiento = tarea.fecha_vencimiento.strftime("%Y-%m-%d") if tarea.fecha_vencimiento else "Sin fecha"
                print(f"Tarea de mayor prioridad: {tarea.nombre} (Prioridad: {tarea.prioridad}, Fecha de vencimiento: {fecha_vencimiento})")
                return tarea
        print("No hay tareas pendientes.")

    # Guardar datos en un archivo
    def guardar_datos(self):
        with open("tareas.json", "w") as archivo:
            datos = {
                "tareas": [
                    {
                        "nombre": t.nombre,
                        "prioridad": t.prioridad,
                        "fecha_vencimiento": t.fecha_vencimiento.strftime("%Y-%m-%d") if t.fecha_vencimiento else None,
                        "dependencias": t.dependencias,
                        "completada": t.completada,
                    }
                    for t in self.tareas.values()
                ],
                "ordenar_por": self.ordenar_por
            }
            json.dump(datos, archivo)

    # Cargar datos desde un archivo
    def cargar_datos(self):
        try:
            with open("tareas.json", "r") as archivo:
                datos = json.load(archivo)
                for tarea_data in datos.get("tareas", []):
                    tarea = Tarea(
                        tarea_data["nombre"],
                        tarea_data["prioridad"],
                        tarea_data["fecha_vencimiento"],
                        tarea_data["dependencias"],
                    )
                    tarea.completada = tarea_data["completada"]
                    self.tareas[tarea.nombre] = tarea
                    if not tarea.completada:
                        heapq.heappush(self.heap, tarea)
                    else:
                        self.tareas_completadas.add(tarea.nombre)
                self.ordenar_por = datos.get("ordenar_por", "prioridad")
        except FileNotFoundError:
            pass

# Programa principal
if __name__ == "__main__":
    sistema = SistemaTareas()

    # Agregar tareas de prueba
    sistema.agregar_tarea("Tarea1", 2, "2024-12-15", [])
    sistema.agregar_tarea("Tarea2", 1, "2024-12-10", ["Tarea1"])
    sistema.agregar_tarea("Tarea3", 3, "2024-12-20", [])
    sistema.agregar_tarea("Tarea4", 5, "2024-12-25", ["Tarea1", "Tarea3"])
    sistema.agregar_tarea("Tarea5", 4, "2024-12-22", ["Tarea2"])

    while True:
        print("\n--- Sistema de Gestión de Tareas ---")
        print("1. Agregar tarea")
        print("2. Mostrar tareas pendientes")
        print("3. Completar tarea")
        print("4. Obtener tarea de mayor prioridad")
        print("5. Cambiar criterio de ordenación")
        print("6. Salir")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            nombre = input("Nombre de la tarea: ")
            try:
                prioridad = int(input("Prioridad de la tarea (número): "))
            except ValueError:
                print("Error: La prioridad debe ser un número entero.")
                continue
            fecha_vencimiento = input("Fecha de vencimiento (YYYY-MM-DD): ")
            dependencias = input("Dependencias (separadas por coma, si las hay, escribe 'no' si no hay): ").split(",")
            dependencias = [d.strip() for d in dependencias if d.strip()]
            sistema.agregar_tarea(nombre, prioridad, fecha_vencimiento, dependencias)

        elif opcion == "2":
            sistema.mostrar_tareas()

        elif opcion == "3":
            nombre = input("Nombre de la tarea a completar: ")
            sistema.completar_tarea(nombre)

        elif opcion == "4":
            sistema.obtener_tarea_mayor_prioridad()

        elif opcion == "5":
            criterio = input("Elige el criterio de ordenación ('prioridad' o 'fecha'): ")
            sistema.cambiar_criterio_ordenacion(criterio)

        elif opcion == "6":
            sistema.guardar_datos()
            print("Saliendo y guardando datos...")
            break

        else:
            print("Opción no válida. Inténtalo de nuevo.")

# BONUS: Verificación automática de dependencias cumplidas

# Esta funcionalidad ya está integrada en el método "es_ejecutable" de la clase Tarea. Antes de completar una tarea,
# se verifica si todas las dependencias están marcadas como completadas. Esto asegura que no se puedan completar
# tareas pendientes de dependencias.