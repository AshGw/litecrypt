# type: ignore

import atexit
import json
import os.path
import platform
import re
import secrets
import string

import ttkbootstrap as tk

import litecrypt.mapper.database as ld
from litecrypt.core.safepack.replicas import Crypt, CryptFile, tqr
from litecrypt.utils.consts import Gui

"""--------------------------------HOW TO ?------------------------"""
gui_usage_manual = f"""This is the Database Output Console,
designed to display database-related operations.
Below is a guide on how to use the GUI for different tasks.


Usage

First step is to set the main key up

- If you don't have a main key, click the "GENERATE" button to create a secure key.
- Paste the generated key into the "ENC KEY" field and press "SELECT."

Text Encryption:

- Enter your text in the field "TEXT".
- Click "ENCRYPT" to encrypt the text.
- Optionally, choose to display the encrypted text as a QR code.

Text Decryption:

- Enter the encrypted text in the field "CIPHERTEXT"
- Click "DECRYPT" to decrypt the text.
- Optionally, choose to display the decrypted text as a QR code.


File Encryption:

- Enter the file name or full path in the "FILE" field.
- Click "ENCRYPT FILE" to encrypt the file.
- A success message will appear if the encryption is successful,
along with the addition of the ".crypt" extension.
- An error message will be displayed if encryption fails.

File Decryption:

- Click "DECRYPT FILE" to decrypt a file with the ".crypt" extension.
- If successful, the ".crypt" extension will be removed from the file name.

Databases

This GUI only supports sqlite databases.

Setup

- Specify the database path where you want your databases to be and any associated output information..
- Specify the name of your main database.
- The main database and the auto-generated keys database will be created.
* Example: you type test_database.db which will in turn generate test_databaseKeys.db

Info

The main database's table is 'stashmain' whereas for the keys database it's 'stashkeys'

Both databases have the same table structure that has 4 columns:

- `ID` which is auto-generated & incremented for each piece of data that gets inserted.

- `name` that holds the filename in both db's ,
although for the keys database if you haven't specified any file
to operate on while selecting different keys, then all these inserted keys will be tagged with:
`STANDALONE` for their associated filename.

- `content` for the main db this holds the entire content of the given file whereas for the keys db
it holds the actual 256-bit encryption key.

- `ref` for both db's, this holds the `ref` A.K.A key reference value.
Which is the only piece of data between the
two databases.

Buttons

The buttons are self-explanatory. Here's a quick overview of their functions:


- "ADD TO DATABASE" toggles to insert encrypted/decrypted data into the database.

- "SWITCH DATABASE" toggles between the main database and keys database.

- "QUERY": Execute raw SQLite queries, the result will be in "output.json."


- "SPAWN": Extracts file(s) from the database associated with a specific key reference
and creates them in the directory you chose.


Click the buttons and observe the results in the "DATABASE OUTPUT CONSOLE."
The genrated output will guide you through the process.
"""
"""------------------------FRAMING STARTED-------------------"""

main_object = tk.Window(themename=Gui.THEME)
main_object.resizable(False, False)
main_object.title(Gui.TITLE)
main_object.geometry(Gui.DIMENSIONS)


databaseFrame = tk.Frame(master=main_object, width=500, height=800)
databaseFrame.place(x=0, y=0)

frameFile1 = tk.Frame(master=main_object, width=500, height=250)
frameFile1.place(x=500, y=0)

frameFile2 = tk.Frame(master=main_object, width=500, height=250)
frameFile2.place(x=500, y=250)

textFrame1 = tk.Frame(master=main_object, width=500, height=250)
textFrame1.place(x=1000, y=0)

textFrame2 = tk.Frame(master=main_object, width=500, height=250)
textFrame2.place(x=1000, y=250)

lowerFrame = tk.Frame(master=main_object, width=1000, height=260)
lowerFrame.place(x=500, y=540)

"""---------------DATABASE FRAME STARTED-----------------------"""


databaseFrame = tk.Frame(master=main_object, height=800, width=500)
databaseFrame.place(rely=0, relx=0)

if platform.system() == "Windows":
    console_label = tk.Label(
        master=databaseFrame, text="DATABASE OUTPUT CONSOLE", font="Calibre 15"
    )
    console_label.place(relx=0.12, rely=0.04)

    db_display_text = tk.ScrolledText(
        width=43, height=27, font="terminal 13", wrap="word"
    )
    db_display_text.place(relx=0.016, rely=0.105)
    db_display_text.insert(
        tk.END, f"Running on: {platform.system()}\nClick '?' to see how this works"
    )
else:
    console_label = tk.Label(
        master=databaseFrame, text="DATABASE OUTPUT CONSOLE", font="Calibre 15 bold"
    )
    console_label.place(relx=0.115, rely=0.04)

    db_display_text = tk.Text(width=38, height=22, font="Calibre 13 bold", wrap="word")
    db_display_text.place(relx=0.015, rely=0.105)
    db_display_text.insert(
        tk.END, f"Running on: {platform.system()}\nClick '?' to see how this works"
    )


