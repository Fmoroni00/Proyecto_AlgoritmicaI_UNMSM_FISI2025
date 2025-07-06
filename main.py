
from flask import Flask, render_template, request, send_file, redirect
from datetime import datetime
import pytz
import csv
import os

# Crear la aplicación Flask
app = Flask(__name__)
#Diccionario de menus:
menus_semanales = {
        0: [  # Lunes
            {"name": "Lunes Opción 1", "description": "Seco con Frejoles", "precio": 11, "image": "lunes1.png"},
            {"name": "Lunes Opción 2", "description": "Tallarines verdes con pollo a la olla", "precio": 11, "image": "lunes2.png"}
        ],
        1: [  # Martes
            {"name": "Martes Opción 1", "description": "Chicharron de pollo con papas y arroz", "precio": 11, "image": "martes1.png"},
            {"name": "Martes Opción 2", "description": "Ensalada rusa con milanesa", "precio": 11, "image": "martes2.png"}
        ],
        2: [  # Miércoles
            {"name": "Miércoles Opción 1", "description": "Arroz Chaufa con cecina", "precio": 11, "image": "miercoles1.png"},
            {"name": "Miércoles Opción 2", "description": "Macarrones con Pollo", "precio": 11, "image": "miercoles2.png"}
        ],
        3: [  # Jueves
            {"name": "Jueves Opción 1", "description": "Tallarines a la Bolognesa", "precio": 11, "image": "jueves1.png"},
            {"name": "Jueves Opción 2", "description": "Pachamanca a la Olla", "precio": 11, "image": "jueves2.png"}
        ],
        4: [  # Viernes
            {"name": "Viernes Opción 1", "description": "Tallarines verdes con pollo al horno y huancaina", "precio": 11, "image": "viernes1.png"},
            {"name": "Viernes Opción 2", "description": "Pure con lomo saltado", "precio": 11, "image": "viernes2.png"}
        ]
    }
# Obtener el día de la semana (0 = Lunes, 6 = Domingo)
lima = pytz.timezone('America/Lima')
dia_actual = datetime.now(lima).weekday()
# Si es fin de semana (5=Sábado, 6=Domingo), no hay servicio
# dia_actual = 2

# Ruta principal - Página de inicio
@app.route('/')
def home():
    return render_template('code.html')  # Muestra la página principal

# Ruta para reservar
@app.route('/reservar', methods=['GET', 'POST'])
def reservar():
    ahora = datetime.now(lima)
    hora_actual = ahora.hour
    minuto_actual = ahora.minute
    #hora_actual = 8  #Para testear en una hora fuera de rango

    # Verificar si está dentro del horario de reservas (6:00 AM - 11:30 AM)
    if hora_actual < 6 or hora_actual > 11 or (hora_actual == 11 and minuto_actual > 30):
        return render_template('reservar.html', menu_items=None,
                            mensaje="Lo sentimos, solo puede reservar de 6:00 AM a 11:30 AM")

    if dia_actual >= 5:
        return render_template('reservar.html', menu_items=None,
                             mensaje="Lo sentimos, solo atendemos de lunes a viernes.")
    # Obtener el menú del día actual
    menu_items = menus_semanales[dia_actual]
    return render_template('reservar.html', menu_items=menu_items)
