from Tkinter import *
from ttk import *
import Tkinter
import sqlite3
import csv
from tkFileDialog import askopenfilename
import tkMessageBox

con = sqlite3.connect('funtest.db')
cur = con.cursor()


# def create_table():
#     c.execute('CREATE TABLE IF NOT EXISTS membersTbl(unix REAL, datestamp TEXT, keyword TEXT, value REAL)')

def apply_color(text, color_code):
    return color_code + text + '\033[0m'


def populate_data(filename):

    try:
        with open(filename, 'rb') as fin:  # `with` statement available in 2.5+
            # csv.DictReader uses first line in file for column headings by default
            dr = csv.DictReader(fin)  # comma is default delimiter
            # Get the column names
            headers = dr.fieldnames
            # identify the csv format and store the data into corresponding tables
            if 'Member #' in headers:
                # creating the table
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS members_table ('Member #' TEXT, 'Last Name' TEXT,'First Name' TEXT,'Street Address' TEXT,'City' TEXT,'State' TEXT,'Zip Code' TEXT,'Phone' TEXT,'Favorite Store' TEXT,'Date Joined' TEXT,'Dues Paid' TEXT);"
                )
                # gathering the data from csv
                to_db = [(i['Member #'], i['Last Name'], i['First Name'], i['Street Address'], i['City'], i['State'],
                          i['Zip Code'], i['Phone'], i['Favorite Store'], i['Date Joined'], i['Dues Paid']) for i in dr]

                # inserting the data to db
                cur.executemany("INSERT INTO members_table VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", to_db)
                print apply_color('Date imported into members table', '\033[94m')

            elif 'Store id' in headers:
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS stores_table ('Store id' TEXT, 'Store name' TEXT,'Location' TEXT);")

                to_db = [(i['Store id'], i['Store name'], i['Location']) for i in dr]
                cur.executemany("INSERT INTO stores_table VALUES (?, ?, ?);", to_db)
                print apply_color('Date imported into stores table', '\033[92m')

            else:
                tkMessageBox.showinfo("Alert", "Given csv file not matched with our format")
                return

        con.commit()
    except:
        con.close()


master = Tk()
master.geometry('500x500')


# Class helps to generate table
class Table(Toplevel):
    def __init__(self, parent, title=None, columns=None):
        Toplevel.__init__(self, parent)
        self.CreateUI(columns)
        self.title(title)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.columns = columns

    def CreateUI(self, columns):
        tv = Treeview(self)
        tv['columns'] = columns
        tv['show'] = 'headings'
        for column in columns:
            tv.heading(column, text=column)
            tv.column(column, anchor='center', width=90)

        tv.grid(sticky=(N, S, W, E))
        self.treeview = tv

    def LoadTable(self, query):
        records = cur.execute(query).fetchall()
        for row in records:
            self.treeview.insert('', 'end', values=(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]))


def import_data():
    print "clicked importData!"
    filename = askopenfilename()
    if not filename.endswith('.csv'):
        tkMessageBox.showinfo("Error", "Invalid csv file")
        return

    populate_data(filename)


def is_stores_table_exists():
    records = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stores_table';")
    for i in records:
        if i[0]:
            return True
    return False


def is_members_table_exists():
    records = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='members_table';")
    for i in records:
        if i[0]:
            return True
    return False


def get_member_table_column_names():
    return 'Member #', 'Last Name', 'First Name', 'Street Address', 'City', 'State', 'Zip Code', 'Phone', 'Favorite Store', 'Date Joined', 'Dues Paid'


def get_store_table_column_names():
    return 'Store id', 'Store name','Location'


def get_names_alphabetically():
    print "clicked Get name alphabetically query!"
    if not is_members_table_exists():
        tkMessageBox.showinfo("Error", "Please upload members.csv file")
        return

    member_table = Table(master, title='Member names in alphabetical order', columns=get_member_table_column_names())
    # getting data from db
    member_table.LoadTable('select * from members_table ORDER BY "First name", "Last name";')


def query2():
    print "clicked query2 button! which List all members with zip code 22101 who have paid dues during January"
    if not is_members_table_exists():
        tkMessageBox.showinfo("Error", "Please upload members.csv file")
        return

    member_table = Table(master, title='List all members with zip code 22101 and have paid dues on January', columns=get_member_table_column_names())
    member_table.LoadTable('select * from members_table where "Zip code"=22101 and strftime(\'%m\', "Dues Paid") = \'01\';')


def query3():
    print "clicked query3 button which lists all members who have joined since 1999-07-01 and live in VA."
    if not is_members_table_exists():
        tkMessageBox.showinfo("Error", "Please upload members.csv file")
        return

    member_table = Table(master, title='List all members who have joined since 1999-07-01 and live in VA.', columns=get_member_table_column_names())
    member_table.LoadTable('select * from members_table where "State"="VA" and date("Date joined") > date("1999-07-01");')


def query4():
    print "clicked query4 button which List the names of all members and the names of their favorite store and its location"
    if not is_members_table_exists():
        tkMessageBox.showinfo("Error", "Please upload members.csv file")
        return

    if not is_stores_table_exists():
        tkMessageBox.showinfo("Error", "Please upload stores.csv file")
        return

    member_table = Table(master, title='List the names of all members and the names of their favorite store and its location.', columns=('First name', 'Last name', 'Store name', 'Location'))
    records = cur.execute('select `First Name`, `Last Name`, `Store name`, `Location` from members_table  INNER JOIN stores_table ON "Favorite Store" = "Store id" ORDER BY "First name";').fetchall()
    for row in records:
        member_table.treeview.insert('', 'end', values=(row[0], row[1], row[2], row[3]))


def query5():
    print "clicked query5 button which lists the names of  all members whose favorite store is Total Wine"
    if not is_members_table_exists():
        tkMessageBox.showinfo("Error", "Please upload members.csv file")
        return

    if not is_stores_table_exists():
        tkMessageBox.showinfo("Error", "Please upload stores.csv file")
        return

    member_table = Table(master, title='List the names of all members and the names of their favorite store and its location.', columns=('First name', 'Last name'))
    records = cur.execute('select `First Name`, `Last Name` from members_table  where "Favorite Store"= (select `Store id` from stores_table where "Store name"="Total Wine");').fetchall()
    for row in records:
        member_table.treeview.insert('', 'end', values=(row[0], row[1]))

bimport = Tkinter.Button(master, text="Import data", command=import_data, width = 55, background="red")
bimport.pack(expand=True, padx=10, pady=10, fill='both')

b1 = Tkinter.Button(master, text="Get alphabetized member names", command=get_names_alphabetically, width = 55, background="green")
b1.pack(expand=True, padx=10, pady=10, fill='both')

b2 = Tkinter.Button(master, text="Get members with zip code 22101 who have paid dues during January", command=query2, width = 55, background="blue")
b2.pack(expand=True, padx=10, pady=10, fill='both')

b3 = Tkinter.Button(master, text="Get members who have joined since 1999-07-01 and live in VA", command=query3, width = 55, background="brown")
b3.pack(expand=True, padx=10, pady=10, fill='both')

b4 = Tkinter.Button(master, text="Get members and the names of their favorite store and its location", command=query4, width = 55, background="cyan")
b4.pack(expand=True, padx=10, pady=10, fill='both')

b5 = Tkinter.Button(master, text="Get members whose favorite store is Total Wine", command=query5, width = 55, background="yellow")
b5.pack(expand=True, padx=10, pady=10, fill='both')

mainloop()
