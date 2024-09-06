import mysql.connector
from mysql.connector import Error
import datetime
from prettytable import PrettyTable


class App:
    def __init__(self):
        # Conectar a la base de datos
        self.conn = self.create_connection()
        if self.conn is None:
            print("No se pudo conectar a la base de datos. Verifica tus credenciales.")
            return

        self.cursor = self.conn.cursor()
        self.create_tables()

        self.current_user_id = None
        self.show_tables()  # Mostrar tablas al iniciar
        self.run()

    def create_connection(self):
        try:
            connection = mysql.connector.connect(
                host='127.0.0.1',
                port='3306',
                database='app_plastico',  # Cambia a 'heidy' si deseas usar esa base de datos
                user='root',
            )
            if connection.is_connected():
                print("Conexión a la base de datos MariaDB exitosa")
                return connection
        except mysql.connector.Error as e:
            print(f"Error al conectar a MariaDB: {e}")
        return None

    def create_tables(self):
        create_users_table_query = '''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
        '''
        create_consumo_table_query = '''
        CREATE TABLE IF NOT EXISTS consumo (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            fecha DATE,
            cantidad DECIMAL(10, 2),
            descripcion TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        '''
        create_sugerencias_table_query = '''
        CREATE TABLE IF NOT EXISTS sugerencias (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            recomendacion TEXT,
            fecha DATE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        '''
        create_metas_table_query = '''
        CREATE TABLE IF NOT EXISTS metas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            meta TEXT,
            fecha_inicio DATE,
            fecha_fin DATE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        '''
        create_historial_table_query = '''
        CREATE TABLE IF NOT EXISTS historial (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            accion TEXT,
            fecha DATE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        '''
        try:
            self.cursor.execute(create_users_table_query)
            self.cursor.execute(create_consumo_table_query)
            self.cursor.execute(create_sugerencias_table_query)
            self.cursor.execute(create_metas_table_query)
            self.cursor.execute(create_historial_table_query)
            self.conn.commit()
        except mysql.connector.Error as e:
            print(f"Error al crear las tablas: {e}")

    def show_tables(self):
        try:
            self.cursor.execute("SHOW TABLES")
            tables = self.cursor.fetchall()
            print("\n--- Tablas en la base de datos ---")
            for table in tables:
                table_name = table[0]
                print(f"\nTabla: {table_name}")
                self.display_table_data(table_name)
        except mysql.connector.Error as e:
            print(f"Error al obtener las tablas: {e}")

    def display_table_data(self, table_name):
        try:
            self.cursor.execute(f"DESCRIBE {table_name}")
            columns = self.cursor.fetchall()
            column_names = [column[0] for column in columns]

            self.cursor.execute(f"SELECT * FROM {table_name}")
            rows = self.cursor.fetchall()

            table = PrettyTable()
            table.field_names = column_names
            for row in rows:
                table.add_row(row)

            print(table)
        except mysql.connector.Error as e:
            print(f"Error al mostrar los datos de la tabla {table_name}: {e}")

    def run(self):
        while True:
            print("\n--- Aplicación de Gestión de Plásticos ---")
            print("1. Registrarse")
            print("2. Iniciar sesión")
            print("3. Recuperar contraseña")
            print("4. Salir")

            choice = input("Seleccione una opción: ")

            if choice == '1':
                self.register_user()
            elif choice == '2':
                self.login_user()
            elif choice == '3':
                self.recover_password()
            elif choice == '4':
                print("Saliendo...")
                break
            else:
                print("Opción no válida. Inténtelo de nuevo.")

    def register_user(self):
        name = input("Nombre: ")
        email = input("Correo Electrónico: ")
        password = input("Contraseña: ")

        if name and email and password:
            try:
                self.cursor.execute('INSERT INTO users (name, email, password) VALUES (%s, %s, %s)',
                                    (name, email, password))
                self.conn.commit()
                print("Registro exitoso")
            except mysql.connector.IntegrityError:
                print("El correo electrónico ya está registrado")
            except mysql.connector.Error as e:
                print(f"Error en el registro: {e}")
        else:
            print("Todos los campos deben ser completados")

    def login_user(self):
        email = input("Correo Electrónico: ")
        password = input("Contraseña: ")

        if email and password:
            self.cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
            user = self.cursor.fetchone()
            if user:
                self.current_user_id = user[0]  # Guarda el ID del usuario actual
                self.record_action("Inicio de sesión")
                print("Inicio de sesión exitoso")
                self.show_main_screen()
            else:
                print("Credenciales incorrectas")
        else:
            print("Todos los campos deben ser completados")

    def recover_password(self):
        email = input("Correo Electrónico: ")

        if email:
            # Aquí se debería agregar la lógica para enviar el enlace de recuperación
            print("Enlace de recuperación enviado")
        else:
            print("El campo de correo electrónico debe ser completado")

    def generate_recommendations(self):
        self.cursor.execute('SELECT fecha, cantidad, descripcion FROM consumo WHERE user_id = %s',
                            (self.current_user_id,))
        consumos = self.cursor.fetchall()

        if not consumos:
            return ["No se encontraron datos de consumo para generar recomendaciones."]

        recommendations = []
        for consumo in consumos:
            fecha, cantidad, descripcion = consumo
            recommendations.append(f"Considera reducir tu consumo de {descripcion} si es mayor a {cantidad}.")

        # Guardar las recomendaciones en la base de datos
        today = datetime.date.today()
        for rec in recommendations:
            self.cursor.execute('INSERT INTO sugerencias (user_id, recomendacion, fecha) VALUES (%s, %s, %s)',
                                (self.current_user_id, rec, today))
        self.conn.commit()

        return recommendations

    def show_main_screen(self):
        while True:
            print("\n--- Pantalla Principal ---")
            print("1. Registrar Consumo")
            print("2. Ver Historial")
            print("3. Sugerir Alternativas")
            print("4. Gestionar Metas")
            print("5. Cerrar sesión")

            choice = input("Seleccione una opción: ")

            if choice == '1':
                self.show_consumo_screen()
            elif choice == '2':
                self.show_historial_screen()
            elif choice == '3':
                self.show_sugerencias_screen()
            elif choice == '4':
                self.show_metas_screen()
            elif choice == '5':
                self.current_user_id = None
                print("Sesión cerrada")
                break
            else:
                print("Opción no válida. Inténtelo de nuevo.")

    def show_consumo_screen(self):
        fecha = input("Fecha (YYYY-MM-DD): ")
        cantidad = input("Cantidad: ")
        descripcion = input("Descripción: ")

        if fecha and cantidad and descripcion:
            try:
                self.cursor.execute(
                    'INSERT INTO consumo (user_id, fecha, cantidad, descripcion) VALUES (%s, %s, %s, %s)',
                    (self.current_user_id, fecha, cantidad, descripcion))
                self.conn.commit()
                self.record_action(f"Consumo registrado: {fecha} - {cantidad} - {descripcion}")
                print("Consumo registrado exitosamente")
            except mysql.connector.Error as e:
                print(f"Error al registrar el consumo: {e}")
        else:
            print("Todos los campos deben ser completados")

    def show_historial_screen(self):
        print("\n--- Historial de Acciones ---")

        self.cursor.execute('SELECT accion, fecha FROM historial WHERE user_id = %s ORDER BY fecha DESC',
                            (self.current_user_id,))
        historial = self.cursor.fetchall()

        if historial:
            for accion, fecha in historial:
                print(f"{fecha} - {accion}")
        else:
            print("No hay historial de acciones.")

    def show_sugerencias_screen(self):
        print("\n--- Sugerencias ---")

        recommendations = self.generate_recommendations()
        for rec in recommendations:
            print(rec)

    def show_metas_screen(self):
        print("\n--- Gestión de Metas ---")

        # Añadir meta
        description = input("Añadir Meta - Descripción: ")
        start_date = input("Fecha Inicio (YYYY-MM-DD): ")
        end_date = input("Fecha Fin (YYYY-MM-DD): ")

        if description and start_date and end_date:
            try:
                self.cursor.execute(
                    'INSERT INTO metas (user_id, meta, fecha_inicio, fecha_fin) VALUES (%s, %s, %s, %s)',
                    (self.current_user_id, description, start_date, end_date))
                self.conn.commit()
                self.record_action(f"Meta añadida: {description} | Inicio: {start_date} | Fin: {end_date}")
                print("Meta añadida exitosamente")
            except mysql.connector.Error as e:
                print(f"Error al añadir la meta: {e}")
        else:
            print("Todos los campos deben ser completados")

        # Mostrar metas actuales
        self.display_metas()

    def display_metas(self):
        print("\n--- Metas Actuales ---")

        self.cursor.execute('SELECT meta, fecha_inicio, fecha_fin FROM metas WHERE user_id = %s',
                            (self.current_user_id,))
        metas = self.cursor.fetchall()

        if metas:
            for meta in metas:
                description, start_date, end_date = meta
                print(f"{description} | Inicio: {start_date} | Fin: {end_date}")
        else:
            print("No hay metas registradas.")

    def record_action(self, action):
        today = datetime.date.today()
        try:
            self.cursor.execute(
                'INSERT INTO historial (user_id, accion, fecha) VALUES (%s, %s, %s)',
                (self.current_user_id, action, today))
            self.conn.commit()
        except mysql.connector.Error as e:
            print(f"Error al registrar la acción: {e}")


if __name__ == "__main__":
    app = App()