def show_all_content():
    global db_enable_blocker, main_db_name_var, usable_real_path, main_db_conn, db_display_text, keys_db_conn

    if db_enable_blocker != 0:
        db_display_text.delete("1.0", tk.END)
        db_display_text.insert(
            tk.END, f"Check 'output.json' in the chosen path : {usable_real_path}\n"
        )
        json_path = os.path.join(usable_real_path, "output.json")
        if swich_db_var.get() == 1:
            conn = keys_db_conn
        else:
            conn = main_db_conn
        try:
            with open(json_path, "w") as f:
                buffer = {}
                for e in conn.content():
                    buffer["ID " + e[0].__str__()] = [
                        {"filename": e[1]},
                        {"content": e[2].__str__()},
                        {"ref": e[3]},
                    ]
                json_content = json.dumps(buffer, indent=2)
                f.write(json_content)
                db_display_text.insert(
                    tk.END,
                    "\nSuccessfully written all table content in output.json\n"
                    "\nNote that this file will be deleted when the app is closed",
                )
        except BaseException as e:
            db_display_text.insert(
                tk.END,
                "Failed to write all table content in output.json\n" f"Reason: {e}",
            )


def show_content_by_id():
    global db_enable_blocker, main_db_conn, keys_db_conn, content_id_entry_var, usable_real_path
    idd = content_id_entry_var.get().strip()
    last_id = checkid()
    if db_enable_blocker != 0:
        if swich_db_var.get() == 1:
            conn = keys_db_conn
        else:
            conn = main_db_conn
        try:
            if int(idd) > 0:
                if last_id == -1:
                    db_display_text.delete("1.0", tk.END)
                    db_display_text.insert(
                        tk.END, "The table does not have any content to show"
                    )
                elif last_id != -1:
                    if int(idd) in range(1, last_id):
                        db_display_text.delete("1.0", tk.END)
                        to_json_path = os.path.join(usable_real_path, "output.json")
                        with open(to_json_path, "w") as f:
                            buffer = {}
                            e = conn.content_by_id(idd)
                            buffer["ID_" + e[0].__str__()] = [
                                {"filename": e[1]},
                                {"content": e[2].__str__()},
                                {"ref": e[3]},
                            ]
                            json_content = json.dumps(buffer, indent=2)
                            f.write(json_content)
                        db_display_text.insert(
                            tk.END,
                            f"Successful fetch !\n\nCheck the 'output.json' file in the"
                            f" chosen path :\n\n'{usable_real_path}'",
                        )
                    if int(idd) == last_id:
                        db_display_text.delete("1.0", tk.END)
                        db_display_text.insert(tk.END, "Chosen last ID\n\n")
                        to_json_path = os.path.join(usable_real_path, "output.json")
                        try:
                            with open(to_json_path, "w") as f:
                                buffer = {}
                                e = conn.content_by_id(int(idd))
                                buffer["ID_" + e[0].__str__()] = [
                                    {"filename": e[1]},
                                    {"content": e[2].__str__()},
                                    {"ref": e[3]},
                                ]
                                json_content = json.dumps(buffer, indent=2)
                                f.write(json_content)
                            db_display_text.insert(
                                tk.END,
                                f"Successful fetch !\n\nCheck the 'output.json' file in the"
                                f" the chosen path :\n\n'{usable_real_path}'",
                            )
                        except BaseException as e:
                            db_display_text.delete("1.0", tk.END)
                            db_display_text.insert(
                                tk.END,
                                "ERROR \n\nCheck the validity of 'output.json' file"
                                "\n\nCheck if the database is faulty\n"
                                f"Error: {e}",
                            )
                    elif int(idd) > last_id:
                        db_display_text.delete("1.0", tk.END)
                        db_display_text.insert(
                            tk.END, "Given ID is greater than the highest available ID"
                        )
            else:
                db_display_text.delete("1.0", tk.END)
                db_display_text.insert(tk.END, "ID must be strictly greater than 0")
        except BaseException as e:
            db_display_text.delete("1.0", tk.END)
            db_display_text.insert(
                tk.END,
                "ID value must be a valid integer in the database\n" f"Error: {e}",
            )


def drop_content_by_id():
    global db_enable_blocker, main_db_conn, keys_db_conn, content_id_entry_var
    idd = content_id_entry_var.get().strip()
    last_id = checkid()
    if db_enable_blocker != 0:
        if swich_db_var.get() == 1:
            conn = keys_db_conn
        else:
            conn = main_db_conn
        try:
            if int(idd) > 0:
                if last_id == -1:
                    db_display_text.delete("1.0", tk.END)
                    db_display_text.insert(
                        tk.END, "The table does not have any content to drop"
                    )
                elif last_id != -1:
                    if int(idd) in range(1, last_id):
                        db_display_text.delete("1.0", tk.END)
                        db_display_text.insert(tk.END, "Valid ID")
                        conn.drop_content(idd)
                        db_display_text.insert(
                            tk.END, f"\nDropping by ID {idd} Went successful"
                        )

                    if int(idd) == last_id:
                        db_display_text.delete("1.0", tk.END)
                        db_display_text.insert(tk.END, "Chosen last ID")
                        conn.drop_content(idd)
                        db_display_text.insert(
                            tk.END, f"\nDropping by ID {idd} Went successful"
                        )

                    elif int(idd) > last_id:
                        db_display_text.delete("1.0", tk.END)
                        db_display_text.insert(
                            tk.END, "Given ID is greater than the greatest available ID"
                        )
            else:
                db_display_text.delete("1.0", tk.END)
                db_display_text.insert(tk.END, "ID must be strictly greater than 0")
        except BaseException as e:
            db_display_text.delete("1.0", tk.END)
            db_display_text.insert(
                tk.END, "ID value must be a valid integer\n" f"Error: {e}"
            )


show_all_content_button = tk.Button(
    master=databaseFrame,
    text="SHOW ALL CONTENT",
    command=show_all_content,
    bootstyle="light outline",
)
show_all_content_button.place(relx=0.334, rely=0.87)


query_clicks = 1


