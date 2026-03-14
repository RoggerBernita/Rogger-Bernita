from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
from gestor_tareas_mejorado import TaskManager
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_super_segura_2024'  # Cambiar en producción
app.permanent_session_lifetime = timedelta(days=7)

# Archivo para almacenar usuarios
USERS_FILE = 'users.json'

# Cargar usuarios existentes
def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

# Guardar usuarios
def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4)

# Diccionario de gestores de tareas por usuario
task_managers = {}

def get_user_manager(username):
    if username not in task_managers:
        task_managers[username] = TaskManager(data_file=f'tasks_{username}.json')
    return task_managers[username]

# Template de Login
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestor de Tareas - Login</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .login-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            width: 100%;
            max-width: 400px;
            padding: 40px;
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .login-header h1 {
            font-size: 2em;
            color: #333;
            margin-bottom: 10px;
        }
        
        .login-header p {
            color: #666;
            font-size: 0.95em;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 5px;
            font-size: 1em;
            font-family: inherit;
            transition: border-color 0.3s ease;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 5px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-bottom: 15px;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .btn-secondary {
            background: #f0f0f0;
            color: #333;
            border: 2px solid #e0e0e0;
        }
        
        .btn-secondary:hover {
            background: #e0e0e0;
        }
        
        .toggle-form {
            text-align: center;
            margin-top: 20px;
            color: #666;
        }
        
        .toggle-form a {
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
            cursor: pointer;
        }
        
        .toggle-form a:hover {
            text-decoration: underline;
        }
        
        .alert {
            padding: 12px;
            border-radius: 5px;
            margin-bottom: 20px;
            display: none;
        }
        
        .alert.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            display: block;
        }
        
        .alert.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            display: block;
        }
        
        .form-section {
            display: none;
        }
        
        .form-section.active {
            display: block;
        }
        
        .demo-info {
            background: #e3f2fd;
            border: 1px solid #90caf9;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: 0.9em;
            color: #1565c0;
        }
        
        .demo-info strong {
            display: block;
            margin-bottom: 8px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h1>📋 Gestor de Tareas</h1>
            <p>Organiza tu día de manera eficiente</p>
        </div>
        
        <div id="alert" class="alert"></div>
        
        <div class="demo-info">
            <strong>🔐 Credenciales de Demostración:</strong>
            Usuario: <code>demo</code><br>
            Contraseña: <code>demo123</code>
        </div>
        
        <!-- Formulario de Login -->
        <div id="loginForm" class="form-section active">
            <form onsubmit="handleLogin(event)">
                <div class="form-group">
                    <label for="loginUsername">Usuario</label>
                    <input type="text" id="loginUsername" required placeholder="Ingresa tu usuario">
                </div>
                
                <div class="form-group">
                    <label for="loginPassword">Contraseña</label>
                    <input type="password" id="loginPassword" required placeholder="Ingresa tu contraseña">
                </div>
                
                <button type="submit" class="btn btn-primary">Iniciar Sesión</button>
            </form>
            
            <div class="toggle-form">
                ¿No tienes cuenta? <a onclick="toggleForms()">Regístrate aquí</a>
            </div>
        </div>
        
        <!-- Formulario de Registro -->
        <div id="registerForm" class="form-section">
            <form onsubmit="handleRegister(event)">
                <div class="form-group">
                    <label for="registerUsername">Usuario</label>
                    <input type="text" id="registerUsername" required placeholder="Elige un usuario">
                </div>
                
                <div class="form-group">
                    <label for="registerPassword">Contraseña</label>
                    <input type="password" id="registerPassword" required placeholder="Crea una contraseña segura">
                </div>
                
                <div class="form-group">
                    <label for="registerConfirm">Confirmar Contraseña</label>
                    <input type="password" id="registerConfirm" required placeholder="Confirma tu contraseña">
                </div>
                
                <button type="submit" class="btn btn-primary">Registrarse</button>
            </form>
            
            <div class="toggle-form">
                ¿Ya tienes cuenta? <a onclick="toggleForms()">Inicia sesión aquí</a>
            </div>
        </div>
    </div>
    
    <script>
        function toggleForms() {
            document.getElementById('loginForm').classList.toggle('active');
            document.getElementById('registerForm').classList.toggle('active');
            document.getElementById('alert').className = 'alert';
        }
        
        function showAlert(message, type) {
            const alert = document.getElementById('alert');
            alert.textContent = message;
            alert.className = `alert ${type}`;
        }
        
        function handleLogin(event) {
            event.preventDefault();
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;
            
            fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/dashboard';
                } else {
                    showAlert(data.message || 'Error al iniciar sesión', 'error');
                }
            })
            .catch(err => showAlert('Error: ' + err, 'error'));
        }
        
        function handleRegister(event) {
            event.preventDefault();
            const username = document.getElementById('registerUsername').value;
            const password = document.getElementById('registerPassword').value;
            const confirm = document.getElementById('registerConfirm').value;
            
            if (password !== confirm) {
                showAlert('Las contraseñas no coinciden', 'error');
                return;
            }
            
            if (password.length < 6) {
                showAlert('La contraseña debe tener al menos 6 caracteres', 'error');
                return;
            }
            
            fetch('/api/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    showAlert('Cuenta creada exitosamente. Inicia sesión ahora.', 'success');
                    setTimeout(() => toggleForms(), 1500);
                } else {
                    showAlert(data.message || 'Error al registrarse', 'error');
                }
            })
            .catch(err => showAlert('Error: ' + err, 'error'));
        }
    </script>
