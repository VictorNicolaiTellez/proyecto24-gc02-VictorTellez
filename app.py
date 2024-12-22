from flask import Flask, render_template
from flask import Flask, Blueprint
from flask import redirect, url_for
from flask import request, session,jsonify
import requests

from API_Contenidos.swagger_server import contenidos_blueprint
from API_Contenidos.swagger_server.controllers import peliculas_controller, series_controller
from API_Usuario.swagger_server.controllers import usuarios_controller
from API_Visualizaciones.swagger_server import visualizaciones_blueprint

from API_Contenidos import dbconnection_contenidos
from API_Usuario import dbconnection_usuarios
from API_Visualizaciones import dbconnection_visualizaciones

app = Flask(__name__)
app.secret_key = 'SECRETA'
app.config['SESSION_TYPE'] = 'filesystem' 

# Registrar cada API con un prefijo de URL
app.register_blueprint(contenidos_blueprint, url_prefix='/api/contenidos')
app.register_blueprint(visualizaciones_blueprint, url_prefix='/api/visualizaciones')
 
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    # Obtener datos del formulario
    email = request.form.get('email')
    password = request.form.get('password')

    # Validar las credenciales usando la base de datos
    id_usuario = dbconnection_usuarios.dbLogIn(email, password)  # Función personalizada que valida en la BD
    if id_usuario is None :
        return render_template('login.html', error_message="Usuario no Existente")
    usuario = usuarios_controller.usuarios_id_get(id_usuario)
    if usuario is None :
        return render_template('login.html', error_message="Usuario no Existente")
    
    try:
        session['id'] = usuario.get('id')
        session['nombre'] = usuario.get('nombre')
        session['apellidos'] = usuario.get('apellidos')
        session['email'] = usuario.get('correo')
        session['password'] = usuario.get('contrasea')
        session['imagen_perfil'] = usuario.get('imagen_perfil')
        session['metodo_pago'] = usuario.get('metodo_pago')
        session['idioma'] = usuario.get('idioma')
        session['genero_favorito'] = usuario.get('genero_favorito')

        # Redirigir al home tras un login exitoso
        return redirect(url_for('home'))
    except KeyError as e:
        print(f"Error al establecer la sesión: clave faltante en 'usuario': {e}")
        return render_template('login.html', error_message="Error interno al iniciar sesión. Inténtalo más tarde.")
    except Exception as e:
        print(f"Error inesperado: {e}")
        return render_template('login.html', error_message="Error interno al iniciar sesión. Inténtalo más tarde.")
    
@app.route('/registro_post/', methods=['POST'])
def registro_post():
    nombre = request.form.get('nombre')
    apellidos=request.form.get('apellidos')
    correo=request.form.get('email')
    password1=request.form.get('password')
    password2=request.form.get('confirm-password')
    
    if password1 == password2:
        body = {
            "firstname": nombre,
            "secondname": apellidos,
            "correo": correo,
            "password1": password1,
            "password2": password2
            }
    else:
        return redirect(url_for('registro'))
    
    try:
            response = usuarios_controller.usuarios_post(body)
            return redirect(url_for('index')) 
    except Exception as e:
            return redirect(url_for('registro')) 
      
    
@app.route('/registro/', methods=['GET'])
def registro():
    return render_template('registro.html')


@app.route('/home/') #Al hacer python app.py hay que poner en la ruta /Inicio
def home():
    if 'id' not in session:
        return redirect(url_for('index'))  # Redirigir al login si no está autenticado
    return render_template('principal.html')

@app.route('/series/')
def series():
    data = request.form
    nombreserie = data.get('query', type=str)
    if request.method=='GET':
        series = series_controller.series_titulo_titulo_get("")
    if request.method=='POST':
        series = series_controller.series_titulo_titulo_get(nombreserie)
    return render_template('series.html', series=series)  # Página de series

@app.route('/peliculas/', methods=['GET', 'POST'])
def peliculas():
    data = request.form
    nombrepelicula = data.get('query', type=str)
    if request.method=='GET':
        peliculas = peliculas_controller.peliculas_titulo_titulo_get("")
    if request.method=='POST':
        peliculas = peliculas_controller.peliculas_titulo_titulo_get(nombrepelicula)
    return render_template('peliculas.html', peliculas=peliculas)  # Página de películas

@app.route('/mi_lista/')
def mi_lista():
    peliculas_id = dbconnection_visualizaciones.dbGetMovieHistory(1)
    peliculas = []
    for x in peliculas_id:
        print(x)
        peliculas.append(peliculas_controller.peliculas_id_get(x[0]))

    return render_template('miLista.html', peliculas=peliculas)  # Página de "Mi lista"

@app.route('/search/')
def search():
    return render_template('search.html')  # Página de "Busqueda"

@app.route('/contenido/pelicula/<movie_id>', methods=['GET', 'POST'])
def search_content_movie(movie_id):
    print('ID DE LA PELICULA QUE SE VA A MOSTRAR: ', movie_id)
    if request.method=='GET':
        info = peliculas_controller.peliculas_id_get(movie_id)
    if request.method=='POST':
        info = None

    return render_template('content-detail.html', contenidos=info)  # Página de "Busqueda"

@app.route('/contenido/serie/<serie_id>', methods=['GET', 'POST'])
def search_content_serie(serie_id):
    print('ID DE LA SERIE QUE SE VA A MOSTRAR: ', serie_id)
    info = series_controller.series_id_get(serie_id)
    if request.method=='GET':
        season = 2
    if request.method=='POST':
        season = request.form.get('temporada')
    
    print('TEMPORADA DE LA SERIE: ', int(season))
    
    return render_template('content-detail.html', contenidos=info, season=season - 1)  # Página de "Busqueda"

