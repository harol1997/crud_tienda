from os import startfile
from psycopg2 import connect
from werkzeug.security import check_password_hash,generate_password_hash
from time import strftime

class Conector:

    def __init__(
            self,nombre_base="tienda",
            usuario="postgres",
            contrasena="passwordpost_97"):
        self.nombre_base = nombre_base
        self.usuario = usuario
        self.contrasena = contrasena

    def __conectar(self):
        conexion = connect(
            dbname=self.nombre_base,
            user = self.usuario,
            password = self.contrasena
            )
        cursor = conexion.cursor()
        return conexion,cursor

    def __cerrar_conexion(self,conexion,cursor):
        cursor.close()
        conexion.close()
    
    def insertar(self,tabla,campos,valores):
        """
            tabla(str): nombre de la tabla\n
            campos(str): nombre de los campos donde se insertara los valores separados por comas (,)\n
            valores(tuple): tupla de los valores a insertar 
        """
        conexion,cursor = self.__conectar()
        instruccion = f"""
        insert into {tabla}({campos})
        values({('%s,'*len(valores))[:-1]})"""
        
        cursor.execute(instruccion,valores)
        conexion.commit()
        self.__cerrar_conexion(conexion,cursor)
        print("Se insertaron los datos correctamente")

    def actualizar(self,tabla,campos,donde,valores):
        """
            tabla(str): nombre de la tabla
            campos(str): nombre de los campos donde se insertara los valores separados por comas (,)
            donde(str):  condicion de la consulta
            valores(tuple): tupla de los valores a que reemplazan a %s
        """
        conexion,cursor = self.__conectar()
        instruccion = f"""update {tabla}
        set {campos}
        where {donde}"""
        cursor.execute(instruccion,valores)
        conexion.commit()
        self.__cerrar_conexion(conexion,cursor)
        print("Se actualizaron los datos correctamente")

    def eliminar(self,tabla,condicion,valores):
        """
            tabla(str):nombre de la tabla
            condicion(str):nombre del campo o campos a evaluar con =%s
        """
        conexion,cursor = self.__conectar()
        instruccion = f"""delete from {tabla}
        where {condicion}"""
        cursor.execute(instruccion,valores)
        self.__cerrar_conexion()
        print("Se eliminaron los datos correctamente")

    def seleccionar(self,campos,tabla,condicion="",valores=(),todo=False):
        """
            campos(str):nombre de los campos a seleccionar separados por comas (,)
            tabla(str): nombre de la tabla
            condicion(str):opcional.Si desea especificar la busqueda
            valores(str):opcion. valores a analizar en la condicion
            todo(bool): si desea obtener todos los datos encontrados, por defecto es False

            return(None o tupla): si todo = False
            return(Lista): si todo =True
        """
        conexion,cursor = self.__conectar()
        instruccion = f"""select {campos} from {tabla}"""
        if condicion != "":
            instruccion += f"""
            where {condicion}"""
            cursor.execute(instruccion,valores)
        else:
            cursor.execute(instruccion)

        if todo:
            datos = cursor.fetchall()
        else:
            datos = cursor.fetchone() 

        self.__cerrar_conexion(conexion,cursor)

        return datos

class Producto:
    
    def __init__(self,codigo,nombre,precio,stock):
        self.__codigo = codigo
        self.__nombre = nombre
        self.__precio = precio
        self.__stock = stock

    def __eq__(self, producto):
        return self.__codigo == producto.codigo

    @property
    def codigo(self):
        return self.__codigo

    @property
    def nombre(self):
        return self.__nombre

    @property
    def precio(self):
        return self.__precio

    @property
    def stock(self):
        return self.__stock
    

    @staticmethod
    def registrar_producto(nombre,precio,cantidad):
        pass 

    @staticmethod
    def obtener_producto(lista_productos,codigo):
        for i in lista_productos:
            if codigo == i.codigo:
                return i
        

    @staticmethod
    def obtener_productos():
        conector = Conector()
        productos = conector.seleccionar('id,nombre,precio,cantidad','producto',todo=True)
        if len(productos) != 0:
            productos = [Producto(i[0],i[1],i[2],i[3]) for i in productos]
        return productos