def query():
    global db_enable_blocker, main_db_conn, keys_db_conn, usable_real_path, query_clicks
    if db_enable_blocker != 0:
        if swich_db_var.get() == 1:
            conn = keys_db_conn
        else:
            conn = main_db_conn
        query_var = query_entry_var.get().strip()
        if len(query_var) > 0:
            try:
                db_display_text.delete("1.0", tk.END)
                json_file = os.path.join(usable_real_path, "output.json")
                query_out = conn._query(query_var)
                conn.create_all()
                with open(json_file, "w") as f:
                    print(query_out)
                    json_content = json.dumps(
                        {f"query {query_clicks}": query_out}, indent=2
                    )
                    query_clicks += 1
                    f.write(json_content)
                db_display_text.insert(tk.END, f"Ran query {query_clicks} !\n\n")
                db_display_text.insert(
                    tk.END, "The result of the query is in 'output.json' file\n\n"
                )
            except BaseException as e:
                db_display_text.delete("1.0", tk.END)
                db_display_text.insert(tk.END, "Failed to finish the query!\n\n" f"{e}")
                db_display_text.insert(tk.END, " Use buttons instead if possible")
        else:
            db_display_text.delete("1.0", tk.END)
            db_display_text.insert(tk.END, "Can't query nothing\n\n")


query_entry_var = tk.StringVar()
query_entry = tk.Entry(
    master=databaseFrame, width=38, font="Calibre 13 bold", textvariable=query_entry_var
)

query_entry.place(relx=0.043, rely=0.742)

query_button = tk.Button(
    master=databaseFrame,
    text="RUN RAW SQL QUERY",
    command=query,
    bootstyle="light outline",
    width=25,
)
query_button.place(relx=0.28, rely=0.81)


drop_content_by_id_button = tk.Button(
    master=databaseFrame,
    text="DROP CONTENT BY ID",
    command=drop_content_by_id,
    bootstyle="light outline",
)
drop_content_by_id_button.place(relx=0.08, rely=0.93)

content_id_entry_var = tk.StringVar(value=" ID")
content_id_entry = tk.Entry(
    master=databaseFrame, textvariable=content_id_entry_var, width=3, font="Calibre 11"
)
content_id_entry.place(relx=0.45, rely=0.93)

show_content_by_id_button = tk.Button(
    master=databaseFrame,
    text="SHOW CONTENT BY ID",
    command=show_content_by_id,
    bootstyle="light outline",
)
show_content_by_id_button.place(relx=0.562, rely=0.93)


"""----------------------LOWER FRAME STARTED------------------"""


lowerFrame = tk.Frame(master=main_object, width=1000, height=260)
lowerFrame.place(x=500, y=540)


db_path_blocker = 0
usable_real_path = ""


def set_db_path():
    global db_path_blocker, usable_real_path
    path = db_path_var.get().strip()
    if os.path.isdir(path.strip()):
        db_path_blocker = 1
        db_path_result_var.set("SET")
        usable_real_path = path
    else:
        db_path_blocker = 0
        db_path_result_var.set("NOT SET")
        usable_real_path = ""


main_db_name_blocker = 0
db_already_exists_blocker = 0
maindbname = ""


def main_db_name():
    global main_db_name_blocker, db_already_exists_blocker, usable_real_path, db_path_blocker, success_maindb_connection_blocker, main_db_conn, maindbname

    dbname = main_db_name_var.get().strip()
    if re.match(r"((^[\w(-.)?]+\.db$)|(^[\w?(-.)]\.db$))", dbname):
        try:
            maindbname = dbname
            main_db_name_blocker = 1
            main_db_name_result_var.set("SET")
            if db_path_blocker == 1:
                fullpath = usable_real_path
                conn_path_db = os.path.join(usable_real_path, maindbname)
                if os.path.isfile(fullpath + f"\\{maindbname}") or os.path.isfile(
                    fullpath + f"/{maindbname}"
                ):
                    db_already_exists_blocker = 1
                    main_db_conn = ld.Database(conn_path_db,silent_errors=True)
                    main_db_name_result_var.set("CONNECTED")
                    db_display_text.delete("1.0", tk.END)
                    db_display_text.insert(tk.END, f"Connected to {maindbname}..\n\n")
                    success_maindb_connection_blocker = 1
                    encfiletoolbutt.state(["!disabled"])
                    decfiletoolbutt.state(["!disabled"])
                else:
                    db_already_exists_blocker = 0
                    main_db_conn = ld.Database(conn_path_db,silent_errors=True)
                    db_display_text.delete("1.0", tk.END)
                    db_display_text.insert(
                        tk.END,
                        f"Created and Connected to '{maindbname}'.. in the directory '{fullpath}'\n\n",
                    )
                    success_maindb_connection_blocker = 1
                    encfiletoolbutt.state(["!disabled"])
                    decfiletoolbutt.state(["!disabled"])

            else:
                db_display_text.delete("1.0", tk.END)
                db_display_text.insert(
                    tk.END,
                    f"PATH : '{db_path_var.get().strip()}' is not a valid path\n\n",
                )
        except BaseException:
            db_display_text.delete("1.0", tk.END)
            db_display_text.insert(tk.END, "The database might be distorted")
    else:
        main_db_name_result_var.set("NOT SET")
        main_db_name_blocker = 0


