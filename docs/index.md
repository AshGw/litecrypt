![alt text](assets/widelogo1.png)
![workflow](https://github.com/ashgw/litecrypt/actions/workflows/deploy.yaml/badge.svg)
[![Static Badge](https://img.shields.io/badge/Docs-latest-%237e56c2)](https://ashgw.github.io/litecrypt)
[![Python Versions](https://img.shields.io/badge/Python-3.7%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)](https://pypi.org/project/litecrypt/)
[![Static Badge](https://img.shields.io/badge/PyPI-v0.0.1-brightgreen)](https://pypi.org/project/litecrypt/)
---

## Welcome to Litecrypt

Litecrypt is a minimal library that provides a simple solution for encrypting and decrypting data and files. Prioritizing both security and ease of use, by employing AES-256 encryption in CBC mode. The library offers the added benefit of secure storage, ensuring the protection of sensitive information. For those seeking a user-friendly experience, an accompanying graphical user interface is also available.

## Key Features
- **Minimalism:** It's all about simplicity. No convoluted code, no more wrestling with complex and unintuitive crypto libraries. You can achieve more with less.
- **User-Friendly App:** Even if you don't want to write code, an app is available.
- **Built on Proven Security Foundations:** By using well established cryptographic primitives sourced from the renowned 'cryptography' library, ensuring a foundation of rock-solid security.
- **Great Editor Support:**  Navigating through Litecrypt is a breeze with intuitive code completion, instant contextual documentation, and interactive examples.


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

```py linenums="1"
from litecrypt import Crypt, CryptFile, Database, gen_key, gen_ref

# Create connections to the main and keys databases
main_conn = Database('vault.db')
keys_conn = Database('vaultKeys.db')

# Specify the filename you want to store in the database
filename = 'notes.csv'

# Get the binary data content of the specified file
file_data = CryptFile.get_binary(filename)

# Generate an encryption key and a reference value
encryption_key = gen_key()
reference_value = gen_ref()

# Encrypt the file data using the encryption key
encrypted_file_data = Crypt(data=file_data, key=encryption_key).encrypt()

# Insert the encrypted file data, content reference, and encryption key into the main database
main_conn.insert(filename=filename + '.crypt',
                 content=encrypted_file_data,
                 ref=reference_value)

# Insert the encryption key and reference into the keys database
keys_conn.insert(filename=filename + '.crypt',
                 content=encryption_key,
                 ref=reference_value)

```

The reference value, such as `#8jX?7c`, remains independent of both the encrypted data and the encryption keys. It does not reveal any information about the keys used or the encrypted data itself. Instead, its purpose is to establish a connection between the two databases, consistently linking each file to its corresponding key.

The primary database holds the filenames and their encrypted data, while the keys database stores the filenames and the keys used to encrypt them. To recover files, both databases need to be simultaneously accessible. However, a crucial point to note is that robust security for the keys database is necessary only when BOTH databases are accessible together.

If someone gets hold of the main database, they'll only get some encrypted content and file names. Trying to break this content would be really hard. On the other hand, if someone only accesses the keys database, they'll only find keys and filenames. It won't help them much.

You have two options: keep the databases separate (though that might be hard and impractical) or make copies of your main database—regardless of your level of trust in the system you place them in.

In this situation, the keys database should be kept safe, preferably encrypted. When you want your files back, get your main database from wherever you stored it. Then, use the keys database to unlock the files you need.

I've made the process of getting files back really simple, actually it's just one function called `spawn()`.

Here's a complete workflow on how Litecrypt might be used, check this out:

### Demo
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
keys_db = Database("secure_vaultKeys.db")  # to hold the keys

# Generate a key reference value to link up the two databases with
key_ref = gen_ref()

# Insert encrypted content and keys into databases
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

The demonstration highlights a practical use case of Litecrypt. The process of securing and recovering encrypted files becomes incredibly straightforward. The demo outlines how to extract and encrypt data from files, establish connections between two databases by associating files and their respective keys using reference values to securely manage keys and file data. It briefly illustrates how  significantly simple the task of safeguarding data is.
<br>Feel free to copy this demo and observe the output in your terminal.

If you don't want to deal with code here's an
## All In One App
Wait... Install the library first
