from flask import Flask, render_template
from flask import Flask, Blueprint
from flask import redirect, url_for
from flask import request, session,jsonify
import requests

from api.API_Contenidos.swagger_server.controllers import peliculas_controller, series_controller
from api.API_Usuarios.swagger_server.controllers import usuarios_controller



from api.API_Usuarios import dbconnection_usuarios

app = Flask(__name__)
app.secret_key = 'SECRETA'
app.config['SESSION_TYPE'] = 'filesystem' 


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



if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