def keyd_db_setup():
    global usable_real_path, success_keysdb_connection_blocker, keys_db_conn
    if db_path_blocker == 1 and main_db_name_blocker == 1:
        try:
            dbname = main_db_name_var.get().strip()
            keys_db = dbname[:-3] + "Keys.db"
            dbname_keys_win = "\\" + keys_db
            dbname_keys_unix = "/" + keys_db
            conn_path_keys = os.path.join(usable_real_path, keys_db)
            if db_already_exists_blocker == 1:
                if os.path.isfile(usable_real_path + dbname_keys_win) or os.path.isfile(
                    usable_real_path + dbname_keys_unix
                ):
                    keys_db_conn = ld.Database(conn_path_keys, for_keys=True,silent_errors=True)
                    db_display_text.insert(tk.END, f"Connected to '{keys_db}' ..\n\n")
                    success_keysdb_connection_blocker = 1
                else:
                    keys_db_conn = ld.Database(conn_path_keys, for_keys=True,silent_errors=True)
                    db_display_text.insert(
                        tk.END,
                        f"'{keys_db}' NOT FOUND ! ==> Created and Connected to '{keys_db}' ..\n\n",
                    )
                    success_keysdb_connection_blocker = 1
            else:
                keys_db_conn = ld.Database(conn_path_keys, for_keys=True,silent_errors=True)
                db_display_text.insert(
                    tk.END, f"Created and Connected to '{keys_db}' ..\n\n"
                )
                success_keysdb_connection_blocker = 1
        except BaseException:
            db_display_text.delete("1.0", tk.END)
            db_display_text.insert(tk.END, "The database might be distorted\n")


success_maindb_connection_blocker = 0
success_keysdb_connection_blocker = 0
db_enable_blocker = 0


def path_name_wrapper():
    set_db_path()
    main_db_name()
    keyd_db_setup()
    global db_enable_blocker, success_keysdb_connection_blocker, success_keysdb_connection_blocker
    if success_keysdb_connection_blocker and success_keysdb_connection_blocker:
        db_enable_blocker = 1
        swich_db_toggle.state(["!disabled"])
    else:
        db_enable_blocker = 0
        swich_db_toggle.state(["disabled"])


db_path_var = tk.StringVar()
db_path_entry = tk.Entry(
    master=lowerFrame, width=31, font="Calibre 14 bold", textvariable=db_path_var
)
db_path_entry.place(relx=0.03, rely=0.005)

db_path_result_var = tk.StringVar(value="")
db_path_result_entry = tk.Label(
    master=lowerFrame,
    font="Calibre 13 bold",
    bootstyle="light",
    textvariable=db_path_result_var,
)
db_path_result_entry.place(relx=0.7, rely=0.022)

path_label = tk.Label(
    master=lowerFrame, font="Calibre 13", bootstyle="light", text="PATH"
)
path_label.place(relx=0.47, rely=0.022)

main_database_label = tk.Label(
    master=lowerFrame, font="Calibre 13", bootstyle="light", text="MAIN DATABASE"
)
main_database_label.place(relx=0.47, rely=0.205)

set_db_path_button = tk.Button(
    master=lowerFrame,
    text="SUBMIT PATH AND NAME",
    width=49,
    command=path_name_wrapper,
    bootstyle="light outline",
)
set_db_path_button.place(relx=0.031, rely=0.38)


def checksize():
    global db_enable_blocker, main_db_conn, keys_db_conn
    if db_enable_blocker != 0:
        if swich_db_var.get() == 1:
            conn = keys_db_conn
        else:
            conn = main_db_conn
        size = conn.size
        if size < 1024:
            db_display_text.delete("1.0", tk.END)
            db_display_text.insert(tk.END, f"Current size is {size:.5f} (MB)'\n\n")
        if size >= 1024:
            db_display_text.delete("1.0", tk.END)
            db_display_text.insert(
                tk.END, f"Current size is {(size/1024):.3f} (GB)'\n\n"
            )


size_button = tk.Button(
    master=lowerFrame,
    text="SIZE",
    width=22,
    command=checksize,
    bootstyle="light outline",
)
size_button.place(relx=0.031, rely=0.58)


def checkid():
    global db_enable_blocker, main_db_conn, keys_db_conn
    if db_enable_blocker != 0:
        if swich_db_var.get() == 1:
            conn = keys_db_conn
        else:
            conn = main_db_conn
        try:
            q = conn._query(f"SELECT ID FROM {conn.current_table}")
            idd = 0
            for e in q:
                for k, v in e.items():
                    idd += v[-1][-1][0]
            db_display_text.delete("1.0", tk.END)
            db_display_text.insert(tk.END, f"Last inserted ID is : '{idd}'\n")
            return idd
        except BaseException:
            db_display_text.delete("1.0", tk.END)
            db_display_text.insert(tk.END, "Last inserted ID is : '0'\n")
            return -1


id_button = tk.Button(
    master=lowerFrame,
    text="LAST ID",
    width=22,
    command=checkid,
    bootstyle="light outline",
)
id_button.place(relx=0.247, rely=0.58)


def check_las_mod():
    global db_enable_blocker, main_db_conn, keys_db_conn
    if db_enable_blocker != 0:
        if swich_db_var.get() == 1:
            conn = keys_db_conn
        else:
            conn = main_db_conn
        db_display_text.delete("1.0", tk.END)
        db_display_text.insert(tk.END, f"Last modification at : '{conn.last_mod}'\n")


las_mod_button = tk.Button(
    master=lowerFrame,
    text="LAST MODIFICATION",
    width=49,
    command=check_las_mod,
    bootstyle="light outline",
)
las_mod_button.place(relx=0.031, rely=0.74)


main_db_name_var = tk.StringVar()
main_db_name_entry = tk.Entry(
    master=lowerFrame, width=31, font="Calibre 14 bold", textvariable=main_db_name_var
)
main_db_name_entry.place(relx=0.03, rely=0.192)


