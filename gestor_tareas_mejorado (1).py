import os

tasks = []

def limpiar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")

def mostrar_menu():
    print("\n" + "="*35)
    print("📋  GESTOR DE TAREAS PRO")
    print("="*35)
    print("1. ➕ Agregar tarea")
    print("2. 📋 Ver tareas")
    print("3. ✔️ Completar tarea")
    print("4. 🗑️ Eliminar tarea")
    print("5. 🚪 Salir")

def agregar_tarea():
    titulo = input("📝 Ingresa la tarea: ").strip()
    if titulo:
        tasks.append({"titulo": titulo, "estado": "Pendiente"})
        print("✅ Tarea agregada")
    else:
        print("❌ No puedes agregar una tarea vacía")

def ver_tareas():
    print("\n📋 LISTA DE TAREAS")
    print("-"*35)
    if not tasks:
        print("No hay tareas aún")
    else:
        for i, t in enumerate(tasks):
            estado = "✅" if t["estado"] == "Completada" else "⏳"
            print(f"{i+1}. {estado} {t['titulo']}")

def completar_tarea():
    ver_tareas()
    try:
        num = int(input("✔️ Número de tarea: "))
        tasks[num-1]["estado"] = "Completada"
        print("🎉 Tarea completada")
    except:
        print("❌ Número inválido")

def eliminar_tarea():
    ver_tareas()
    try:
        num = int(input("🗑️ Número de tarea a eliminar: "))
        tarea = tasks.pop(num-1)
        print(f"🗑️ Eliminaste: {tarea['titulo']}")
    except:
        print("❌ Número inválido")

while True:
    limpiar_pantalla()
    mostrar_menu()
    opcion = input("\n👉 Elige una opción: ")

    if opcion == "1":
        agregar_tarea()
    elif opcion == "2":
        ver_tareas()
    elif opcion == "3":
        completar_tarea()
    elif opcion == "4":
        eliminar_tarea()
    elif opcion == "5":
        print("👋 Hasta luego")
        break
    else:
        print("❌ Opción inválida")

    input("\nPresiona ENTER para continuar...")
