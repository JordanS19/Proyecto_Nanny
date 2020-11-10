from tkinter import *
from tkinter import ttk
from tkinter import messagebox as ms
import sqlite3
from Login import login

class Cuidador():
    database = 'database.db'
    personal_db = 'quit.db'
    id_num = 0
    def __init__(self, window, nombre, numero):
        global id_num
        self.window = window
        self.window.title('Nanny Cuidador')

        self.nombre = nombre 
        self.numero = numero

        frame = Frame(self.window)
        frame.grid(row=0, column=0, sticky=NSEW, columnspan=2)

        self.tree = ttk.Treeview(height = 10, columns=("#0","#1","#2","#3","#4"))
        self.tree.grid(row = 4, column = 0, columnspan = 1)
        self.tree.heading('#0', text = 'Name', anchor = CENTER)
        self.tree.heading('#1', text = 'Dia', anchor = CENTER)
        self.tree.heading('#2', text = 'Amount of kids', anchor = CENTER)
        self.tree.heading('#3', text = 'From', anchor = CENTER)
        self.tree.heading('#4', text = 'To', anchor = CENTER)
        self.tree.heading('#5', text = 'Special Care', anchor = CENTER)

        ttk.Button(self.window, text = 'ACCEPT', command=lambda: self.accept()).grid(row = 5, column = 0, columnspan = 1, sticky = W + E)
        ttk.Button(self.window, text = 'REFRESH', command=self.get_products).grid(row = 5, column = 1, columnspan = 2, sticky = W + E)

        scroll = ttk.Scrollbar(self.window, orient = VERTICAL, command= self.tree.yview)
        self.tree['yscroll'] = scroll.set

        self.tree.grid(in_=frame, row=0, column=0, sticky=NSEW)
        scroll.grid(in_=frame, row=0, column=2, sticky=NS)
        
        self.get_products()
    
    def run_query(self, query, parameters = ()):
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, parameters)
            conn.commit()
        return result
    
    def get_products(self):
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)

        query = 'SELECT * FROM ordenes ORDER BY id DESC'
        db_rows = self.run_query(query)
        for row in db_rows:
            if row[8] == "Yes":
                pass
            else:
                self.tree.insert('', 0, text = row[0], values = (row[1], row[2], row[3], row[4], row[5]))

    def accept(self):
        global id_num
        try:
            self.tree.item(self.tree.selection())['text'][0]
        except IndexError as e:
            ms.showerror('Error!', 'Please select an order')
            return
        nombre = self.tree.item(self.tree.focus())
        query = 'SELECT * FROM ordenes'
        db_rows = self.run_query(query)
        for row in db_rows:
            if row[0] == nombre.get("text"):
                ms.showinfo('Detalles', f'Nombre: {nombre.get("text")}\nNumero de telefono: {row[7]}')
                id_num = row[6]
                break
        query = f'UPDATE ordenes SET accepted = "Yes", nombre_c = "{self.nombre}", telefono = "{self.numero}" WHERE id = {id_num}'
        self.run_query(query)
        self.get_products()
    
    def delete(self, parameters):
        query = 'DELETE FROM ordenes WHERE id = ?'
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (parameters, ))
            conn.commit()
        self.get_products()