main_db_name_result_var = tk.StringVar(value="")
main_db_name_result_entry = tk.Label(
    master=lowerFrame,
    font="Calibre 13 bold",
    bootstyle="light",
    textvariable=main_db_name_result_var,
)
main_db_name_result_entry.place(relx=0.7, rely=0.205)

current_working_db = maindbname


def swich_db():
    global current_working_db
    if db_enable_blocker != 0:
        if swich_db_var.get() == 1:
            switch_db_label_var.set("ON KEYS")
            db_display_text.delete("1.0", tk.END)
            db_display_text.insert(tk.END, "Switched to keys database\n")
            current_working_db = maindbname
        else:
            switch_db_label_var.set("ON MAIN")
            db_display_text.delete("1.0", tk.END)
            db_display_text.insert(tk.END, "Back to default main database\n")
            current_working_db = maindbname[:-3] + "Keys.db"


switch_db_label_var = tk.StringVar(value="SWITCH DATABASE")
switch_db_label = tk.Label(
    master=lowerFrame,
    textvariable=switch_db_label_var,
    bootstyle="light",
    font="Calibre 13",
)
switch_db_label.place(relx=0.52, rely=0.39)


swich_db_var = tk.IntVar(value=0)
swich_db_toggle = tk.Checkbutton(
    bootstyle="light,squared-toggle",
    master=lowerFrame,
    variable=swich_db_var,
    offvalue=0,
    onvalue=1,
    command=swich_db,
)
swich_db_toggle.state(["disabled"])


swich_db_toggle.place(relx=0.47, rely=0.413)

spawning_try_count = 1
actual_spawned_path = ""


def create_spawned_directory():
    global usable_real_path, actual_spawned_path, spawning_try_count
    base_spawned_path = os.path.join(usable_real_path, "spawned")

    while spawning_try_count <= 100:
        spawned_path = base_spawned_path + str(spawning_try_count)
        if not os.path.exists(spawned_path):
            try:
                os.mkdir(spawned_path)
                actual_spawned_path = spawned_path
                break
            except Exception:
                db_display_text.insert(
                    tk.END, f"ERROR CREATING '{spawned_path}' directory!\n"
                )
        else:
            spawning_try_count += 1
            db_display_text.insert(tk.END, f"Trying '{spawned_path}'...\n")
    else:
        db_display_text.insert(
            tk.END, "ABORTING: Reached the maximum number of directories to spawn in.\n"
        )


spawn_out_blocker = 1


def spawn_out():
    global db_enable_blocker, keySelectionFlag, main_db_conn, keys_db_conn, key_ref_entry_var, usable_real_path, actual_spawned_path, spawn_out_blocker

    if db_enable_blocker:
        db_display_text.delete("1.0", tk.END)
        db_display_text.insert(
            tk.END, "ATTEMPTING TO SPAWN OUT FILES IN THE CHOSEN PATH..\n"
        )

        filenames_list = ld.reference_linker(
            connection=main_db_conn,
            key_reference=key_ref_entry_var.get().__str__().strip(),
            get_filename=True,
            get_all=True,
        )
        if len(filenames_list) == 0:
            db_display_text.insert(tk.END, "NO FILES FOUND WITH THIS REFERENCE\n")
        elif not len(filenames_list) == 0:
            db_display_text.insert(tk.END, "FILES FOUND WITH THE GIVEN REFERENCE: \n")
            for file in filenames_list:
                db_display_text.insert(tk.END, f"{file}\n")
            if len(filenames_list) != len(set(filenames_list)):
                create_spawned_directory()
                if spawning_try_count >= 99:
                    spawn_out_blocker = 0
                if spawn_out_blocker:
                    db_display_text.insert(
                        tk.END,
                        f"DUPLICATE FILES DETECTED ! SPAWNING IN '{actual_spawned_path}'"
                        f" UNDER 'IGNORE DUPLICATES FLAG'\n",
                    )
                    try:
                        ld.spawn(
                            main_connection=main_db_conn,
                            keys_connection=keys_db_conn,
                            get_all=True,
                            directory=actual_spawned_path,
                            ignore_duplicate_files=True,
                            key_reference=key_ref_entry_var.get().__str__(),
                        )
                    except Exception:
                        db_display_text.insert(
                            tk.END, f"ERROR OCCURRED DURING FILES RETRIEVAL !'\n"
                        )
                else:
                    return

            elif len(filenames_list) == len(set(filenames_list)):
                create_spawned_directory()
                if spawning_try_count >= 99:
                    spawn_out_blocker = 0
                if spawn_out_blocker:
                    db_display_text.insert(
                        tk.END,
                        f"NO DUPLICATE FILES DETECTED SPAWNING IN '{actual_spawned_path}'\n",
                    )
                    try:
                        ld.spawn(
                            main_connection=main_db_conn,
                            keys_connection=keys_db_conn,
                            get_all=True,
                            key_reference=key_ref_entry_var.get().__str__(),
                            directory=actual_spawned_path,
                        )
                    except Exception:
                        db_display_text.insert(
                            tk.END, f"ERROR OCCURRED DURING FILES RETREIVAL !'\n"
                        )
                else:
                    return


key_ref_entry_var = tk.StringVar()
key_ref_entry = tk.Entry(
    master=lowerFrame, width=11, font="calibre 10 bold", textvariable=key_ref_entry_var
)
key_ref_entry.place(relx=0.484, rely=0.575)

spawn_ref_label = tk.Label(
    master=lowerFrame,
    text="#KEYREF",
    bootstyle="secondary",
    font="Calibre 13",
)
spawn_ref_label.place(relx=0.62, rely=0.58)