@app.route('/search_result/', methods=['GET', 'POST'])
def search_result():
    if request.method == 'POST':
        # Obtén el término de búsqueda desde el formulario
        termino_busqueda = request.form.get('query', '').strip()

        # Aquí podrías realizar una búsqueda en la base de datos o lógica personalizada
        # Por ahora, simplemente muestra el término buscado
        resultados = f"Resultados para: {termino_busqueda}"
        
        #Pueba ejemplo lista(cambiar por BD)
        peliculas = peliculas_controller.peliculas_titulo_titulo_get(termino_busqueda)
        series = series_controller.series_titulo_titulo_get(termino_busqueda)
        
        # Renderiza una página con los resultados
        return render_template('search.html', peliculas=peliculas, series=series)
        #return render_template('search.html', termino=termino_busqueda, resultados=resultados)
    
    # Si es GET, muestra la página inicial de búsqueda
    return render_template('search.html')
   

@app.route('/perfil/')
def perfil():
    if 'id' not in session:
        return redirect(url_for('login'))  # Redirige al login si no hay sesión activa

    # Extrae los datos desde la sesión
    user_data = {
        "nombre": session['nombre'],
        "apellidos": session['apellidos'],
        "email": session['email'],
        "genero_favorito": session['genero_favorito']
    }
    
    return render_template('user-profile.html', user_data=user_data)

@app.route('/edit_perfil/', methods=['GET', 'POST'])
def edit_perfil():
    if request.method == 'GET':
        id_usuario = session['id']
        nombre = session['nombre']
        apellidos = session['apellidos']
        email = session['email']
        password = session['password']
        genero_favorito = session['genero_favorito']
        
        return render_template('edit-profile.html', id_usuario=id_usuario,
                               nombre=nombre,apellidos=apellidos,
                               email=email,
                               genero_favorito=genero_favorito)
        
    if request.method == 'POST':
        # Aquí procesas los datos del formulario solo si se hizo clic en "Guardar"
        new_name = request.form['nombre']
        new_secondname = request.form['apellidos']
        new_email = request.form['email']
        new_password = request.form['password1']
        new_password2 = request.form['password2']
        new_genero = request.form.get('genero_favorito', None)
        
        if new_password != new_password2:
            error_message = "Las contraseñas no coinciden. Por favor, intente de nuevo."
            return render_template('edit_profile.html', 
                                   nombre=session['nombre'], 
                                   apellidos=session['apellidos'],
                                   email=session['email'] ,
                                   genero_favorito=session['genero_favorito'],
                                   error_message=error_message)
            
        if 'guardar' in request.form:
            try:
                if new_name != session['nombre'] or new_secondname!=session['apellidos']:
                    # Llamar al controlador para actualizar el nombre
                    bodyname = {
                        "nombre": new_name,
                        "apellidos": new_secondname
                    }
                    print(f"Llamando a usuarios_id_put con: {bodyname}, ID: {session['id']}")
                    usuarios_controller.usuarios_id_put(bodyname, session['id'])
                    print(f"Exitosa")
                    
                    session['nombre'] = new_name  # Actualizamos la sesión con el nuevo nombre
                    session['apellidos'] = new_secondname

                if new_email != session['email']:
                    # Llamar al controlador para actualizar el email
                    bodycorreo = {
                        "correo": new_email
                    }
                    usuarios_controller.usuarios_id_correo_put(bodycorreo, session['id'])
                    session['email'] = new_email  # Actualizamos la sesión con el nuevo email

                if new_password != '' and new_password != session['password']:
                    # Si la contraseña cambia, llamamos al controlador para actualizarla
                    bodypassword = {
                        "contrasea": new_password
                    }
                    usuarios_controller.usuarios_id_contrasea_put(bodypassword, session['id'])
                    session['password'] = new_password  # Actualizamos la sesión con la nueva contraseña

                if new_genero != session['genero_favorito']:
                    # Llamar al controlador para actualizar el género favorito
                    bodygenero = {
                        "genero_favorito": new_genero
                    }
                    usuarios_controller.usuarios_id_genero_favorito_put(bodygenero,session['id'])
                    session['genero_favorito'] = new_genero  # Actualizamos la sesión con el nuevo género

                # Redirigir a la página de perfil con los datos actualizados
                return redirect(url_for('perfil'))
        
            except Exception as e:
            # Si ocurre un error, podemos mostrar un mensaje de error
                error_message = f"Hubo un error al actualizar los datos: {str(e)}"
                return render_template('edit-profile.html', 
                                    nombre=session['nombre'],
                                    apellidos=session['apellidos'], 
                                    email=session['email'],
                                    genero_favorito=session['genero_favorito'],
                                    error_message=error_message)
        
        # Redirige al perfil después de guardar o cancelar
        return redirect(url_for('perfil'))

@app.route('/remove_user/', methods=['POST'])
def remove_user():
    # Verificar si el usuario está autenticado
    if 'id' not in session:
        return redirect(url_for('login'))  # Redirige a la página de login si no está autenticado

    try:
        # Llamada a la función para eliminar el usuario de la base de datos
        
        resultado = usuarios_controller.usuarios_id_delete(session['id'])

        if  resultado:
            session.clear()  # Limpia la sesión después de eliminar la cuenta
            return redirect(url_for('index'))  # Redirige al índice después de eliminar
        else:
            return "Error al eliminar el usuario", 500  # Código de error
    except Exception as e:
        print("Error al eliminar el usuario:", e)
        return "Error interno del servidor", 500

@app.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)