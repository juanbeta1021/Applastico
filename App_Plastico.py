import tkinter as tk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error
import datetime


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplicación de Gestión de Plásticos")

        # Conectar a la base de datos
        self.conn = self.create_connection()
        if self.conn is None:
            print("No se pudo conectar a la base de datos. Verifica tus credenciales.")
            return

        self.cursor = self.conn.cursor()
        self.create_tables()

        # Crear los marcos de las pantallas
        self.frame_register = tk.Frame(root)
        self.frame_login = tk.Frame(root)
        self.frame_recover = tk.Frame(root)
        self.frame_main = tk.Frame(root)
        self.frame_metas = tk.Frame(root)
        self.frame_historial = tk.Frame(root)

        # Mostrar la pantalla de registro al iniciar
        self.show_register_screen()

    def create_connection(self):
        try:
            connection = mysql.connector.connect(
                host='127.0.0.1',
                port='3306',
                database='app_plastico',
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

    def show_register_screen(self):
        self.clear_screen()

        tk.Label(self.frame_register, text="Registro de Usuarios").pack()
        tk.Label(self.frame_register, text="Nombre:").pack()
        self.entry_name = tk.Entry(self.frame_register)
        self.entry_name.pack()

        tk.Label(self.frame_register, text="Correo Electrónico:").pack()
        self.entry_email = tk.Entry(self.frame_register)
        self.entry_email.pack()

        tk.Label(self.frame_register, text="Contraseña:").pack()
        self.entry_password = tk.Entry(self.frame_register, show='*')
        self.entry_password.pack()

        tk.Button(self.frame_register, text="Registrar", command=self.register_user).pack()
        tk.Button(self.frame_register, text="Iniciar Sesión", command=self.show_login_screen).pack()
        tk.Button(self.frame_register, text="Recuperar Contraseña", command=self.show_recover_screen).pack()

        self.frame_register.pack()

    def show_login_screen(self):
        self.clear_screen()

        tk.Label(self.frame_login, text="Inicio de Sesión").pack()
        tk.Label(self.frame_login, text="Correo Electrónico:").pack()
        self.entry_login_email = tk.Entry(self.frame_login)
        self.entry_login_email.pack()

        tk.Label(self.frame_login, text="Contraseña:").pack()
        self.entry_login_password = tk.Entry(self.frame_login, show='*')
        self.entry_login_password.pack()

        tk.Button(self.frame_login, text="Iniciar Sesión", command=self.login_user).pack()
        tk.Button(self.frame_login, text="Volver al Registro", command=self.show_register_screen).pack()

        self.frame_login.pack()

    def show_recover_screen(self):
        self.clear_screen()

        tk.Label(self.frame_recover, text="Recuperación de Contraseña").pack()
        tk.Label(self.frame_recover, text="Correo Electrónico:").pack()
        self.entry_recover_email = tk.Entry(self.frame_recover)
        self.entry_recover_email.pack()

        tk.Button(self.frame_recover, text="Enviar Enlace de Recuperación", command=self.recover_password).pack()
        tk.Button(self.frame_recover, text="Volver al Registro", command=self.show_register_screen).pack()

        self.frame_recover.pack()

    def register_user(self):
        name = self.entry_name.get()
        email = self.entry_email.get()
        password = self.entry_password.get()

        if name and email and password:
            try:
                self.cursor.execute('INSERT INTO users (name, email, password) VALUES (%s, %s, %s)',
                                    (name, email, password))
                self.conn.commit()
                messagebox.showinfo("Registro", "Registro exitoso")
                self.show_login_screen()
            except mysql.connector.IntegrityError:
                messagebox.showerror("Error", "El correo electrónico ya está registrado")
            except mysql.connector.Error as e:
                messagebox.showerror("Error", f"Error en el registro: {e}")
        else:
            messagebox.showerror("Error", "Todos los campos deben ser completados")

    def login_user(self):
        email = self.entry_login_email.get()
        password = self.entry_login_password.get()

        if email and password:
            self.cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
            user = self.cursor.fetchone()
            if user:
                self.current_user_id = user[0]  # Guarda el ID del usuario actual
                self.record_action("Inicio de sesión")
                messagebox.showinfo("Inicio de Sesión", "Inicio de sesión exitoso")
                self.show_main_screen()
            else:
                messagebox.showerror("Error", "Credenciales incorrectas")
        else:
            messagebox.showerror("Error", "Todos los campos deben ser completados")

    def recover_password(self):
        email = self.entry_recover_email.get()

        if email:
            # Aquí se debería agregar la lógica para enviar el enlace de recuperación
            messagebox.showinfo("Recuperación", "Enlace de recuperación enviado")
            self.show_register_screen()
        else:
            messagebox.showerror("Error", "El campo de correo electrónico debe ser completado")

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
        self.clear_screen()

        tk.Label(self.frame_main, text="Pantalla Principal").pack()
        tk.Button(self.frame_main, text="Registrar Consumo", command=self.show_consumo_screen).pack()
        tk.Button(self.frame_main, text="Ver Historial", command=self.show_historial_screen).pack()
        tk.Button(self.frame_main, text="Sugerir Alternativas", command=self.show_sugerencias_screen).pack()
        tk.Button(self.frame_main, text="Gestionar Metas", command=self.show_metas_screen).pack()

        self.frame_main.pack()

    def show_consumo_screen(self):
        self.clear_screen()

        tk.Label(self.frame_main, text="Registrar Consumo").pack()

        tk.Label(self.frame_main, text="Fecha (YYYY-MM-DD):").pack()
        self.entry_fecha = tk.Entry(self.frame_main)
        self.entry_fecha.pack()

        tk.Label(self.frame_main, text="Cantidad:").pack()
        self.entry_cantidad = tk.Entry(self.frame_main)
        self.entry_cantidad.pack()

        tk.Label(self.frame_main, text="Descripción:").pack()
        self.entry_descripcion = tk.Entry(self.frame_main)
        self.entry_descripcion.pack()

        tk.Button(self.frame_main, text="Guardar Consumo", command=self.save_consumo).pack()
        tk.Button(self.frame_main, text="Volver", command=self.show_main_screen).pack()

        self.frame_main.pack()

    def save_consumo(self):
        fecha = self.entry_fecha.get()
        cantidad = self.entry_cantidad.get()
        descripcion = self.entry_descripcion.get()

        if fecha and cantidad and descripcion:
            try:
                self.cursor.execute(
                    'INSERT INTO consumo (user_id, fecha, cantidad, descripcion) VALUES (%s, %s, %s, %s)',
                    (self.current_user_id, fecha, cantidad, descripcion))
                self.conn.commit()
                self.record_action(f"Consumo registrado: {fecha} - {cantidad} - {descripcion}")
                messagebox.showinfo("Consumo", "Consumo registrado exitosamente")
                self.show_main_screen()
            except mysql.connector.Error as e:
                messagebox.showerror("Error", f"Error al registrar el consumo: {e}")
        else:
            messagebox.showerror("Error", "Todos los campos deben ser completados")

    def show_historial_screen(self):
        self.clear_screen()

        tk.Label(self.frame_historial, text="Historial de Acciones").pack()

        self.cursor.execute('SELECT accion, fecha FROM historial WHERE user_id = %s ORDER BY fecha DESC',
                            (self.current_user_id,))
        historial = self.cursor.fetchall()

        if historial:
            for accion, fecha in historial:
                tk.Label(self.frame_historial, text=f"{fecha} - {accion}").pack()
        else:
            tk.Label(self.frame_historial, text="No hay historial de acciones.").pack()

        tk.Button(self.frame_historial, text="Volver", command=self.show_main_screen).pack()

        self.frame_historial.pack()

    def show_sugerencias_screen(self):
        self.clear_screen()

        tk.Label(self.frame_main, text="Sugerencias").pack()

        recommendations = self.generate_recommendations()
        for rec in recommendations:
            tk.Label(self.frame_main, text=rec).pack()

        tk.Button(self.frame_main, text="Volver", command=self.show_main_screen).pack()

        self.frame_main.pack()

    def show_metas_screen(self):
        self.clear_screen()

        tk.Label(self.frame_metas, text="Gestión de Metas").pack()

        # Añadir meta
        tk.Label(self.frame_metas, text="Añadir Meta:").pack()
        tk.Label(self.frame_metas, text="Descripción:").pack()
        self.entry_meta_desc = tk.Entry(self.frame_metas)
        self.entry_meta_desc.pack()

        tk.Label(self.frame_metas, text="Fecha Inicio (YYYY-MM-DD):").pack()
        self.entry_meta_start = tk.Entry(self.frame_metas)
        self.entry_meta_start.pack()

        tk.Label(self.frame_metas, text="Fecha Fin (YYYY-MM-DD):").pack()
        self.entry_meta_end = tk.Entry(self.frame_metas)
        self.entry_meta_end.pack()

        tk.Button(self.frame_metas, text="Guardar Meta", command=self.add_meta).pack()

        # Ver metas
        tk.Label(self.frame_metas, text="Metas Actuales:").pack()
        self.display_metas()

        tk.Button(self.frame_metas, text="Volver", command=self.show_main_screen).pack()

        self.frame_metas.pack()

    def add_meta(self):
        description = self.entry_meta_desc.get()
        start_date = self.entry_meta_start.get()
        end_date = self.entry_meta_end.get()

        if description and start_date and end_date:
            try:
                self.cursor.execute(
                    'INSERT INTO metas (user_id, meta, fecha_inicio, fecha_fin) VALUES (%s, %s, %s, %s)',
                    (self.current_user_id, description, start_date, end_date))
                self.conn.commit()
                self.record_action(f"Meta añadida: {description} | Inicio: {start_date} | Fin: {end_date}")
                messagebox.showinfo("Meta", "Meta añadida exitosamente")
                self.display_metas()
            except mysql.connector.Error as e:
                messagebox.showerror("Error", f"Error al añadir la meta: {e}")
        else:
            messagebox.showerror("Error", "Todos los campos deben ser completados")

    def display_metas(self):
        for widget in self.frame_metas.winfo_children():
            if isinstance(widget, tk.Label) and widget.cget("text").startswith("Meta"):
                widget.destroy()

        self.cursor.execute('SELECT meta, fecha_inicio, fecha_fin FROM metas WHERE user_id = %s',
                            (self.current_user_id,))
        metas = self.cursor.fetchall()

        if metas:
            for meta in metas:
                description, start_date, end_date = meta
                tk.Label(self.frame_metas, text=f"{description} | Inicio: {start_date} | Fin: {end_date}").pack()
        else:
            tk.Label(self.frame_metas, text="No hay metas registradas.").pack()

    def record_action(self, action):
        today = datetime.date.today()
        try:
            self.cursor.execute(
                'INSERT INTO historial (user_id, accion, fecha) VALUES (%s, %s, %s)',
                (self.current_user_id, action, today))
            self.conn.commit()
        except mysql.connector.Error as e:
            print(f"Error al registrar la acción: {e}")

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.pack_forget()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