spawn_me_button = las_mod_button = tk.Button(
    master=lowerFrame,
    text="SPAWN",
    width=15,
    command=spawn_out,
    bootstyle="secondary outline",
)
spawn_me_button.place(relx=0.47, rely=0.74)


def how_this_works_func():
    global db_display_text
    db_display_text.delete("1.0", tk.END)
    db_display_text.insert(tk.END, gui_usage_manual)


how_to_button = tk.Button(
    master=lowerFrame,
    text="?",
    command=how_this_works_func,
    bootstyle="info outline",
)
how_to_button.place(relx=0.95, rely=0.8)


"""------------TEXT DECRYPTION/ENCRYPTION STARTED--------------"""


def encryption():
    m = text_encryption_var.get()
    if CryptFile.keyverify(mainkeyvar.get()) == 1 and keySelectionFlag.get() == 1:
        if len(m) > 200:
            text_encryption_output_var.set("Too Long")
        else:
            if text_encryption_var.get():
                progressbar_enc.start()
                a = Crypt(m, mainkeyvar.get())
                b = a.encrypt()[1]
                text_encryption_output_var.set(b.__str__())
                if qr_enc_var.get() == 1:
                    tqr(b)


def decryption():
    n = text_decryption_var.get()
    if CryptFile.keyverify(mainkeyvar.get()) == 1 and keySelectionFlag.get() == 1:
        if text_decryption_var.get():
            progressbar_dec.start()
            a = Crypt(n, mainkeyvar.get())
            b = a.decrypt()[1]
            text_decryption_output_var.set(b.__str__())
            if qr_dec_var.get() == 1:
                if not len(b) > 200:
                    tqr(b)


def qr_enc_func():
    if qr_enc_var.get() == 1:
        qr_label_encryption.config(text="QR ON")
    else:
        qr_label_encryption.config(text="QR OFF")


def qr_dec_func():
    if qr_dec_var.get() == 1:
        qr_label_decryption.config(text="QR ON")
    else:
        qr_label_decryption.config(text="QR OFF")


encrypt_text_button = tk.Button(
    master=textFrame1, text="ENCRYPT", command=encryption, bootstyle="light outline"
)
encrypt_text_button.place(relx=0.42, rely=0.73)

decrypt_text_button = tk.Button(
    master=textFrame2, text="DECRYPT", command=decryption, bootstyle="light outline"
)
decrypt_text_button.place(relx=0.42, rely=0.8)

text_encryption_var = tk.StringVar(value="               TEXT")
text_encryption_entry = tk.Entry(
    master=textFrame1,
    width=20,
    font="Calibre 11 bold",
    textvariable=text_encryption_var,
)
text_encryption_entry.place(relx=0.29, rely=0.30)

text_decryption_var = tk.StringVar(value="        CIPHERTEXT")
text_decryption_entry = tk.Entry(
    master=textFrame2,
    font="Calibre 11 bold",
    width=20,
    textvariable=text_decryption_var,
)
text_decryption_entry.place(relx=0.290, rely=0.38)
if platform.system() == "Windows":
    text_encryption_label = tk.Label(
        master=textFrame1,
        text="--------------------------------------------",
        font="Calibre 20",
    )
    text_encryption_label.place(relx=0.01, rely=0.10)
    text_decryption_label = tk.Label(
        master=textFrame2,
        text="--------------------------------------------",
        font="Calibre 20",
    )
    text_decryption_label.place(relx=0.01, rely=0.200)
else:
    text_encryption_label = tk.Label(
        master=textFrame1,
        text="TEXT ENCRYPTION",
        font="Calibre 20 bold",
    )
    text_encryption_label.place(relx=0.190, rely=0.10)
    text_decryption_label = tk.Label(
        master=textFrame2,
        text="TEXT DECRYPTION",
        font="Calibre 20 bold",
    )
    text_decryption_label.place(relx=0.190, rely=0.200)


text_encryption_output_var = tk.StringVar()
text_encryption_output = tk.Entry(
    master=textFrame1, textvariable=text_encryption_output_var, font="terminal 11 bold"
)
text_encryption_output.place(relx=0.02, rely=0.48, width=480, height=50)

text_decryption_output_var = tk.StringVar()
text_decryption_output = tk.Entry(
    master=textFrame2, textvariable=text_decryption_output_var, font="terminal 11 bold"
)
text_decryption_output.place(relx=0.02, rely=0.55, width=480, height=50)


qr_label_encryption = tk.Label(master=textFrame1, text="QR", font=("terminal", 17))
qr_label_encryption.place(relx=0.2, rely=0.75)
qr_enc_var = tk.IntVar()
check_button_enc = tk.Checkbutton(
    bootstyle="success , round-toggle",
    master=textFrame1,
    variable=qr_enc_var,
    offvalue=0,
    command=qr_enc_func,
)

check_button_enc.place(relx=0.1, rely=0.77)


qr_label_decryption = tk.Label(master=textFrame2, text="QR", font=("terminal", 17))
qr_label_decryption.place(relx=0.2, rely=0.82)
qr_dec_var = tk.IntVar()
check_button_dec = tk.Checkbutton(
    bootstyle="success , round-toggle",
    master=textFrame2,
    variable=qr_dec_var,
    offvalue=0,
    command=qr_dec_func,
)

check_button_dec.place(relx=0.1, rely=0.84)


progressbar_enc = tk.Progressbar(
    master=textFrame1,
    mode="indeterminate",
    style="secondary",
    length=100,
)
progressbar_enc.place(relx=0.05, rely=0.34)

