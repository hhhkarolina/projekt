import Keys
import requests
import json
from tkinter import *
from tkinter import messagebox
import mysql.connector

#polaczenie z baza dancyh
connection = mysql.connector.connect(user='root', password=Keys.password, host='127.0.0.1', database='ingredients1', auth_plugin='mysql_native_password')

query = 'SELECT * FROM ingredients'
cursor = connection.cursor()
cursor.execute(query)

fridge = []

for i in cursor:
    fridge.append(i[0])


print(fridge)


#wymiary okienka aplikacji
WIDTH_OF_ROOT = 310
HEIGHT_OF_ROOT = 205


class DataBaseItem: 
    query = 'SELECT * FROM table;'
    add_query = 'INSERT INTO table VALUES (%(name)s);'
    remove_query = 'DELETE FROM table WHERE ingredient=%(name)s;'

    #dodawanie obiektu do bazy dancyh       
    @classmethod
    def add_to_database(cls, **kwargs):
        cursor.execute(cls.add_query, kwargs)
        connection.commit()

    #usuwanie obiektu z bazy danych
    @classmethod
    def remove_from_database(cls, **kwargs):
        cursor.execute(cls.remove_query, kwargs)
        connection.commit()

    

class Ingredient(DataBaseItem):
    query = 'SELECT * FROM ingredients'
    add_query = 'INSERT INTO ingredients VALUES (%(name)s, %(amount)s);'
    remove_query = 'DELETE FROM ingredients WHERE ingredient = %(name)s;'
    edit_query = 'UPDATE ingredients SET amount = %(amount)s WHERE ingredient = %(name)s;'
    
    #edycja wartości liczby produktu w bazie danych
    @classmethod
    def edit_amount(cls, **kwargs):
        cursor.execute(cls.edit_query, kwargs)
        connection.commit()

   


class Dish(DataBaseItem):
    query = 'SELECT * FROM dishes;'
    add_query = 'INSERT INTO dishes VALUES (%(name)s);'
    remove_query = 'DELETE FROM dishes WHERE name=%(name)s;'

    #lista zawierająca dania z tabeli ulubione dania w bazie danych
    @classmethod    
    def select(cls):
        cursor.execute(cls.query)
        res = []

        for i in cursor:
            res.append(i[0])

        #print('ULUBIONE', res)

        return res



