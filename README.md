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

Currently, supports MySQL, PostgresSQL and SQLite.

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

Confused ? check the **[Docs](https://ashgw.github.io/litecrypt)**.

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