progressbar_dec = tk.Progressbar(
    master=textFrame2,
    mode="indeterminate",
    style="secondary",
    length=100,
)
progressbar_dec.place(relx=0.05, rely=0.42)


"""---------FILE ENCRYPTION/DECRYPTION STARTED-------------"""


if platform.system() == "Windows":
    filepathlabel = tk.Label(
        master=frameFile1,
        text="F I L E S",
        font="Calibre 20",
    )
    filepathlabel.place(relx=0.385, rely=0.10)

    resultvarfile = tk.StringVar(value="     -----------------------------------")
    resultLabelfile = tk.Label(
        master=frameFile1, textvariable=resultvarfile, font="terminal 13 bold"
    )
    resultLabelfile.place(rely=0.55)
else:
    filepathlabel = tk.Label(
        master=frameFile1,
        text="FILE PATH",
        font="Calibre 20 bold",
    )
    filepathlabel.place(relx=0.335, rely=0.10)
    resultvarfile = tk.StringVar(value="                    ..........")
    resultLabelfile = tk.Label(
        master=frameFile1, textvariable=resultvarfile, font="terminal 13 bold"
    )
    resultLabelfile.place(rely=0.55)


def enc_file():
    global add_enc_to_db, main_db_conn, mainkey
    if 1:
        if keySelectionFlag.get() != 0:
            filename = filenameStringVar.get().strip()
            key = mainkey
            target = CryptFile(filename, key)
            a = target.encrypt()
            if a == 1:
                filename = filename + ".crypt"
                filenameStringVar.set(filename)
                if platform.system() == "Windows":
                    resultvarfile.set("    Encrypted Successfully / added .crypt")
                else:
                    resultvarfile.set("      Encrypted Successfully / added .crypt")
                if encfiletoolbuttvar.get() == 1:
                    with open(filename, "rb") as f:
                        file_content = f.read()
                    try:
                        main_db_conn.insert(
                            filename, file_content, outputKeyref.get().strip()
                        )
                    except BaseException:
                        db_display_text.delete("1.0", tk.END)
                        db_display_text.insert(
                            tk.END, "ERROR \n\nDatabase might be distorted\n"
                        )
            if platform.system() == "Windows":
                if a == 2:
                    resultvarfile.set("                 File is Empty")
                if a == 3:
                    resultvarfile.set("               File Doesn't Exist")
                if a == 0:
                    resultvarfile.set("                  Can't Encrypt")
                if a == 4:
                    resultvarfile.set("                     ERROR")
                if a == 5:
                    resultvarfile.set("          ERROR : Key is Not 512-bit")
                if a == 6:
                    resultvarfile.set("       ERROR : File is already encrypted")
                elif a == 7:
                    resultvarfile.set(" ERROR : Given a directory instead of a file")
            else:
                if a == 2:
                    resultvarfile.set("                   File is Empty")
                if a == 3:
                    resultvarfile.set("                 File Doesn't Exist")
                if a == 0:
                    resultvarfile.set("                    Can't Encrypt")
                if a == 4:
                    resultvarfile.set("                       ERROR")
                if a == 5:
                    resultvarfile.set("            ERROR : Key is Not 512-bit")
                if a == 6:
                    resultvarfile.set("         ERROR : File is already encrypted")
                elif a == 7:
                    resultvarfile.set("   ERROR : Given a directory instead of a file")


def decfile():
    global add_dec_to_db, main_db_conn, mainkey
    if 1:
        if keySelectionFlag.get() != 0:
            filename = filenameStringVar.get().strip()
            key = mainkey
            target = CryptFile(filename, key)
            a = target.decrypt()
            if a == 1:
                filename = os.path.splitext(filename)[0]
                filenameStringVar.set(filename)
                if platform.system() == "Windows":
                    resultvarfile.set("    Decrypted Successfully + removed .crypt")
                else:
                    resultvarfile.set("     Decrypted Successfully + removed .crypt")
                if decfiletoolbuttvar.get() == 1:
                    with open(filename, "rb") as f:
                        file_content = f.read()
                    try:
                        main_db_conn.insert(
                            filename, file_content, outputKeyref.get().strip()
                        )
                    except BaseException:
                        db_display_text.delete("1.0", tk.END)
                        db_display_text.insert(
                            tk.END, "ERROR \n\nDatabase might be distorted\n"
                        )
            if platform.system() == "Windows":
                if a == 2:
                    resultvarfile.set("                 File is Empty")
                if a == 3:
                    resultvarfile.set("               File Doesn't Exist")
                if a == 0:
                    resultvarfile.set("                 Can't Decrypt")
                if a == 4:
                    resultvarfile.set("                     ERROR")
                elif a == 5:
                    resultvarfile.set("          ERROR : Key is Not 512-bit")
                if a == 6:
                    resultvarfile.set("       ERROR : File is already decrypted")
                elif a == 7:
                    resultvarfile.set(" ERROR : Given a directory instead of a file")
            else:
                if a == 2:
                    resultvarfile.set("                   File is Empty")
                if a == 3:
                    resultvarfile.set("                 File Doesn't Exist")
                if a == 0:
                    resultvarfile.set("                   Can't Decrypt")
                if a == 4:
                    resultvarfile.set("                       ERROR")
                elif a == 5:
                    resultvarfile.set("            ERROR : Key is Not 512-bit")
                if a == 6:
                    resultvarfile.set("         ERROR : File is already decrypted")
                elif a == 7:
                    resultvarfile.set("   ERROR : Given a directory instead of a file")


encryptionfilebutton = tk.Button(
    master=frameFile1,
    text="ENCRYPT FILE",
    command=enc_file,
    bootstyle="light outline",
)
encryptionfilebutton.place(relx=0.25, rely=0.73)

