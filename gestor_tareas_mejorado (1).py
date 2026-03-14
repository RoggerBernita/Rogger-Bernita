import datetime
import json
import os
import logging
import sys

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class Task:
    def __init__(self, task_id: int, title: str, description: str = "", priority: str = "Media", due_date: datetime.date = None, status: str = "Pendiente", created_at: datetime.datetime = None):
        self.id = task_id
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status
        self.created_at = created_at if created_at else datetime.datetime.now()
        self.due_date = due_date # Almacenado como objeto date

    def __str__(self) -> str:
        due_str = self.due_date.strftime("%Y-%m-%d") if self.due_date else "N/A"
        status_icon = "✅" if self.status == "Completada" else "⏳"
        return f"[{self.id}] {status_icon} {self.title} | Prioridad: {self.priority} | Vence: {due_str} | Estado: {self.status}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "due_date": self.due_date.isoformat() if self.due_date else None
        }

    @classmethod
    def from_dict(cls, data: dict):
        due_date = None
        if data.get("due_date"):
            try:
                due_date = datetime.date.fromisoformat(data["due_date"])
            except ValueError:
                logging.error(f"Fecha de vencimiento inválida en datos cargados: {data['due_date']}")

        created_at = None
        if data.get("created_at"):
            try:
                created_at = datetime.datetime.fromisoformat(data["created_at"])
            except ValueError:
                logging.error(f"Fecha de creación inválida en datos cargados: {data['created_at']}")

        return cls(
            task_id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            priority=data.get("priority", "Media"),
            due_date=due_date,
            status=data.get("status", "Pendiente"),
            created_at=created_at
        )

