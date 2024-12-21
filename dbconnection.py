import oracledb as db


from api.API_Usuarios.swagger_server.models.usuario import Usuario


def dbConectar():
    ip = "host.docker.internal"
    puerto = 1521
    s_id = "xe"

    usuario = "system"
    contrasena = "12345"
    dsn = db.makedsn(ip, puerto, s_id)

    print("---dbConectar---")
    print("---Conectando a Oracle---")

    try:
        conexion = db.connect(user=usuario, password=contrasena, host=ip, port=puerto, sid=s_id)
        print("Conexión realizada a la base de datos",conexion)
        return conexion
    except db.DatabaseError as error:
        print("Error en la conexión")
        print(error)
        return None

def dbSignUp(email=str, firstName=str, secondName=str, password1=str, password2=str):
    print("---dbSignUp---")
    
    try:
        cursor = conexion.cursor()
        print(email)
        print(firstName)
        print(secondName)
        print(password1)
        print(password2)
        consulta = "INSERT INTO asee_users (email, firstname, secondname, passwd) VALUES(:email, :firstName, :secondName, :password1)"
        if(password1 == password2):
            cursor.execute(consulta, [email, firstName, secondName, password1])
            print("Tupla insertada correctamente")
            print('------------------------------')
            cursor.close()
            conexion.commit()
            return True
        else:
            print("Error: Las contraseñas no coinciden")
            cursor.close()
            return False
    except db.DatabaseError as error:
        print("Error. No se ha podido crear el usuario")
        print(error)
        return False

def dbLogIn(email=str, password=str):
    print("---dbLogIn---")

    try:
        cursor = conexion.cursor()
        print(email)
        print(password)
        consulta = "SELECT user_id,email, passwd FROM asee_users WHERE email = :email AND passwd = :password"
        cursor.execute(consulta, [email, password])
        resul = cursor.fetchone()
        if(cursor.rowcount == 1):
            print("Usuario encontrado correctamente")
            if(resul[2] == password):
                print('Usuario y contraseña correctos')
            else:
                print('La contraseña no es correcta')
                return False
        else:
            print("Usuario no existente:",cursor.rowcount)
            return False
        print('------------------------------')
        
        cursor.close()
        conexion.commit()
        if resul[0] is None:
            return None
        else:
            return resul[0]
       
    except db.DatabaseError as error:
        print("Error. No se ha podido iniciar sesión")
        print(error)
        return False

def dbPrint():
    try:
        cursor = conexion.cursor()
        consulta = "SELECT * FROM asee_users"
        cursor.execute(consulta)
        for tupla in cursor:
            print(tupla)
        print("Total usuarios:", cursor.rowcount)
        cursor.close()
    except db.DatabaseError as error:
        print("Error: No hay nada")

def dbGetUser(id):
    print("---dbGetUser---")

    try:
        cursor = conexion.cursor()
        consulta = "SELECT * FROM asee_users WHERE user_id = :id"
        cursor.execute(consulta, [id])
        tupla = cursor.fetchone()
        print(tupla)
        imagen = "imagen.jpg"
        mpago = "Paypal"
        idioma = "Español"
        
        if tupla is None:
            return None

        usuario = Usuario(tupla[0], tupla[2], tupla[3], tupla[1],tupla[4], imagen, mpago, idioma, tupla[5])
        cursor.close()
        return usuario.to_dict()
    except db.DatabaseError as error:
        print("Error: No se puede obtener el usuario")
        print(error)

def dbModifyUserName(id, nombre,apellidos):
    print("---dbModifyUserName---")
    try:
        cursor = conexion.cursor()
        print(nombre, apellidos)
        consulta = "UPDATE asee_users SET firstname = :nombre, secondname =:apellidos WHERE user_id = :id"
        cursor.execute(consulta, [nombre, apellidos, id])
        
        if cursor.rowcount == 1:
            print("Nombre del usuario ", id, " modificado. Nuevo nombre: ", nombre)
            respuesta = True
        else:
            print("No se ha podido modificar el nombre del usuario")
            respuesta = False
        
        cursor.close()
        conexion.commit()
        return respuesta
    except db.DatabaseError as error:
        print("Error: No se ha podido cambiar el nombre del usuario")
        print(error)
        return False

def dbModifyFavGenre(id, genero):
    print("---dbModifyFavGenre---")
    try:
        cursor = conexion.cursor()
        consulta = "UPDATE asee_users SET fav_genre = :genero WHERE user_id = :id"
        cursor.execute(consulta, [genero, id])
        
        if cursor.rowcount == 1:
            print("Genero favorito del usuario ", id, " modificado. Nuevo genero favorito: ", genero)
            respuesta = True
        else:
            print("No se ha podido modificar el genero favorito del usuario")
            respuesta = False
        
        cursor.close()
        conexion.commit()
        return respuesta
    except db.DatabaseError as error:
        print("Error: No se ha podido cambiar el genero favorito del usuario")
        print(error)
        return False

def dbModifylEmail(id, email):
    print("---dbModifylEmail---")
    try:
        cursor = conexion.cursor()
        consulta = "UPDATE asee_users SET email = :email WHERE user_id = :id"
        cursor.execute(consulta, [email, id])
        
        if cursor.rowcount == 1:
            print("Email del usuario ", id, " modificado. Nuevo email: ", email)
            respuesta = True
        else:
            print("No se ha podido modificar el email favorito del usuario")
            respuesta = False
        
        cursor.close()
        conexion.commit()
        return respuesta
    except db.DatabaseError as error:
        print("Error: No se ha podido cambiar el email del usuario")
        print(error)
        return False

def dbModifyPassword(id, password):
    print("---dbModifyPassword---")
    try:
        cursor = conexion.cursor()
        consulta = "UPDATE asee_users SET passwd = :password WHERE user_id = :id"
        cursor.execute(consulta, [password, id])
        
        if cursor.rowcount == 1:
            print("Contraseña del usuario ", id, " modificada. Nueva contraseña: ", password)
            respuesta = True
        else:
            print("No se ha podido modificar la contarseña del usuario")
            respuesta = False
        
        cursor.close()
        conexion.commit()
        return respuesta
    except db.DatabaseError as error:
        print("Error: No se ha podido cambiar la contraseña del usuario")
        print(error)
        return False

    try:
        cursor = conexion.cursor()
        consulta = "SELECT movie FROM asee_user_movie WHERE user_id = :user_id"
        cursor.execute(consulta, [user_id,])
        peliculas = []
        for tupla in cursor:
            peliculas.append(tupla)
        return peliculas
    except db.DatabaseError as error:
        print("Error. No se han podido actualizar las visualizaciones de usuario")
        print(error)
        return False



conexion = dbConectar()