class GUI:
    def __init__(self):
        self.root = Tk()
        self.root.geometry('{0}x{1}'.format(WIDTH_OF_ROOT, HEIGHT_OF_ROOT))
        self.root.title('Pomysły na jedzenie')

        #ramka zawierająca liste posiadancyh produków
        self.list_frame = Frame(self.root, width=150, padx=10, pady=6)
        self.list_frame.grid(column=0, row=0)

        #ramka trzymająca dwie kolejne ramki
        self.right_frame = Frame(self.root, width=150, height=180, padx=10, pady=6)
        self.right_frame.grid(column=1, row=0)

        #pierwsza z ramek w right_frame, która zawiera pole do dodawania składników
        self.add_frame = Frame(self.right_frame, width=150)
        self.add_frame.grid(column=1, row=0)

        #druga ramka umieszczona w right_frame zawierająca przyciski: wyszukaj, wyświetl ulubione dania, usuń składniki
        self.search_frame = Frame(self.right_frame, pady= 40)
        self.search_frame.grid(column=1, row=1)

        #stworzenie listy składników razem ze scrollbarem
        self.scrollbar = Scrollbar(self.list_frame)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.ingredients = Listbox(self.list_frame, yscrollcommand=self.scrollbar.set, selectmode='extended')
        self.insert_to_fridge()
        self.ingredients.bind('<Double-1>', self.ing_info)
        self.ingredients.pack(side=LEFT, fill=BOTH)
        self.scrollbar.config(command=self.ingredients.yview)


        self.search = Button(self.search_frame, width=14, text='Wyszukaj przepisy', command=self.search)
        self.search.grid(row=1, column=1)

        self.remove = Button(self.search_frame, command=self.remove_ingredient, text='Usuń składniki', width=14)
        self.remove.grid(row=3, column=1)

        self.display_fav_button = Button(self.search_frame, command=self.display_fav, text='Ulubione dania', width=14)
        self.display_fav_button.grid(row=2, column=1)

        self.label_add = Label(self.add_frame, text='Dodaj składniki')
        self.label_add.grid(row=0, column=0)

        self.entry = Entry(self.add_frame, width=18)
        self.entry.grid(row=1, column=0)

        self.add = Button(self.add_frame, width=1, height=1, text='+', command=self.add_ingredient)
        self.add.grid(row=1, column=1)

        self.menubar = Menu(self.root)
        self.menu= Menu(self.menubar, tearoff=0)
        self.editmenu = Menu(self.menubar, tearoff=0)

        self.create_menu()

        self.root.config(menu=self.menu)

        self.root.mainloop()

    def help(self):
        messagebox.showinfo("Help", "Zaznacz składniki, które chcesz usunąć, a następnie kliknij przycisk 'Usuń składniki'.\nAby dodać kilka składników jednocześnie, oddziel je przecinkami.")

    #po podwojnym kliknieciu w skladnik
    def ing_info(self, event):
        selected_items = self.ingredients.curselection()
        sel_query = "SELECT * FROM ingredients WHERE ingredient=%(ingr)s;"

        for i in selected_items:
            #dla każdego zaznaczonego składnika wyświetla się nowe okienko
            ing_win = Tk()
            text = StringVar(ing_win)

            ing_name = self.ingredients.get(i)

            ing_win.title(ing_name)

            name_label = Label(ing_win, text=ing_name)
            name_label.grid(column=0, row=0)
            
            #pobranie z bazy danych skladnika o danej nazwie
            cursor.execute(sel_query, {'ingr' : ing_name})

            for c in cursor:
                #zapisanie liczby danego skladnika do data
                data = c[1]

            #stworzenie spinboxa do zmieniania liczby skladnika i ustawienie liczby, która się wyświetla na początku na obecną wartość 
            #danego składnika
            amount_spinbox = Spinbox(ing_win, textvariable=text, from_=0, to_=1000)
            text.set(data)
            amount_spinbox.grid(column=1, row=0)

            confirm_button = Button(ing_win, text='Potwierdź', command = lambda: self.edit_ing_amount(text.get(), ing_name))
            confirm_button.grid(row=0, column=2)

            ing_win.mainloop()
            

    #po kliknieciu przycisku potwierdz w ing_info
    def edit_ing_amount(self, amount, name):
        Ingredient.edit_amount(amount=amount, name=name)
        messagebox.showinfo('Info', 'Liczba została pomyślnie zmieniona')
           
    #dodawanie jednego lub wiecej skladnikow
    def add_ingredient(self):
        #pobranie wartosci z pola entry
        ing = self.entry.get()
        #wydzielenie osobnych skladnikow oddzielonych przecinkami
        ing = ing.split(',')

        for i in ing:
            #jezeli dany nie znajduje sie juz na liscie i ma dlugosc wieksza niz zero, to mozna go dodac
            if not i in self.ingredients.get(0, END) and len(i) > 0:
                self.ingredients.insert(END, i)

                Ingredient.add_to_database(name=i, amount=1)
                
                #usuniecie tekstu z pola entry
                self.entry.delete(0, last=END)
                

    def search(self):
        result_win = Tk()
        result_win.title('Wyniki wyszukiwania')

        scrollb = Scrollbar(result_win)
        scrollb.pack(side=RIGHT, fill=Y)

        dishes = Listbox(result_win, yscrollcommand=scrollb.set, selectmode='extended', width=100)
        
        #utworzenie listy na posiadane skladniki
        list = []
        for ing in self.ingredients.get(0, END):
            list.append(ing)

        #zmodywikowanie listy na string w taki sposob by pasowal do requesta
        list = ',+'.join(list)

        response = requests.get(url="https://api.spoonacular.com/recipes/findByIngredients?ingredients={}".format(list), 
                        headers= {'x-api-key': Keys.api_key})

        if response.status_code == 200:
            dish_data = json.loads(response.text)
        else:
            dish_data = {'title' : 'błąd połączenia - {}'.format(response.status_code)}
        

        for i in dish_data:
            dishes.insert(END, i['title'])
            #dishes.insert(END, i)

        def add_to_fav(event):
            selected = dishes.curselection()
            for i in selected:
                if not dishes.get(i) in Dish.select():
                    Dish.add_to_database(name=dishes.get(i))
                    messagebox.showinfo('Info', 'Dodano do ulubionych!')
                else:
                    messagebox.showinfo('Info', 'To danie znajduje się już w ulubionych!')

        dishes.bind('<Double-1>', add_to_fav)
        
        dishes.pack(side=LEFT, fill=BOTH)
        scrollb.config(command=dishes.yview)

        result_win.mainloop()


    def remove_ingredient(self):
        selected_items = self.ingredients.curselection()

        for i in selected_items[::-1]:
            Ingredient.remove_from_database(name = self.ingredients.get(i))
            self.ingredients.delete(i)


    def insert_to_fridge(self):
        for ing in fridge:
            self.ingredients.insert(END, ing)

    def display_fav(self):
        fav = Tk()
        fav.title('Ulubione')
        left_frame = Frame(fav)
        left_frame.grid(column=0, row=0, padx=10, pady=10)

        right_frame = Frame(fav)
        right_frame.grid(column=1, row=0, padx=10, pady=10)

        scrollb = Scrollbar(left_frame)
        scrollb.pack(side=RIGHT, fill=Y)

        favs = Listbox(left_frame, yscrollcommand=scrollb.set, selectmode='extended', width=50)

        for i in Dish.select():
            favs.insert(END, i)

            
        rem_button = Button(right_frame, text='Usuń z ulubionych', command = lambda: self.remove_fav(favs))
        rem_button.grid(column=1, row=0)
        favs.pack()
        scrollb.config(command=favs.yview)


        fav.mainloop()

    def remove_fav(self, listbox):
        selected_items = listbox.curselection()

        for i in selected_items[::-1]:

            Dish.remove_from_database(name = listbox.get(i))
            listbox.delete(i)




    def create_menu(self):
        self.menu.add_command(label="Help",command=self.help)
        self.menubar.add_cascade(label = "File", menu=self.menu)



if __name__ == '__main__':
    a = GUI()

 