</body>
</html>
"""

# Template del Dashboard (igual al anterior pero con logout)
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestor de Tareas</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header-title h1 {
            font-size: 2.5em;
            margin-bottom: 5px;
        }
        
        .header-title p {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .user-info {
            text-align: right;
        }
        
        .user-info p {
            margin-bottom: 10px;
            font-size: 0.95em;
        }
        
        .btn-logout {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 2px solid white;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .btn-logout:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        .content {
            padding: 30px;
        }
        
        .form-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            border: 2px solid #e9ecef;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        .form-group input,
        .form-group textarea,
        .form-group select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1em;
            font-family: inherit;
        }
        
        .form-group textarea {
            resize: vertical;
            min-height: 80px;
        }
        
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        
        .btn {
            padding: 12px 25px;
            border: none;
            border-radius: 5px;
            font-size: 1em;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            width: 100%;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .btn-small {
            padding: 8px 15px;
            font-size: 0.9em;
            margin-right: 5px;
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .btn-success:hover {
            background: #218838;
        }
        
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        
        .btn-danger:hover {
            background: #c82333;
        }
        
        .btn-info {
            background: #17a2b8;
            color: white;
        }
        
        .btn-info:hover {
            background: #138496;
        }
        
        .filters {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .filter-btn {
            padding: 8px 15px;
            border: 2px solid #ddd;
            background: white;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .filter-btn.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        
        .tasks-section h2 {
            margin-bottom: 20px;
            color: #333;
            font-size: 1.5em;
        }
        
        .task-item {
            background: #f8f9fa;
            border-left: 5px solid #667eea;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: start;
            transition: all 0.3s ease;
        }
        
        .task-item:hover {
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transform: translateX(5px);
        }
        
        .task-item.completed {
            background: #e8f5e9;
            border-left-color: #28a745;
            opacity: 0.7;
        }
        
        .task-content {
            flex: 1;
        }
        
        .task-header {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .task-id {
            background: #667eea;
            color: white;
            padding: 3px 8px;
            border-radius: 3px;
            font-weight: 600;
            margin-right: 10px;
            font-size: 0.9em;
        }
        
        .task-title {
            font-size: 1.1em;
            font-weight: 600;
            color: #333;
        }
        
        .task-completed .task-title {
            text-decoration: line-through;
            color: #999;
        }
        
        .task-meta {
            display: flex;
            gap: 15px;
            font-size: 0.9em;
            color: #666;
            margin-bottom: 8px;
            flex-wrap: wrap;
        }
        
        .priority-badge {
            padding: 3px 8px;
            border-radius: 3px;
            font-weight: 600;
            font-size: 0.85em;
        }
        
        .priority-alta {
            background: #ffebee;
            color: #c62828;
        }
        
        .priority-media {
            background: #fff3e0;
            color: #e65100;
        }
        
        .priority-baja {
            background: #e8f5e9;
            color: #2e7d32;
        }
        
        .task-description {
            color: #666;
            font-size: 0.95em;
            margin-bottom: 10px;
            font-style: italic;
        }
        
        .task-actions {
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
        }
        
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #999;
        }
        
        .empty-state-icon {
            font-size: 3em;
            margin-bottom: 15px;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        
        .stat-card h3 {
            font-size: 2em;
            margin-bottom: 5px;
        }
        
        .stat-card p {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .alert {
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            display: none;
        }
        
        .alert.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            display: block;
        }
        
        .alert.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            display: block;
        }
        
        @media (max-width: 600px) {
            .form-row {
                grid-template-columns: 1fr;
            }
            
            .task-item {
                flex-direction: column;
            }
            
            .task-actions {
                width: 100%;
                margin-top: 10px;
            }
            
            .stats {
                grid-template-columns: 1fr;
            }
            
            .header {
                flex-direction: column;
                text-align: center;
            }
            
            .user-info {
                text-align: center;
                margin-top: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-title">
                <h1>📋 Gestor de Tareas</h1>
                <p>Organiza tu día de manera eficiente y segura</p>
            </div>
            <div class="user-info">
                <p>👤 Bienvenido, <strong>{{ username }}</strong></p>
                <button class="btn-logout" onclick="logout()">Cerrar Sesión</button>
            </div>
        </div>
        
        <div class="content">
            <div id="alert" class="alert"></div>
            
            <div class="form-section">
                <h3>➕ Agregar Nueva Tarea</h3>
                <form id="taskForm" onsubmit="addTask(event)">
                    <div class="form-group">
                        <label for="title">Título *</label>
                        <input type="text" id="title" required placeholder="Ej: Terminar proyecto">
                    </div>
                    
                    <div class="form-group">
                        <label for="description">Descripción</label>
                        <textarea id="description" placeholder="Detalles adicionales..."></textarea>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="priority">Prioridad</label>
                            <select id="priority">
                                <option value="Baja">Baja</option>
                                <option value="Media" selected>Media</option>
                                <option value="Alta">Alta</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="dueDate">Fecha Límite</label>
                            <input type="date" id="dueDate">
                        </div>
                    </div>
                    
                    <button type="submit" class="btn btn-primary">Agregar Tarea</button>
                </form>
            </div>
            
            <div class="stats" id="stats"></div>
            
            <div class="tasks-section">
                <h2>📝 Mis Tareas</h2>
                
                <div class="filters">
                    <button class="filter-btn active" onclick="filterTasks('all')">Todas</button>
                    <button class="filter-btn" onclick="filterTasks('Pendiente')">Pendientes</button>
                    <button class="filter-btn" onclick="filterTasks('Completada')">Completadas</button>
                </div>
                
                <div id="tasksList"></div>
            </div>
        </div>
    </div>
    
    <script>
        let currentFilter = 'all';
        
        function logout() {
            fetch('/api/logout', {method: 'POST'})
            .then(() => window.location.href = '/');
        }
        
        function addTask(event) {
            event.preventDefault();
            
            const title = document.getElementById('title').value;
            const description = document.getElementById('description').value;
            const priority = document.getElementById('priority').value;
            const dueDate = document.getElementById('dueDate').value;
            
            fetch('/api/tasks', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    title, description, priority, due_date: dueDate
                })
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    showAlert('Tarea agregada exitosamente', 'success');
                    document.getElementById('taskForm').reset();
                    loadTasks();
                } else {
                    showAlert(data.message || 'Error al agregar tarea', 'error');
                }
            })
            .catch(err => showAlert('Error: ' + err, 'error'));
        }
        
        function loadTasks() {
            fetch('/api/tasks')
            .then(r => r.json())
            .then(data => {
                renderTasks(data.tasks);
                updateStats(data.tasks);
            });
        }
        
        function renderTasks(tasks) {
            let filtered = tasks;
            if (currentFilter !== 'all') {
                filtered = tasks.filter(t => t.status === currentFilter);
            }
            
            const tasksList = document.getElementById('tasksList');
            
            if (filtered.length === 0) {
                tasksList.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">📭</div>
                        <p>No hay tareas para mostrar</p>
                    </div>
                `;
                return;
            }
            
            tasksList.innerHTML = filtered.map(task => `
                <div class="task-item ${task.status === 'Completada' ? 'completed' : ''}">
                    <div class="task-content">
                        <div class="task-header">
                            <span class="task-id">#${task.id}</span>
                            <span class="task-title">${task.title}</span>
                        </div>
                        <div class="task-meta">
                            <span class="priority-badge priority-${task.priority.toLowerCase()}">${task.priority}</span>
                            ${task.due_date ? `<span>📅 ${task.due_date}</span>` : ''}
                            <span>${task.status}</span>
                        </div>
                        ${task.description ? `<div class="task-description">${task.description}</div>` : ''}
                    </div>
                    <div class="task-actions">
                        ${task.status !== 'Completada' ? `
                            <button class="btn btn-success btn-small" onclick="completeTask(${task.id})">✓ Completar</button>
                        ` : ''}
                        <button class="btn btn-danger btn-small" onclick="deleteTask(${task.id})">🗑️ Eliminar</button>
                    </div>
                </div>
            `).join('');
        }
        
        function updateStats(tasks) {
            const total = tasks.length;
            const completed = tasks.filter(t => t.status === 'Completada').length;
            const pending = tasks.filter(t => t.status === 'Pendiente').length;
            const productivity = total > 0 ? ((completed / total) * 100).toFixed(1) : 0;
            
            document.getElementById('stats').innerHTML = `
                <div class="stat-card">
                    <h3>${total}</h3>
                    <p>Total de Tareas</p>
                </div>
                <div class="stat-card">
                    <h3>${pending}</h3>
                    <p>Pendientes</p>
                </div>
                <div class="stat-card">
                    <h3>${completed}</h3>
                    <p>Completadas</p>
                </div>
                <div class="stat-card">
                    <h3>${productivity}%</h3>
                    <p>Productividad</p>
                </div>
            `;
        }
        
        function completeTask(id) {
            fetch(`/api/tasks/${id}/complete`, {method: 'PUT'})
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    showAlert('Tarea marcada como completada', 'success');
                    loadTasks();
                }
            });
        }
        
        function deleteTask(id) {
            if (confirm('¿Estás seguro de que deseas eliminar esta tarea?')) {
                fetch(`/api/tasks/${id}`, {method: 'DELETE'})
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        showAlert('Tarea eliminada', 'success');
                        loadTasks();
                    }
                });
            }
        }
        
        function filterTasks(status) {
            currentFilter = status;
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            loadTasks();
        }
        
        function showAlert(message, type) {
            const alert = document.getElementById('alert');
            alert.textContent = message;
            alert.className = `alert ${type}`;
            setTimeout(() => {
                alert.className = 'alert';
            }, 3000);
        }
        
        // Cargar tareas al iniciar
        loadTasks();
        setInterval(loadTasks, 5000);
    </script>
</body>
</html>
"""

