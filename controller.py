from os import system
from getpass import getpass
from view import MenuView,Tabla,pedir_contrasena
from model import Cliente,Producto,Factura,Encriptador


def run():
    while True:
        menu_principal = MenuView({
            'Iniciar Sesion': ControladorPrincipal.inicio_sesion,
            'Registarse': ControladorPrincipal.registrarse,
            'Salir': exit
        })
        menu_principal.ejecutar_accion()


class ControladorPrincipal:
    @staticmethod
    def inicio_sesion():
        correo = input("Ingrese correo: ")
        contrasena = pedir_contrasena("Ingrese contraseña: ")

        cliente = Cliente.existe(correo,contrasena)

        if cliente == None:
            print("Usted no ha sido registrado")
        elif cliente == False:
            print("La contraseña es incorrecta")
        else:
            print("Acceso Correcto")
            while True:
                print()#espacio para orden
                controlador_cliente = ControladorCliente(cliente)
                menu = MenuView({
                    'Comprar':controlador_cliente.comprar,
                    'Cambiar correo':controlador_cliente.cambiar_correo,
                    'Cambiar Contraseña':controlador_cliente.cambiar_contrasena,
                    'Eliminar Cuenta':controlador_cliente.eliminar_cuenta
                },
                titulo=f"Bienvenido {cliente.nombre}")
                menu.ejecutar_accion()
            
                print()
                if input("Desea seguir? (s/n): ").strip() != 's':
                    break
    @staticmethod
    def registrarse():
        while True:
            nombres = input("Ingrese nombres completos: ")
            correo = input("Ingrese correo: ")
            contrasena = pedir_contrasena("Ingrese contraseña: ")
            contrasena2 = pedir_contrasena("Vuelva a escribir la contraseña: ")

            if contrasena == contrasena2:
                break
            print("Las contraseñas deben coincidir")

        Cliente.registrarse(nombres,correo,contrasena)


class ControladorCliente:
    def __init__(self,cliente):
        self.cliente = cliente

    def comprar(self):
        while True: 
            productos = Producto.obtener_productos()
            
            if len(productos) == 0:
                print("Aún no hay productos registrados")

            else:
                datos = {
                    'Codigo':[i.codigo for i in productos],
                    'nombre':[i.nombre for i in productos],
                    'precio':[i.precio for i in productos],
                    'stock':[i.stock for i in productos]}
                tabla = Tabla(datos)
                print()#espacios para la tabla
                tabla.mostrar_tabla()
                print()#espacios para la tabla
                codigo = tabla.elegir_opcion()
                if codigo:
                    decision_carrito = input("Desea eliminar o agregar al carrito?(e / a): ").strip()
                    producto = Producto.obtener_producto(productos,codigo)
                    if decision_carrito == 'a':
                        self.cliente.agregar_producto(producto)
                    elif decision_carrito == 'e':
                        self.cliente.eliminar_producto(producto)
                    else:
                        print("solo ingrese (a) o (e)")
                    
                    elegir = input("Desea volver a elegir otro producto?(s/n): ").strip()
                    if elegir != 's':
                        break    

        if self.cliente.carrito:
            print()#diseno
            print(f"{self.cliente.nombre} los productos que elegiste son:")
            tabla = Tabla({
                'Codigo':[i.codigo for i in self.cliente.carrito],
                'nombre':[i.nombre for i in self.cliente.carrito],
                'precio':[i.precio for i in self.cliente.carrito],
                'stock':[i.stock for i in self.cliente.carrito]
            })
            print()#diseno
            tabla.mostrar_tabla()
            print()#diseno
            confirmacion = input("Confirmar(co) o Cancelar el pedido(presione enter): ").strip()

            if confirmacion == "co":
                Factura.registrar_factura(self.cliente.id_cliente,self.cliente.carrito)
            else:
                print("Compra cancelada")

    def cambiar_correo(self):
        contrasena = pedir_contrasena("Ingrese contraseña para la confirmacion (Enter para cancelar): ").strip()

        if Encriptador().comparar(self.cliente.contrasena,contrasena):
            correo = input("Ingrese nuevo correo: ")
            if correo == self.cliente.correo:
                print("Se tiene que ingresar un correo diferente al anterior")
            else:
                self.cliente.correo = correo
                print("El correo se ha cambiado correctamente")
        else:
            print("Contraseña incorrecta")

    def cambiar_contrasena(self):
        contrasena = pedir_contrasena("Ingrese contraseña para la confirmacion (Enter para cancelar): ").strip()

        if Encriptador().comparar(self.cliente.contrasena,contrasena):
            nueva_contrasena = pedir_contrasena("Ingrese nueva contraseña: ")
            if Encriptador().comparar(self.cliente.contrasena,nueva_contrasena):
                print("Se tiene que ingresar un correo diferente al anterior")
            else:
                self.cliente.contrasena = nueva_contrasena
                print("La contraseña se ha cambiado correctamente")
        else:
            print("Contraseña incorrecta")

    def eliminar_cuenta(self):
        print("su solicitud de eliminacion ha sido enviada.")