class TaskManager:
    def __init__(self, data_file: str = "tasks.json"):
        self.data_file = data_file
        self.tasks = []
        self.next_id = 1
        self._load_tasks()

    def _load_tasks(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(d) for d in data]
                    if self.tasks:
                        self.next_id = max(task.id for task in self.tasks) + 1
                logging.info(f"Tareas cargadas desde {self.data_file}")
            except json.JSONDecodeError:
                logging.error(f"Error al decodificar JSON desde {self.data_file}. El archivo podría estar corrupto. Se iniciará con tareas vacías.")
                self.tasks = []
            except Exception as e:
                logging.error(f"Error inesperado al cargar tareas: {e}. Se iniciará con tareas vacías.")
                self.tasks = []
        else:
            logging.info("No se encontró archivo de datos, iniciando con lista de tareas vacía.")

    def _save_tasks(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([task.to_dict() for task in self.tasks], f, indent=4)
            logging.info(f"Tareas guardadas en {self.data_file}")
        except Exception as e:
            logging.error(f"Error al guardar tareas: {e}")

    def add_task(self, title: str, description: str = "", priority: str = "Media", due_date_str: str = None) -> bool:
        if not title.strip():
            logging.warning("Intento de agregar tarea con título vacío.")
            print("Error: El título no puede estar vacío.")
            return False
        
        valid_priorities = ["Alta", "Media", "Baja"]
        if priority not in valid_priorities:
            logging.warning(f"Intento de agregar tarea con prioridad inválida: {priority}")
            print(f"Error: Prioridad no válida. Debe ser {', '.join(valid_priorities)}.")
            return False

        due_date = None
        if due_date_str:
            try:
                due_date = datetime.date.fromisoformat(due_date_str)
            except ValueError:
                logging.warning(f"Formato de fecha inválido proporcionado: {due_date_str}")
                print("Advertencia: Formato de fecha inválido. La tarea se guardará sin fecha límite.")

        new_task = Task(self.next_id, title, description, priority, due_date)
        self.tasks.append(new_task)
        self.next_id += 1
        self._save_tasks()
        print(f"Tarea '{title}' agregada con éxito.")
        logging.info(f"Tarea {new_task.id} agregada: {title}")
        return True

    def list_tasks(self, filter_status: str = None, filter_priority: str = None, sort_by: str = None):
        filtered = self.tasks
        
        if filter_status:
            filtered = [t for t in filtered if t.status == filter_status]
        
        if filter_priority:
            filtered = [t for t in filtered if t.priority == filter_priority]

        if sort_by == "prioridad":
            priority_order = {"Alta": 0, "Media": 1, "Baja": 2}
            filtered.sort(key=lambda t: priority_order.get(t.priority, 3))
        elif sort_by == "fecha_creacion":
            filtered.sort(key=lambda t: t.created_at)
        elif sort_by == "fecha_vencimiento":
            # Las tareas sin fecha de vencimiento van al final
            filtered.sort(key=lambda t: t.due_date if t.due_date else datetime.date.max)

        if not filtered:
            print("\nNo se encontraron tareas.")
            return

        print("\n--- LISTA DE TAREAS ---")
        for task in filtered:
            print(task)
        logging.info(f"Listadas {len(filtered)} tareas.")

    def mark_completed(self, task_id: int) -> bool:
        task = self.find_task_by_id(task_id)
        if task:
            if task.status == "Completada":
                print("La tarea ya está completada.")
                return False
            else:
                task.status = "Completada"
                self._save_tasks()
                print(f"Tarea [{task_id}] marcada como completada.")
                logging.info(f"Tarea {task_id} marcada como completada.")
                return True
        else:
            logging.warning(f"Intento de marcar como completada tarea inexistente: {task_id}")
            print(f"Error: No se encontró la tarea con ID {task_id}.")
            return False

    def delete_task(self, task_id: int) -> bool:
        task = self.find_task_by_id(task_id)
        if task:
            confirm = get_user_input(f"¿Estás seguro de que deseas eliminar la tarea '{task.title}'? (s/n): ", validation_func=lambda x: x.lower() in ['s', 'n'], error_message="Por favor, ingresa 's' o 'n'.")
            if confirm == 's':
                self.tasks.remove(task)
                self._save_tasks()
                print("Tarea eliminada.")
                logging.info(f"Tarea {task_id} eliminada: {task.title}")
                return True
            else:
                print("Operación cancelada.")
                return False
        else:
            logging.warning(f"Intento de eliminar tarea inexistente: {task_id}")
            print(f"Error: No se encontró la tarea con ID {task_id}.")
            return False

    def edit_task(self, task_id: int) -> bool:
        task = self.find_task_by_id(task_id)
        if not task:
            logging.warning(f"Intento de editar tarea inexistente: {task_id}")
            print(f"Error: No se encontró la tarea con ID {task_id}.")
            return False

        print(f"Editando tarea: {task.title}")
        
        new_title = get_user_input(f"Nuevo título (deja vacío para mantener '{task.title}'): ", allow_empty=True)
        if new_title:
            task.title = new_title

        new_desc = get_user_input(f"Nueva descripción (deja vacío para mantener): ", allow_empty=True)
        if new_desc:
            task.description = new_desc

        valid_priorities = ["Alta", "Media", "Baja"]
        new_prio = get_user_input(f"Nueva prioridad (Alta, Media, Baja) (deja vacío para mantener '{task.priority}'): ", allow_empty=True, validation_func=lambda x: x in valid_priorities if x else True, error_message="Prioridad inválida. Debe ser Alta, Media o Baja.")
        if new_prio:
            task.priority = new_prio

        new_due_str = get_user_input("Nueva fecha límite (AAAA-MM-DD) (deja vacío para mantener o 'borrar' para eliminar): ", allow_empty=True)
        if new_due_str == 'borrar':
            task.due_date = None
            print("Fecha límite eliminada.")
        elif new_due_str:
            try:
                task.due_date = datetime.date.fromisoformat(new_due_str)
            except ValueError:
                logging.warning(f"Formato de fecha inválido al editar tarea {task_id}: {new_due_str}")
                print("Advertencia: Formato de fecha inválido. No se cambió la fecha.")

        self._save_tasks()
        print("Tarea actualizada con éxito.")
        logging.info(f"Tarea {task_id} editada.")
        return True

    def search_tasks(self, keyword: str):
        keyword_lower = keyword.lower()
        results = [t for t in self.tasks if keyword_lower in t.title.lower() or keyword_lower in t.description.lower()]
        if not results:
            print(f"No se encontraron tareas con la palabra: '{keyword}'")
            logging.info(f"Búsqueda de '{keyword}' sin resultados.")
        else:
            print(f"\n--- RESULTADOS DE BÚSQUEDA: '{keyword}' ---")
            for task in results:
                print(task)
            logging.info(f"Búsqueda de '{keyword}' encontró {len(results)} resultados.")

    def show_statistics(self):
        total = len(self.tasks)
        if total == 0:
            print("No hay tareas para mostrar estadísticas.")
            return

        pendientes = len([t for t in self.tasks if t.status == "Pendiente"])
        completadas = len([t for t in self.tasks if t.status == "Completada"])
        productividad = (completadas / total) * 100 if total > 0 else 0
        
        now = datetime.date.today()
        proximas = [t for t in self.tasks if t.status == "Pendiente" and t.due_date and (t.due_date - now).days <= 3 and (t.due_date - now).days >= 0]

        print("\n--- ESTADÍSTICAS ---")
        print(f"Total de tareas: {total}")
        print(f"Tareas pendientes: {pendientes}")
        print(f"Tareas completadas: {completadas}")
        print(f"Porcentaje de productividad: {productividad:.2f}%")
        
        if proximas:
            print("\n--- TAREAS PRÓXIMAS A VENCER (3 días o menos) ---")
            for t in proximas:
                print(t)
        logging.info("Estadísticas mostradas.")

    def find_task_by_id(self, task_id: int):
        for t in self.tasks:
            if t.id == task_id:
                return t
        return None

def clear_screen():
    # Para compatibilidad con diferentes sistemas operativos
    os.system('cls' if os.name == 'nt' else 'clear')

def get_user_input(prompt: str, validation_func=None, error_message: str = "Entrada inválida. Inténtalo de nuevo.", allow_empty: bool = False):
    while True:
        user_input = input(prompt).strip()
        if not user_input and allow_empty:
            return user_input
        if not user_input and not allow_empty:
            print("Este campo no puede estar vacío.")
            continue

        if validation_func:
            try:
                if validation_func(user_input):
                    return user_input
                else:
                    print(error_message)
            except ValueError:
                print(error_message)
        else:
            return user_input

def main():
    manager = TaskManager()
    
    # Datos de ejemplo si no hay tareas guardadas
    if not manager.tasks:
        manager.add_task("Terminar ensayo de historia", "Ensayo de 5 páginas", "Alta", "2026-03-20")
        manager.add_task("Estudiar para examen de matemáticas", "Temas: Cálculo y Álgebra", "Alta", "2026-03-25")
        manager.add_task("Lavar ropa", "Ropa de color y blanca", "Baja")

    while True:
        clear_screen()
        print("\n=== GESTOR DE TAREAS PERSONALES ===")
        print("1. Agregar nueva tarea")
        print("2. Ver todas las tareas")
        print("3. Ver solo tareas pendientes")
        print("4. Ver solo tareas completadas")
        print("5. Marcar tarea como completada")
        print("6. Editar tarea")
        print("7. Eliminar tarea")
        print("8. Buscar tareas")
        print("9. Estadísticas")
        print("10. Salir del programa")
        
        choice = get_user_input("\nSelecciona una opción: ", validation_func=lambda x: x.isdigit() and 1 <= int(x) <= 10, error_message="Por favor, ingresa un número entre 1 y 10.")

        if choice == "1":
            title = get_user_input("Título: ", allow_empty=False)
            desc = get_user_input("Descripción (opcional): ", allow_empty=True)
            prio = get_user_input("Prioridad (Alta, Media, Baja) [Media]: ", allow_empty=True, validation_func=lambda x: x in ["Alta", "Media", "Baja"] if x else True, error_message="Prioridad inválida. Debe ser Alta, Media o Baja.") or "Media"
            due = get_user_input("Fecha límite (AAAA-MM-DD) (opcional): ", allow_empty=True, validation_func=lambda x: datetime.date.fromisoformat(x) if x else True, error_message="Formato de fecha inválido. Usa AAAA-MM-DD.")
            manager.add_task(title, desc, prio, due)

        elif choice == "2":
            sort = get_user_input("¿Ordenar por (prioridad/fecha_creacion/fecha_vencimiento)? (deja vacío para orden por ID): ", allow_empty=True, validation_func=lambda x: x.lower() in ["prioridad", "fecha_creacion", "fecha_vencimiento"] if x else True, error_message="Opción de ordenamiento inválida.").lower()
            manager.list_tasks(sort_by=sort if sort else None)

        elif choice == "3":
            manager.list_tasks(filter_status="Pendiente")

        elif choice == "4":
            manager.list_tasks(filter_status="Completada")

        elif choice == "5":
            tid_str = get_user_input("ID de la tarea a completar: ", validation_func=lambda x: x.isdigit(), error_message="Por favor, ingresa un número válido para el ID.")
            if tid_str:
                manager.mark_completed(int(tid_str))

        elif choice == "6":
            tid_str = get_user_input("ID de la tarea a editar: ", validation_func=lambda x: x.isdigit(), error_message="Por favor, ingresa un número válido para el ID.")
            if tid_str:
                manager.edit_task(int(tid_str))

        elif choice == "7":
            tid_str = get_user_input("ID de la tarea a eliminar: ", validation_func=lambda x: x.isdigit(), error_message="Por favor, ingresa un número válido para el ID.")
            if tid_str:
                manager.delete_task(int(tid_str))

        elif choice == "8":
            kw = get_user_input("Palabra clave a buscar: ", allow_empty=False)
            manager.search_tasks(kw)

        elif choice == "9":
            manager.show_statistics()

        elif choice == "10":
            print("¡Hasta luego!")
            logging.info("Aplicación cerrada.")
            sys.exit(0) # Salida limpia
        
        get_user_input("Presiona Enter para continuar...") # Pausa para que el usuario vea los mensajes

if __name__ == "__main__":
    main()