# Rutas
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template_string(DASHBOARD_TEMPLATE, username=session['username'])

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Usuario y contraseña requeridos'}), 400
    
    if len(username) < 3:
        return jsonify({'success': False, 'message': 'El usuario debe tener al menos 3 caracteres'}), 400
    
    users = load_users()
    if username in users:
        return jsonify({'success': False, 'message': 'El usuario ya existe'}), 400
    
    users[username] = generate_password_hash(password)
    save_users(users)
    
    return jsonify({'success': True, 'message': 'Cuenta creada exitosamente'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    users = load_users()
    
    if username not in users or not check_password_hash(users[username], password):
        return jsonify({'success': False, 'message': 'Usuario o contraseña incorrectos'}), 401
    
    session.permanent = True
    session['username'] = username
    return jsonify({'success': True, 'message': 'Sesión iniciada'})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    if 'username' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    manager = get_user_manager(session['username'])
    return jsonify({'tasks': [task.to_dict() for task in manager.tasks]})

@app.route('/api/tasks', methods=['POST'])
def create_task():
    if 'username' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    data = request.json
    title = data.get('title', '').strip()
    
    if not title:
        return jsonify({'success': False, 'message': 'El título no puede estar vacío'}), 400
    
    manager = get_user_manager(session['username'])
    success = manager.add_task(
        title=title,
        description=data.get('description', ''),
        priority=data.get('priority', 'Media'),
        due_date_str=data.get('due_date') if data.get('due_date') else None
    )
    
    return jsonify({'success': success})

@app.route('/api/tasks/<int:task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    if 'username' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    manager = get_user_manager(session['username'])
    success = manager.mark_completed(task_id)
    return jsonify({'success': success})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task_api(task_id):
    if 'username' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    manager = get_user_manager(session['username'])
    success = manager.delete_task(task_id)
    return jsonify({'success': success})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
