![alt text](assets/widelogo1.png)
![workflow](https://github.com/ashgw/litecrypt/actions/workflows/deploy.yaml/badge.svg)
[![Static Badge](https://img.shields.io/badge/Docs-latest-%237e56c2)](https://ashgw.github.io/litecrypt)
[![Python Versions](https://img.shields.io/badge/Python-3.7%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)](https://pypi.org/project/litecrypt/)
[![Static Badge](https://img.shields.io/badge/PyPI-v0.0.1-brightgreen)](https://pypi.org/project/litecrypt/)
---

## Litecrypt

Library that provides a simple solution for encrypting and decrypting files and messages, as well as keeping track of them.

## Example Usage

### Encrypting data
```py linenums="1"
from litecrypt import Crypt , gen_key

key = gen_key()

data = b'some random data'
message = 'some random message'

encrypted_data = Crypt(data,key).encrypt()
encrypted_message = Crypt(message,key).encrypt()

message_again = Crypt(encrypted_message,key).decrypt()
print(message_again)
```

### Encrypting Files
```py linenums="1"
from litecrypt import CryptFile, gen_key

# Create a file to see how it works
CryptFile.make_file(filename='notes.txt',content='hello there')

key = gen_key()
CryptFile('notes.txt',key=key).encrypt(echo=True)
CryptFile('notes.txt.crypt',key=key).decrypt(echo=True)
# echo, to display progress in the console
```

### Database usage


Let's say we have 3 files: `file`, `image.png`, and `notes.txt` in a directory called `test`:

```python
files = ['test/file', 'test/image.png', 'test/notes.txt']
```
<details><summary>Click me to make them</summary>

```python
import os
from litecrypt import CryptFile

# Create a directory for testing
os.mkdir('test')

# Create sample files
files = ['test/file', 'test/image.png', 'test/notes.txt']
file_contents = [b'some data', b'binary data of some image', b'some notes']

for file, content in zip(files, file_contents):
    CryptFile.make_file(filename=file, content=content)

# The files now exist in the directory test/
```
</details>

Leave the files in there, take a **copy** of their content, encrypt it, and store it in a database.
<br>You never know when you'll need them.
<details><summary>Collect the content</summary>

```python
file_contents = []
for file in files:
    file_content = CryptFile.get_binary(file)
    file_contents.append(file_content)

```
</details>

</details>
<details><summary>Encrypt each file content</summary>

```python
from litecrypt import Crypt, gen_key

key = gen_key()
encrypted_contents = []
for content in file_contents:
    encrypted_content = Crypt(content, key).encrypt(get_bytes=True)
    encrypted_contents.append(encrypted_content)
```
</details>

With a **copy** of the content encrypted we need storage

```python
from litecrypt import Database, gen_ref

# Create & connect to the databases (sqlite for now)
main_db = Database('secure_vault.db')
keys_db = Database('secure_vaultKeys.db',for_keys=True)

# Generate a key reference value to link up the two databases with
key_ref = gen_ref()

# Insert encrypted content and keys into the databases
for file, encrypted_content in zip(files, encrypted_contents):
    main_db.insert(filename=f'does-not-matter/{file}.crypt', content=encrypted_content, ref=key_ref)
    keys_db.insert(filename=f'does-not-matter/{file}.crypt', content=key, ref=key_ref)
# Add .crypt to indicate they're encrypted
```

Done! The files are still in `test/`, but you now have encrypted copies of them in the main database.
<br>The keys used for encryption are stored in the keys database.
<br>You can encrypt your keys database too, but for this demo, let it be as is.

**✈️  You're somewhere else now. How do you get the files back?**
<br>Let's simulate this by creating another directory, which we'll call `spawned`:
```python
os.mkdir('spawned')
```
Now, retrieve the files:

```py linenums="1"
from litecrypt import spawn

main_db = ... #  your Database connection instance
keys_db = ... # Your Database connection instance for keys
key_ref = ... # The reference value used for the file/key combo used

spawned = spawn(main_connection=main_db,
                       keys_connection=keys_db,
                       key_reference=key_ref,
                       directory='spawned',
                       get_all=True,
                       echo=True)
```

That's it! They exist now in the 'spawned/' directory, encrypted though like we put them.

How about we decrypt them ?

```python
for file, key in zip(spawned['filenames'], spawned['keys']):
    CryptFile(file, key).decrypt(echo=True)
```
The files are retrieved and decrypted. Check if the files in `test/` match the files in `spawned/`.
<details><summary>Here's the full demo</summary>

```py linenums="1"
import os

from litecrypt import Crypt, CryptFile, Database, gen_key, gen_ref, spawn

# Create a directory for testing
os.mkdir("test")

# Create sample files
files = ["test/file", "test/image.png", "test/notes.txt"]
file_contents = [b"some data", b"binary data of some image", b"some notes"]

for file, content in zip(files, file_contents):
    CryptFile.make_file(filename=file, content=content)

# The files now exist in the directory test/

# Collect each file's content
file_contents = []
for file in files:
    file_content = CryptFile.get_binary(file)
    file_contents.append(file_content)

# Encrypt each file's content one by one
key = gen_key()
encrypted_contents = []
for content in file_contents:
    encrypted_content = Crypt(content, key).encrypt(get_bytes=True)
    encrypted_contents.append(encrypted_content)

# Initialize the main & the associated keys database
main_db = Database("secure_vault.db")
keys_db = Database("secure_vaultKeys.db",for_keys=True)  # Specify it's for keys

# Generate a key reference value to link up the two databases with
key_ref = gen_ref()

# Insert encrypted content and keys into the databases
for file, encrypted_content in zip(files, encrypted_contents):
    main_db.insert(
        filename=f"does-not-matter/{file}.crypt", content=encrypted_content, ref=key_ref
    )
    keys_db.insert(filename=f"does-not-matter/{file}.crypt", content=key, ref=key_ref)
# Add .crypt to indicate they're encrypted

# Create another directory
os.mkdir("spawned")

# The files will now pop into existence in this new directory
spawned = spawn(
    main_connection=main_db,
    keys_connection=keys_db,
    key_reference=key_ref,
    directory="spawned",
    get_all=True,
    echo=True,
)

# Decrypt them
for file, key in zip(spawned["filenames"], spawned["keys"]):
    CryptFile(file, key).decrypt(echo=True)
```

</details>


### Supported Databases

The library currently supports: MySQL, PostgreSQL and SQLite.
> **Note:** The GUI only support SQLite
#### How To Connect ?
**SQLite**: Specify the file name of the database, it must end with either `.db` or `.sqlite`
```Py
from litecrypt import Database
main_connection = Database('test.db')
keys_connection = Database('somekeysdatabase.db',for_keys=True)
```
By default, every database connection defaults to main, set the parameter `for_keys=True` to let the underlying process know this is used for keys, this is mando to retrieve files based on reference.

**PostgreSQL**:
<br>
Plug in the coordinates  as the url.
```Py
from litecrypt import Database

main_conn = Database(url='username:password@host:port/database',
                     engine_for='postgres',
                     echo=True)
```
The echo parameter is optional, it shows what's happening behind the scenes.

**MySQL**:<br>
Same as PostgreSQL except the engine is different.
```Py
from litecrypt import Database

main_conn = Database(url='username:password@host:port/database',
                     engine_for='mysql',
                     echo=True)
```


###  Why Use Reference ?
The reference value, such as `#8jX?7c`, remains independent of both the encrypted data and the encryption keys. It does not reveal any information about the keys used or the encrypted data itself. Instead, its purpose is to establish a connection between the two databases, consistently linking each file to its corresponding key.

The primary database holds the filenames and their encrypted data, while the keys database stores the filenames and the keys used to encrypt them. To recover files, both databases need to be simultaneously accessible. However, a crucial point to note is that robust security for the keys database is necessary only when BOTH databases are accessible together.

If someone gets hold of the main database, they'll only get dog shit. Trying to break the content would be really hard. On the other hand, if someone only accesses the keys database, they'll only find keys and filenames. It won't help much.

You can keep the databases separate (though that might be hard and impractical) or make copies of your main database—regardless of your level of trust in the system you place them in.

In this situation, the keys database should be kept safe, preferably encrypted. When you want your files back, get your main database from wherever you stored it. Then, use the keys database to unlock the files you need.

The process of getting files back really simple, actually it's just one function called `spawn()`

## All In One App
Wait... Install the library first
