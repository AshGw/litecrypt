from litecrypt.mapper.database import Database, reference_linker, spawn

ref = "#i3LJ9?"
key = "172aec5b549cec15a55b6deb5a24c5016f760437b461f928661677e22c6e8df4"
main_connection = Database("test.db", echo=True)
keys_connection = Database("testKeys.db", echo=True, for_keys=True)


main_connection.insert(filename="gomehow.py", ref=ref, content=b"zer")
print(main_connection.columns)
for gen in main_connection.content():
    print(gen)

print(main_connection.content_by_id(1))
print()
res = reference_linker(
    connection=main_connection, key_reference=ref, get_content_or_key=True
)
print(res)
print()
res = reference_linker(
    connection=main_connection, key_reference=ref, get_filename=True, get_all=True
)
print(res)


keys_connection.insert(filename="dumb.py", ref=ref, content=key)
print(keys_connection.columns)
for gen in keys_connection.content():
    print(gen)

print(keys_connection.content_by_id(1))
print()
res = reference_linker(
    connection=keys_connection, key_reference=ref, get_content_or_key=True
)
print(res)
print()
res = reference_linker(
    connection=keys_connection, key_reference=ref, get_content_or_key=True, get_all=True
)
print(res)
print("\naliefghftyftfyyftyftyfudtdtrsresezs\n\n")
print("\naliefghftyftfyyftyftyfudtdtrsresezs\n\n")
print("\naliefghftyftfyyftyftyfudtdtrsresezs\n\n")
print("\naliefghftyftfyyftyftyfudtdtrsresezs\n\n")

a = main_connection.session.execute(statement="SELECT ID FROM stashmain").fetchall()
print(a)

spawn(
    echo=True,
    key_reference=ref,
    main_connection=main_connection,
    keys_connection=keys_connection,
    get_all=False,
    ignore_duplicate_files=True,
)

print(keys_connection.current_table)
print(main_connection.current_table)

q = main_connection._query("SELECT ID FROM STASHMAIN")
print("This is q")
print(q)
idd = 0
for e in q:
    for k, v in e.items():
        idd += v[-1][-1][0]
print(idd)

buffer = {}
e = main_connection.content_by_id(1)
buffer["ID_" + e[0].__str__()] = [
    {"filename": e[1]},
    {"content": e[2].__str__()},
    {"ref": e[3]},
]
print(buffer)


print(main_connection._query("SELECT ID FROM StashMain"))

buffer = {}
for e in main_connection.content():
    buffer["ID_" + e[0].__str__()] = [
        {"filename": e[1]},
        {"content": e[2].__str__()},
        {"ref": e[3]},
    ]
print(buffer)


keys_connection.end_session()
main_connection.end_session()