@app.route('/menu')
def menu_semanal():
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    return render_template('menu.html', menus_semanales=menus_semanales, dias=dias)
# Ruta para procesar la reserva de un plato específico
@app.route('/hacer-reserva/<plato>', methods=['GET', 'POST'])
def hacer_reserva(plato):
    # Para sacar el nombre del plato
    for item in menus_semanales[dia_actual]:
        if item["name"] == plato:  
            plato_nombre = item["description"]
            break
    # Si el usuario envía el formulario (método POST)
    if request.method == 'POST':
        # Obtener los datos del formulario y eliminar espacios en blanco
        nombre = request.form.get('nombre', '').strip()
        correo = request.form.get('correo', '').strip()
        telefono = request.form.get('telefono', '').strip()
        puerta = request.form.get('puerta', '')
        horario = request.form.get('horario', '')
        # Validación simple
        if not nombre or not correo or not telefono:
            return render_template('formulario-reserva.html', plato=plato,
                                 error="Por favor, completa todos los campos")

        # Obtener la fecha y hora actual para la reserva
        fecha_hora = datetime.now(lima).strftime('%Y-%m-%d %H:%M:%S')
        # Nombre del archivo CSV donde se guardan las reservas
        archivo = 'reservas.csv'
        # Verificar si el archivo ya existe
        existe = os.path.isfile(archivo)

        # Abrir el archivo en modo "agregar" para no sobrescribir datos existentes
        with open(archivo, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Si es la primera reserva, crear la cabecera del CSV
            if not existe:
                writer.writerow(['Nombre', 'Correo', 'Teléfono', 'Plato', 'Fecha y Hora', 'Puerta', 'Horario'])
            # Agregar la nueva reserva al archivo
            writer.writerow([nombre, correo, telefono, plato_nombre, fecha_hora, puerta, horario])

        # Mostrar página de confirmación con los datos de la reserva
        return render_template('confirmacion.html', plato=plato, plato_nombre=plato_nombre, nombre=nombre,
                                correo=correo, telefono=telefono, fecha_hora=fecha_hora, puerta=puerta, horario=horario)

    # Si es una petición GET, mostrar el formulario de reserva
    return render_template('formulario-reserva.html', plato=plato, plato_nombre=plato_nombre)

# Ruta para manejar la selección de un plato (opcional, no se usa actualmente)
@app.route('/seleccionar/<plato>', methods=['POST'])
def seleccionar(plato):
    # Función simple que confirma la selección del plato
    return f'Has seleccionado: {plato}'

# Ruta para descargar el archivo de reservas (para administradores)
@app.route('/exportar-reservas')
def exportar_reservas():
    archivo = 'reservas.csv'
    # Verificar si existe el archivo de reservas
    if os.path.exists(archivo):
        # Enviar el archivo como descarga
        return send_file(archivo, as_attachment=True)
    # Si no hay reservas, mostrar mensaje con CSS
    return '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sin Reservas - Aquimenu</title>
        <link rel="stylesheet" href="/static/style.css">
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    </head>
    <body>
        <div class="csv-empty-state reservas">
            <div class="csv-empty-icon reservas">📋</div>
            <h2>Aún no hay reservas registradas</h2>
            <p>No se encontraron reservas para descargar. Los clientes podrán hacer reservas cuando estén disponibles.</p>
            <div class="csv-buttons-container">
                <a href="/admin" class="btn-volver-admin-csv">Volver al Panel Admin</a>
                <a href="/" class="btn-menu-principal-csv">Menú Principal</a>
            </div>
        </div>
    </body>
    </html>
    '''

# Ruta para el panel de administración
@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        # Verificar credenciales
        usuario = request.form.get('usuario', '').strip()
        password = request.form.get('password', '').strip()

        # Lista de usuarios autorizados y contraseña común
        USUARIOS_AUTORIZADOS = ['24200178', '24200183', '24200185', '24200152', '24200165']
        ADMIN_PASSWORD = 'aquimenu2025'

        if usuario in USUARIOS_AUTORIZADOS and password == ADMIN_PASSWORD:
            # Login exitoso, mostrar panel de admin
            return render_template('admin.html', admin_name=usuario)
        else:
            # Login fallido, mostrar error
            return render_template('admin-login.html', error="Usuario o contraseña incorrectos")

    # Si es GET, mostrar formulario de login
    return render_template('admin-login.html')

# Ruta para borrar todas las reservas (para administradores)
@app.route('/borrar-reservas')
def borrar_reservas():
    archivo = 'reservas.csv'
    # Verificar si existe el archivo
    if os.path.exists(archivo):
        # Eliminar el archivo de reservas
        os.remove(archivo)
        mensaje = "borrado"
    else:
        mensaje = "no_existe"
    # Volver al panel de admin con un mensaje de confirmación
    return render_template('admin.html', mensaje=mensaje)



@app.route('/escribir-resena/<nombre>/<correo>/<plato>')
def escribir_resena(nombre, correo, plato):
    """Formulario para escribir una reseña"""
    # Buscar el nombre descriptivo del plato
    plato_nombre = plato  # Por defecto usar el nombre del parámetro
    for dia_menus in menus_semanales.values():
        for item in dia_menus:
            if item["name"] == plato:
                plato_nombre = item["description"]
                break

    return render_template('formulario-resena.html', 
                         nombre=nombre, 
                         correo=correo, 
                         plato=plato,
                         plato_nombre=plato_nombre)


@app.route('/guardar-resena', methods=['POST'])
def guardar_resena():
    """Procesar y guardar la reseña enviada"""
    nombre = request.form.get('nombre', '').strip()
    correo = request.form.get('correo', '').strip()
    plato = request.form.get('plato', '').strip()
    calificacion = request.form.get('calificacion', '').strip()
    comentario = request.form.get('comentario', '').strip()

    # Validación
    if not all([nombre, correo, plato, calificacion, comentario]):
        return render_template('formulario-resena.html',
                             nombre=nombre,
                             correo=correo,
                             plato=plato,
                             error="Por favor, completa todos los campos")

    # Obtener fecha actual
    lima = pytz.timezone('America/Lima')
    fecha_resena = datetime.now(lima).strftime('%Y-%m-%d %H:%M:%S')

    # Archivo CSV para reseñas
    archivo_resenas = 'resenas.csv'
    existe = os.path.isfile(archivo_resenas)

    # Guardar la reseña
    with open(archivo_resenas, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow([
                'nombre', 'correo', 'plato', 'calificacion', 'comentario', 
                'fecha_resena', 'estado'
            ])
        writer.writerow([
            nombre, correo, plato, calificacion, comentario, 
            fecha_resena, 'pendiente'
        ])

    return render_template('resena-enviada.html', 
                         nombre=nombre,
                         calificacion=calificacion)


@app.route('/admin-resenas')
def admin_resenas():
    """Panel de administración de reseñas"""
    archivo_resenas = 'resenas.csv'
    resenas = []

    # Obtener filtros de la URL
    filtro_estado = request.args.get('estado', 'todas')
    filtro_calificacion = request.args.get('calificacion', 'todas')
    filtro_plato = request.args.get('plato', 'todos')

    if os.path.exists(archivo_resenas):
        with open(archivo_resenas, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):  # Agregar índice real
                # Aplicar filtros
                if filtro_estado != 'todas' and row.get('estado') != filtro_estado:
                    continue
                if filtro_calificacion != 'todas' and row.get('calificacion') != filtro_calificacion:
                    continue
                if filtro_plato != 'todos' and filtro_plato not in row.get('plato', ''):
                    continue

                row['indice_real'] = idx  # Guardar el índice real
                resenas.append(row)

    # Ordenar por fecha más reciente
    resenas.sort(key=lambda x: x.get('fecha_resena', ''), reverse=True)

    # Obtener lista única de platos para el filtro
    platos_unicos = set()
    if os.path.exists(archivo_resenas):
        with open(archivo_resenas, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                platos_unicos.add(row.get('plato', ''))

    return render_template('admin-resenas.html', 
                         resenas=resenas,
                         filtro_estado=filtro_estado,
                         filtro_calificacion=filtro_calificacion,
                         filtro_plato=filtro_plato,
                         platos_unicos=sorted(platos_unicos))


@app.route('/aprobar-resena/<int:indice>')
def aprobar_resena(indice):
    """Aprobar una reseña específica"""
    if cambiar_estado_resena_por_datos(indice, 'aprobada'):
        return redirect('/admin-resenas?estado=pendiente')  # Volver a pendientes
    return redirect('/admin-resenas')

@app.route('/rechazar-resena/<int:indice>')
def rechazar_resena(indice):
    """Rechazar una reseña específica"""
    if cambiar_estado_resena_por_datos(indice, 'rechazada'):
        return redirect('/admin-resenas?estado=pendiente')  # Volver a pendientes
    return redirect('/admin-resenas')

@app.route('/ocultar-resena/<int:indice>')
def ocultar_resena(indice):
    """Ocultar una reseña específica"""
    if cambiar_estado_resena_por_datos(indice, 'oculta'):
        return redirect('/admin-resenas')
    return redirect('/admin-resenas')

@app.route('/borrar-resena-individual/<int:indice>')
def borrar_resena_individual(indice):
    """Borrar una reseña específica"""
    archivo_resenas = 'resenas.csv'

    if not os.path.exists(archivo_resenas):
        return redirect('/admin-resenas')

    # Leer todas las reseñas
    resenas = []
    with open(archivo_resenas, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        resenas = list(reader)

    # Verificar que el índice sea válido y eliminar la reseña
    if 0 <= indice < len(resenas):
        resenas.pop(indice)

        # Reescribir el archivo sin la reseña eliminada
        with open(archivo_resenas, 'w', newline='', encoding='utf-8') as f:
            if resenas:
                fieldnames = ['nombre', 'correo', 'plato', 'calificacion', 'comentario', 'fecha_resena', 'estado']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(resenas)
            # Si no hay reseñas, el archivo queda vacío

    return redirect('/admin-resenas')


def cambiar_estado_resena_por_datos(indice, nuevo_estado):
    """Cambiar estado usando el índice real del archivo"""
    archivo_resenas = 'resenas.csv'

    if not os.path.exists(archivo_resenas):
        return False

    # Leer todas las reseñas sin filtros
    resenas = []
    with open(archivo_resenas, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        resenas = list(reader)

    # Verificar que el índice sea válido
    if 0 <= indice < len(resenas):
        resenas[indice]['estado'] = nuevo_estado

        # Reescribir el archivo
        with open(archivo_resenas, 'w', newline='', encoding='utf-8') as f:
            if resenas:
                fieldnames = ['nombre', 'correo', 'plato', 'calificacion', 'comentario', 'fecha_resena', 'estado']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(resenas)
        return True

    return False


@app.route('/borrar-resenas')
def borrar_resenas():
    """Borrar todas las reseñas"""
    archivo_resenas = 'resenas.csv'
    if os.path.exists(archivo_resenas):
        os.remove(archivo_resenas)
        mensaje = "resenas_borradas"
    else:
        mensaje = "no_existe_resenas"

    return render_template('admin.html', mensaje=mensaje)

@app.route('/exportar-resenas')
def exportar_resenas():
    """Descargar el archivo de reseñas CSV"""
    archivo = 'resenas.csv'
    if os.path.exists(archivo):
        return send_file(archivo, as_attachment=True, download_name='resenas_aquimenu.csv')
    return '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sin Reseñas - Aquimenu</title>
        <link rel="stylesheet" href="/static/style.css">
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    </head>
    <body>
        <div class="csv-empty-state resenas">
            <div class="csv-empty-icon resenas">⭐</div>
            <h2>Aún no hay reseñas registradas</h2>
            <p>No se encontraron reseñas para descargar. Los clientes podrán dejar reseñas después de realizar sus reservas.</p>
            <div class="csv-buttons-container">
                <a href="/admin" class="btn-volver-admin-csv">Volver al Panel Admin</a>
                <a href="/" class="btn-menu-principal-csv">Menú Principal</a>
            </div>
        </div>
    </body>
    </html>
    '''

# Ruta para mostrar las reseñas
def cargar_resenas():
    """Cargar todas las reseñas del archivo CSV"""
    archivo_resenas = 'resenas.csv'
    resenas = []

    if os.path.exists(archivo_resenas):
        with open(archivo_resenas, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            resenas = list(reader)

    return resenas

@app.route('/resenas')
def mostrar_resenas():
    resenas = cargar_resenas()
    # Excluir reseñas ocultas de la vista pública
    resenas_aprobadas = [r for r in resenas if r.get('estado') == 'aprobada']

    # Calcular estadísticas reales
    total_resenas = len(resenas_aprobadas)

    if total_resenas > 0:
        # Calcular calificación promedio
        suma_calificaciones = sum(int(r['calificacion']) for r in resenas_aprobadas)
        calificacion_promedio = round(suma_calificaciones / total_resenas, 1)

        # Calcular porcentaje de satisfacción (4-5 estrellas)
        resenas_satisfactorias = len([r for r in resenas_aprobadas if int(r['calificacion']) >= 4])
        porcentaje_satisfaccion = round((resenas_satisfactorias / total_resenas) * 100)
    else:
        calificacion_promedio = 0
        porcentaje_satisfaccion = 0

    return render_template('resenas.html', 
                         resenas=resenas_aprobadas,
                         total_resenas=total_resenas,
                         calificacion_promedio=calificacion_promedio,
                         porcentaje_satisfaccion=porcentaje_satisfaccion)



# Ruta para la página "Nosotros"
@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')


# Ejecutar la aplicación Flask
if __name__ == '__main__':
    # Obtener el puerto desde las variables de entorno o usar 3000 por defecto
    port = int(os.environ.get("PORT", 3000))
    # Iniciar el servidor Flask
    app.run(host="0.0.0.0", port=port, debug=True)