class Cliente:
    
    def __init__(self,id_cliente,nombre,correo,contrasena):
        self.__id_cliente = id_cliente
        self.__nombre = nombre
        self.__correo = correo
        self.__contrasena = contrasena
        self.__carrito = list()
        self.conector = Conector()


    def agregar_producto(self,producto):
        if producto in self.__carrito:
            print("El producto ya se encuentra en el carrito")
        else:
            self.__carrito.append(producto)
            print(f"El producto {producto.nombre} se ha agregado al carrito")
    
    def eliminar_producto(self,producto):
        if producto in self.__carrito:
            self.__carrito.remove(producto)
            print(f"El producto {producto.nombre} ha sido removido del carrito")
        else:
            print("El producto no se encuentra en el carrito")

    @property
    def correo(self):
        return self.__correo
    
    @correo.setter
    def correo(self,correo):
        self.conector.actualizar(
            "cliente",
            "correo=%s",
            "correo=%s",
            (correo,self.__correo))
        self.__correo = correo
    
    @property
    def contrasena(self):
        return self.__contrasena

    @contrasena.setter
    def contrasena(self,contrasena):
        contrasena_encriptada = generate_password_hash(contrasena,'sha256')

        self.conector.actualizar(
            "cliente",
            "contrasena=%s",
            "correo=%s",
            (contrasena_encriptada,self.__correo)
            )
        self.__contrasena = contrasena_encriptada
        

    @property
    def id_cliente(self):
        return self.__id_cliente
    
    @property
    def nombre(self):
        return self.__nombre

    @property
    def carrito(self):
        return self.__carrito

    @staticmethod
    def registrarse(nombres,correo,contrasena):
        contrasena_encriptada = Encriptador().encriptar(contrasena)

        conector = Conector()

        if conector.seleccionar('id','cliente','correo=%s',(correo,)):
            print("El usuario ya ha sido registrado")
        else:
            conector.insertar(
                'cliente',
                'nombres,correo,contrasena',
                (nombres,correo,contrasena_encriptada)
                )

    @staticmethod
    def existe(correo,contrasena):
        """
            correo(str): correo del cliente
            contrasena(str): contraseña del cliente

            return: 
                None -> si no existe el usuario
                False -> si existe pero la contraseña es incorrecta
                objeto Cliente -> si existe y la contraseña es correcta
        """
        conector = Conector()
        datos = conector.seleccionar(
            'id,nombres,correo,contrasena',
            'cliente',
            'correo=%s',
            (correo,))
        
        if datos is not None:
            if Encriptador().comparar(datos[-1],contrasena):
                datos = Cliente(datos[0],datos[1],datos[2],datos[3])
            else:
                datos = False
        return datos

class Factura:
    @staticmethod
    def registrar_factura(id_cliente,carrito):
        fecha = strftime("%d/%m/%y")
        conector = Conector()
        conector.insertar(
            "factura",
            "id_cliente,fecha",
            (id_cliente,fecha))
        codigo_factura = len(conector.seleccionar("*","factura",todo=True))
        for i in carrito:
            conector.insertar(
                "factura_producto",
                "id_factura,id_producto",
                (codigo_factura,i.codigo)
                )
        print(f"el codigo de su factura es: {codigo_factura}")

    @staticmethod
    def ver_facturas(correo):
        conector = Conector()
        datos = conector.seleccionar(
            "id",
            "cliente",
            "correo=%s",
            (correo,)
            )
        if datos:
            id_cliente = datos[0]
            datos_factura = conector.seleccionar(
                "id,fecha",
                "factura",
                "id_cliente=%s",
                (id_cliente,),
                todo=True
                )#todas las facturas relacionadas al cliente
            if datos_factura:
                datos_producto = list()
                for i in datos_factura:#i[0] --> codigo de factura
                    id_producto = conector.seleccionar(
                        "id_producto",
                        "factura_producto",
                        "id_factura=%s",
                        (i[0],),
                        todo = True
                        )#lista de listas de los id de los productos
                    for i in id_producto:#i[0] --> id del producto
                        producto = conector.seleccionar(
                            "nombre,precio"
                            ,"producto"
                            ,"id=%s"
                            ,(i,)
                            )
                        datos_producto.append(producto)
                return datos_factura,datos_producto
            else:
                datos_factura
        else:
            return datos


class Encriptador:

    def encriptar(self,argumento):
        return generate_password_hash(argumento,'sha256')

    def comparar(self,argumento_encriptado,argumento):
        return check_password_hash(argumento_encriptado,argumento)

