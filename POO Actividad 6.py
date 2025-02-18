import tkinter as tk
from tkinter import messagebox, ttk
import os
import re
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArchivoCRUD:
    def __init__(self, nombre_archivo):
        self.nombre_archivo = nombre_archivo
        self.crear_archivo()

    def crear_archivo(self):
        """Crea el archivo si no existe y registra la ubicación."""
        try:
            # Obtener la ruta absoluta del archivo
            ruta_absoluta = os.path.abspath(self.nombre_archivo)
            logger.info(f"Intentando crear/acceder al archivo en: {ruta_absoluta}")

            # Crear el archivo si no existe
            if not os.path.exists(ruta_absoluta):
                with open(ruta_absoluta, 'w', encoding='utf-8') as archivo:
                    archivo.write(f"# Archivo de contactos creado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                logger.info("Archivo creado exitosamente")
            else:
                logger.info("El archivo ya existe")

            # Verificar permisos
            if os.access(os.path.dirname(ruta_absoluta), os.W_OK):
                logger.info("Tenemos permisos de escritura en el directorio")
            else:
                logger.warning("No hay permisos de escritura en el directorio")

        except Exception as e:
            logger.error(f"Error al crear el archivo: {str(e)}")
            messagebox.showerror("Error", f"No se pudo crear el archivo: {str(e)}")

    def validar_telefono(self, telefono):
        """Valida el formato del número de teléfono."""
        patron = re.compile(r'^\+?[\d\s-]{6,15}$')
        return bool(patron.match(telefono))

    def crear(self, nombre, telefono, email=""):
        """Añade un nuevo contacto al archivo."""
        try:
            contactos = self.leer()
            # Verificar si el contacto ya existe
            if any(c['nombre'].lower() == nombre.lower() for c in contactos):
                return False, "El contacto ya existe"
            
            if not self.validar_telefono(telefono):
                return False, "Formato de teléfono inválido"

            with open(self.nombre_archivo, 'a', encoding='utf-8') as archivo:
                archivo.write(f'{nombre},{telefono},{email}\n')
            logger.info(f"Contacto creado: {nombre}")
            return True, "Contacto creado exitosamente"
        except Exception as e:
            logger.error(f"Error al crear contacto: {str(e)}")
            return False, f"Error al crear contacto: {str(e)}"

    def leer(self):
        """Lee y devuelve todos los contactos del archivo."""
        contactos = []
        try:
            with open(self.nombre_archivo, 'r', encoding='utf-8') as archivo:
                for linea in archivo:
                    if linea.startswith('#') or not linea.strip():
                        continue
                    partes = linea.strip().split(',')
                    nombre = partes[0]
                    telefono = partes[1]
                    email = partes[2] if len(partes) > 2 else ""
                    contactos.append({
                        'nombre': nombre,
                        'telefono': telefono,
                        'email': email
                    })
            logger.info(f"Leídos {len(contactos)} contactos")
        except FileNotFoundError:
            logger.warning("Archivo no encontrado, creando uno nuevo")
            self.crear_archivo()
        except Exception as e:
            logger.error(f"Error al leer contactos: {str(e)}")
        return contactos

    def actualizar(self, nombre, nuevo_telefono, nuevo_email=""):
        """Actualiza los datos de un contacto."""
        if not self.validar_telefono(nuevo_telefono):
            return False, "Formato de teléfono inválido"
            
        contactos = self.leer()
        actualizado = False
        with open(self.nombre_archivo, 'w', encoding='utf-8') as archivo:
            archivo.write("# Última actualización: {}\n".format(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            for contacto in contactos:
                if contacto['nombre'].lower() == nombre.lower():
                    contacto['telefono'] = nuevo_telefono
                    contacto['email'] = nuevo_email
                    actualizado = True
                archivo.write(f"{contacto['nombre']},{contacto['telefono']},{contacto['email']}\n")
        return actualizado, "Contacto actualizado" if actualizado else "Contacto no encontrado"

    def eliminar(self, nombre):
        """Elimina un contacto del archivo."""
        contactos = self.leer()
        contactos_filtrados = [c for c in contactos if c['nombre'].lower() != nombre.lower()]
        eliminado = len(contactos) != len(contactos_filtrados)
        
        if eliminado:
            with open(self.nombre_archivo, 'w', encoding='utf-8') as archivo:
                archivo.write("# Última actualización: {}\n".format(
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                for contacto in contactos_filtrados:
                    archivo.write(f"{contacto['nombre']},{contacto['telefono']},{contacto['email']}\n")
        
        return eliminado

class AplicacionCRUD:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Contactos")
        self.root.geometry("600x500")
        self.crud = ArchivoCRUD('contactos.txt')
        self.crear_interfaz()
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.configure("Treeview", rowheight=25)
        self.style.configure("TButton", padding=5)

    def crear_interfaz(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Frame para entradas
        input_frame = ttk.LabelFrame(main_frame, text="Datos del Contacto", padding="5")
        input_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)

        # Etiquetas y entradas
        ttk.Label(input_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_nombre = ttk.Entry(input_frame, width=30)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Teléfono:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_telefono = ttk.Entry(input_frame, width=20)
        self.entry_telefono.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Email:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_email = ttk.Entry(input_frame, width=30)
        self.entry_email.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky=tk.W)

        # Frame para botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=4, pady=10)

        # Botones CRUD
        ttk.Button(button_frame, text="Crear", command=self.crear_contacto).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self.actualizar_contacto).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self.eliminar_contacto).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self.limpiar_campos).grid(row=0, column=3, padx=5)

        # Tabla para mostrar contactos
        self.tree = ttk.Treeview(main_frame, columns=("Nombre", "Teléfono", "Email"), show='headings', height=15)
        self.tree.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # Configurar columnas
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Teléfono", text="Teléfono")
        self.tree.heading("Email", text="Email")
        
        self.tree.column("Nombre", width=200)
        self.tree.column("Teléfono", width=150)
        self.tree.column("Email", width=250)

        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=2, column=4, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Bindear evento de selección
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        # Mostrar contactos iniciales
        self.mostrar_contactos()

    def limpiar_campos(self):
        """Limpia todos los campos de entrada."""
        self.entry_nombre.delete(0, tk.END)
        self.entry_telefono.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.tree.selection_remove(self.tree.selection())

    def on_select(self, event):
        """Maneja la selección de un contacto en la tabla."""
        selected_items = self.tree.selection()
        if selected_items:
            item = self.tree.item(selected_items[0])
            valores = item['values']
            self.entry_nombre.delete(0, tk.END)
            self.entry_telefono.delete(0, tk.END)
            self.entry_email.delete(0, tk.END)
            self.entry_nombre.insert(0, valores[0])
            self.entry_telefono.insert(0, valores[1])
            if len(valores) > 2:
                self.entry_email.insert(0, valores[2])

    def crear_contacto(self):
        nombre = self.entry_nombre.get().strip()
        telefono = self.entry_telefono.get().strip()
        email = self.entry_email.get().strip()
        
        if not nombre or not telefono:
            messagebox.showerror("Error", "Nombre y teléfono son obligatorios.")
            return

        exito, mensaje = self.crud.crear(nombre, telefono, email)
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.limpiar_campos()
            self.mostrar_contactos()
        else:
            messagebox.showerror("Error", mensaje)

    def actualizar_contacto(self):
        nombre = self.entry_nombre.get().strip()
        telefono = self.entry_telefono.get().strip()
        email = self.entry_email.get().strip()
        
        if not nombre or not telefono:
            messagebox.showerror("Error", "Nombre y teléfono son obligatorios.")
            return

        exito, mensaje = self.crud.actualizar(nombre, telefono, email)
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.limpiar_campos()
            self.mostrar_contactos()
        else:
            messagebox.showerror("Error", mensaje)

    def eliminar_contacto(self):
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showerror("Error", "Seleccione un contacto para eliminar.")
            return

        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar el contacto '{nombre}'?"):
            if self.crud.eliminar(nombre):
                messagebox.showinfo("Éxito", "Contacto eliminado correctamente.")
                self.limpiar_campos()
                self.mostrar_contactos()
            else:
                messagebox.showerror("Error", "No se encontró el contacto.")

    def mostrar_contactos(self):
        """Actualiza la tabla con los contactos actuales."""
        for row in self.tree.get_children():
            self.tree.delete(row)
        contactos = self.crud.leer()
        for contacto in contactos:
            self.tree.insert("", tk.END, values=(
                contacto['nombre'],
                contacto['telefono'],
                contacto.get('email', "")
            ))

if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionCRUD(root)
    root.mainloop()