decryptionfilebutton = tk.Button(
    master=frameFile1, text="DECRYPT FILE", command=decfile, bootstyle="light outline"
)
decryptionfilebutton.place(relx=0.53, rely=0.73)

filenameStringVar = tk.StringVar(value="")

filenametext = tk.Entry(
    master=frameFile1, width=31, font="Calibre 15 bold", textvariable=filenameStringVar
)
filenametext.place(relx=0.05, rely=0.30)


addtodbLabel = tk.Label(
    master=frameFile1, text="ADD TO DB", font=("Calibre", 11), bootstyle="light"
)
addtodbLabel.place(relx=0.4, rely=0.908)

add_enc_to_db = 0


def enc_toggle_func():
    global add_enc_to_db
    if encfiletoolbuttvar == 1:
        add_enc_to_db = 1
    else:
        add_enc_to_db = 0


add_dec_to_db = 0


def dec_toggle_func():
    global add_dec_to_db
    if decfiletoolbuttvar == 1:
        add_dec_to_db = 1
    else:
        add_dec_to_db = 0


encfiletoolbuttvar = tk.IntVar()
encfiletoolbutt = tk.Checkbutton(
    bootstyle="warning , round-toggle",
    master=frameFile1,
    variable=encfiletoolbuttvar,
    offvalue=0,
    onvalue=1,
    command=enc_toggle_func,
)
encfiletoolbutt.state(["disabled"])
encfiletoolbutt.place(relx=0.25, rely=0.92)


decfiletoolbuttvar = tk.IntVar()
decfiletoolbutt = tk.Checkbutton(
    bootstyle="warning , round-toggle",
    master=frameFile1,
    variable=decfiletoolbuttvar,
    offvalue=0,
    command=dec_toggle_func,
)
decfiletoolbutt.state(["disabled"])
decfiletoolbutt.place(relx=0.7, rely=0.92)


keySelectionFlag = tk.IntVar(value=0)


def main_key_wrapper():
    global success_keysdb_connection_blocker, mainkey
    if CryptFile.keyverify(mainkeyvar.get().strip()) == 1:
        mainkey = mainkeyvar.get().strip()
        keyref_gen()
        keyselectionvar.set("       SELECTED")
        keySelectionFlag.set(1)
        try:
            if success_keysdb_connection_blocker and os.path.isfile(
                filenameStringVar.get().strip()
            ):
                keys_db_conn.insert(
                    filenameStringVar.get().strip(), mainkey, outputKeyref.get()
                )
            if success_keysdb_connection_blocker and not os.path.isfile(
                filenameStringVar.get().strip()
            ):
                keys_db_conn.insert("STANDALONE", mainkey, outputKeyref.get())
        except BaseException:
            db_display_text.delete("1.0", tk.END)
            db_display_text.insert(tk.END, "Faulty Database\n")
    else:
        keySelectionFlag.set(0)
        keyselectionvar.set("     NOT SELECTED")


if platform.system() == "Windows":
    mainkeyLabel = tk.Label(
        master=frameFile2,
        text="E N C   K E Y",
        font="Calibre 20",
        bootstyle="info",
    )
    mainkeyLabel.place(relx=0.21, rely=0.075)
else:
    mainkeyLabel = tk.Label(
        master=frameFile2,
        text="MAIN KEY",
        font="Calibre 20 bold",
        bootstyle="info",
    )
    mainkeyLabel.place(relx=0.3, rely=0.075)


mainkeyvar = tk.StringVar()
mainkeyEntry = tk.Entry(
    master=frameFile2, font="Calibre 14 bold", textvariable=mainkeyvar, width=29
)
mainkeyEntry.place(relx=0.09, rely=0.29)


def keyref_gen():
    ref = "#"
    for _ in range(6):
        character = secrets.choice(
            string.ascii_letters
            + string.digits
            + "$"
            + "?"
            + "&"
            + "@"
            + "!"
            + "-"
            + "+"
        )
        ref += character
    outputKeyref.set(ref)


outputKeyref = tk.StringVar(value="#KEYREF")
keyrefLabel = tk.Label(
    master=frameFile2,
    textvariable=outputKeyref,
    bootstyle="secondary",
    font=("terminal", 12),
)
keyrefLabel.place(relx=0.712, rely=0.12)

keySelectButton = tk.Button(
    master=frameFile2,
    text="SELECT KEY",
    command=main_key_wrapper,
    bootstyle="info outline",
)
keySelectButton.place(relx=0.6725, rely=0.5)


keyselectionvar = tk.StringVar(value="   KEY NOT SELECTED")
keyselectionLabel = tk.Label(
    master=frameFile2,
    textvariable=keyselectionvar,
    bootstyle="info",
    font="terminal 11",
)
keyselectionLabel.place(relx=0.15, rely=0.465, height=50)


def genkey():
    keyGenVar.set(CryptFile.genkey())


keyGenVar = tk.StringVar(value="")
keyGenEntry = tk.Entry(
    master=frameFile2, font="Calibre 12 bold", textvariable=keyGenVar, width=23
)
keyGenEntry.place(relx=0.1, rely=0.69)

keyButton = tk.Button(
    master=frameFile2, text="GENERATE", command=genkey, bootstyle="success outline"
)
keyButton.place(relx=0.671, rely=0.7)


def rm_json():
    global usable_real_path
    file = os.path.join(usable_real_path, "output.json")
    if os.path.exists(file):
        os.remove(file)


atexit.register(rm_json)


if __name__ == "__main__":
    main_object.mainloop()