class Cliente():
    database = 'database.db'
    personal_db = 'quit.db'
    id_num = 0

    def __init__(self, window, nombre, numero):
        self.window = window
        self.window.title('Nanny')
        self.n_kids = StringVar()
        self.n_kids.set('1')
        self.care = StringVar()
        self.care.set('No')
        self.nombre = nombre 
        self.numero = numero
        self.ordenes = []

        frame = Frame(self.window)
        frame.grid(row=0, column=0, sticky=NSEW, columnspan=2)

        Label(frame, text = 'Dia: ').grid(row = 1, column = 0)
        self.dia = Entry(frame)
        self.dia.grid(row = 1, column = 1)

        Label(frame, text = 'Cantidad de infantes: ').grid(row = 2, column = 0)
        self.kids = OptionMenu(frame, self.n_kids, '1', '2', '3')
        self.kids.grid(row = 2, column = 1)

        Label(frame, text = 'Desde: (Formato 24hr, Ej. 15:30)').grid(row = 3, column = 0)
        self.in_time = Entry(frame)
        self.in_time.grid(row = 3, column = 1)

        Label(frame, text = 'Hasta: (Formato 24hr, Ej. 19:00)').grid(row = 4, column = 0)
        self.end_time = Entry(frame)
        self.end_time.grid(row = 4, column = 1)

        Label(frame, text = 'Special Care: ').grid(row = 5, column = 0)
        self.special_care = OptionMenu(frame, self.care, 'Yes', 'No')
        self.special_care.grid(row = 5, column = 1)

        ttk.Button(frame, text='ORDER', command = self.add_order).grid(row=6, column = 1)
        ttk.Button(frame, text='CHECK', command = self.check).grid(row=6, column = 0)

    def run_query(self, query, parameters = ()):
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, parameters)
            conn.commit()
        return result
    
    def add_order(self):
        if self.validation():
            query = 'INSERT INTO ordenes VALUES(?,?,?,?,?,?,NULL,?,?,NULL,NULL,?)'
            codigo = f"{self.nombre[0]}{self.dia.get()[3]}{self.n_kids.get()[0]}{self.in_time.get()[1]}{self.end_time.get()[1]}{self.care.get()[0]}{self.numero[-4:]}"
            parameters = (self.nombre, self.dia.get(), self.n_kids.get(), self.in_time.get(), self.end_time.get(), self.care.get(), self.numero, 'No', codigo)
            self.run_query(query, parameters)
            ms.showinfo("Codigo", f"Codigo: {codigo}\nNo pierda este codigo! Lo necesitara para checar su orden.")
            self.dia.delete(0, END)
            self.in_time.delete(0, END)
            self.end_time.delete(0, END)
            self.n_kids.set('1')
            self.care.set('No')
            
    def check(self):
        check_page = Toplevel()

        frame = Frame(check_page)
        frame.grid(row=0, column=0, sticky=NSEW, columnspan=2)

        Label(frame, text = 'Codigo: ').grid(row = 1, column = 0)
        code = Entry(frame)
        code.grid(row = 1, column = 1)

        ttk.Button(frame, text = "CHECK", command=lambda: self.check_code(code)).grid(row=2, columnspan=2)

    def check_code(self, code):
        if len(code.get()) != 0:
            query = f'SELECT * FROM ordenes WHERE code = "{code.get()}"'
            db_rows = self.run_query(query)
            for row in db_rows:
                if row[8] == 'Yes':
                    ms.showinfo('Orden Aceptada', f'Nombre del Cuidador: {row[9]}\nNumero del cuidador: {row[10]}')
                else:
                    ms.showinfo('Orden siendo procesada', 'Su orden no ha sido aceptada todavia')
    
    def validation(self):
        return len(self.dia.get()) != 0 and len(self.in_time.get()) != 0 and len(self.end_time.get()) != 0 and len(self.care.get()) != 0

if __name__ == "__main__":
    avanzar = False
    tipo = ''
    nombre = ''
    telefono = ''
    window = Tk()
    aplicacion = login(window, avanzar, tipo, nombre, telefono)
    window.mainloop()
    avanzar = aplicacion.advance
    tipo = aplicacion.tipo
    nombre = aplicacion.nombre
    numero = aplicacion.telefono
    if avanzar == True:
        if tipo == 'Cliente':
            window2 = Tk()
            aplicacion = Cliente(window2, nombre, numero)
            window2.mainloop()
        elif tipo == 'Cuidador':
            window2 = Tk()
            aplicacion = Cuidador(window2, nombre, numero)
            window2.mainloop()