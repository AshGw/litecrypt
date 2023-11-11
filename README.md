![alt text](docs/assets/widelogo1.png)
![workflow](https://github.com/ashgw/litecrypt/actions/workflows/deploy.yaml/badge.svg)
[![Static Badge](https://img.shields.io/badge/Docs-latest-%237e56c2)](https://ashgw.github.io/litecrypt)
[![Python Versions](https://img.shields.io/badge/Python-3.7%7C3.8%7C3.9%7C3.10%7C3.11%7C3.12-blue)](https://pypi.org/project/litecrypt/)
[![Static Badge](https://img.shields.io/badge/PyPI-latest-brightgreen)](https://pypi.org/project/litecrypt/)



## 🔒 Encryption & Data Storage Made Simple

**Embed in Code**: Easily integrated into your existing codebase with just a few lines.

**Use the GUI**: Enjoy the full functionality of the library through the intuitive GUI.

## 🧙‍♂️ Installation

Starting is a breeze. Just use pip:
```shell
pip install litecrypt
```

## 🔑 Effortlessly Secure Encryption!

```python
from litecrypt import CryptFile, gen_key

key = gen_key()
CryptFile('accounts.csv', key).encrypt()
# Voila! Your file is now called ==> accounts.csv.crypt
```
The encryption process is **blazingly fast** by default, but you can choose to make it computationally intensive
<details><summary>How ?</summary>

```python
from litecrypt import CryptFile, gen_key

key = gen_key()
CryptFile('anyfile.txt',
          key=key,
          intensive_compute=True,
          iteration_rounds=10000
          ).encrypt()
```
To decrypt simply run:


```python
from litecrypt import CryptFile

key = 'THE_KEY_YOU_USED'
CryptFile('anyfile.txt.crypt',key=key).decrypt()
```
</details>


Need to protect a message?
```python
from litecrypt import Crypt, gen_key

key = gen_key()
encrypted = Crypt('any message', key).encrypt()
print(encrypted)  # Check the return value
```


## 💾 Database Integration
<h3>Databases</h3>

Currently, supports MySQL, PostgreSQL and SQLite, check the [docs](https://ashgw.github.io/litecrypt) for more info.

<h3>Example Usage</h3>

```python
from litecrypt import CryptFile, Database, gen_key, gen_ref

files = ["file", "image.png", "notes.txt"]

encryption_key = gen_key()
print(encryption_key) # check it out

# encrypt files
for file in files:
    CryptFile(file,key=encryption_key).encrypt(echo=True)
    # each one of these files ends with .crypt now

same_files_but_with_crypt_extension = ["file.crypt",
                                       "image.png.crypt",
                                       "notes.txt.crypt"]

# Create & connect to the databases (sqlite for now)
main_db = Database('xyz_main.db',echo=True)
keys_db = Database('xyz_keys.db',for_keys=True,echo=True)

# To link up the two databases generate a:
reference_value = gen_ref()
print(reference_value) # check it out

for encrypted_file_name in same_files_but_with_crypt_extension:
    with open(encrypted_file_name,'rb') as f:
        encrypted_file_binary_content = f.read()
        # Insert encrypted content and keys into the databases
        # & link'em up with a ref value
        main_db.insert(encrypted_file_name,
                       encrypted_file_binary_content,
                       ref=reference_value)
        keys_db.insert(encrypted_file_name,
                       encryption_key,
                       ref=reference_value)
```

Here's what's happening:

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

Done! Your files are still in `test/`, but you now have encrypted copies of them in the main database.
<br>The keys used for encryption are stored in the keys database.
<br>You can encrypt your keys database too, but for this demo, let it be as is.

**✈️  You're somewhere else now. How do you get the files back?**
<br>Let's simulate this by creating another directory, which we'll call `spawned`:
```python
os.mkdir('spawned')
```
Now, retrieve the files:
```python
from litecrypt import spawn

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
Your files are retrieved and decrypted. Check if the files in `test/` match the files in `spawned/`.
<details><summary>Here's the full demo</summary>

```python
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

That's it! Try this yourself and see the output in the terminal.

## 🚀 Or, Simplify with the GUI

![alt text](docs/assets/GUI.png)

**The place where everything comes together, a user-friendly graphical user interface that combines the library's power into one easy-to-use app.**

<details><summary>Check the GUI demo</summary>

https://github.com/AshGw/litecrypt/assets/126174609/190b6ab8-3f8a-4656-9525-dbaf5e56db5e

</details>


## 📚 Documentation

Check out the **[Docs](https://ashgw.github.io/litecrypt)**.



## 🔐 License

Litecrypt is open-source and licensed under the [MIT License](https://github.com/AshGw/litecrypt/blob/main/LICENSE).
