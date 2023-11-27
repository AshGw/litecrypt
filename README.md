![alt text](docs/assets/widelogo1.png)
![workflow](https://github.com/ashgw/litecrypt/actions/workflows/deploy.yaml/badge.svg)
[![Static Badge](https://img.shields.io/badge/Docs-latest-%237e56c2)](https://ashgw.github.io/litecrypt)
[![Python Versions](https://img.shields.io/badge/Python-3.8%7C3.9%7C3.10%7C3.11%7C3.12-blue)](https://pypi.org/project/litecrypt/)
[![Static Badge](https://img.shields.io/badge/PyPI-latest-brightgreen)](https://pypi.org/project/litecrypt/)

## Overview
I made this library for personal use to secure some files. It provides support for both fast and highly computationally intensive encryption. Also, it includes a database integration system . This system facilitates the restoration of files to their original state if necessary, and a graphical user interface (GUI) is also included to obviate the need to write code.

## Installation
```shell
pip install litecrypt
```
## Usage

```python
from litecrypt import CryptFile, gen_key

key = gen_key()
CryptFile('file_of_any.type', key).encrypt()
# the file is now called ==> 'file_of_any.type.crypt
```
The encryption process is **blazingly fast** by default, to make it computationally intensive
<details><summary>Do this</summary>

```python
from litecrypt import CryptFile, gen_key

key = gen_key()
CryptFile('anyfile.txt',
          key=key,
          intensive_compute=True,
          iteration_rounds=10000
          ).encrypt()
```
> Running `intensive_compute` with no `iteration_rounds` sets the rounds to 50 (minimum) by default

To decrypt simply run:


```python
from litecrypt import CryptFile

key = 'THE_KEY_YOU_USED'
CryptFile('anyfile.txt.crypt',key=key).decrypt()
```
</details>


For messages:
```python
from litecrypt import Crypt, gen_key

key = gen_key()
encrypted = Crypt('any message', key).encrypt()  # can also be a bytes message
print(encrypted)  # Check the return value
```

### Details
<br>**Algorithm:** AES-256 CBC
<br>**Layout:**
````commandline
+-------------+  +--------+  +------------+  +-------------+  +-------------+  +------------------+
|    HMAC     | →|   IV   | →|   Salt     | →|  Pepper     | →| Iterations  | →|     KDF ID     |  →
+-------------+  +--------+  +------------+  +-------------+  +-------------+  +------------------+
                              +------------------+
                              |   Ciphertext    ...
                              +------------------+
````

The main key which is a 32-byte random hex string is provided by `gen_key()` function.

> *The higher the number of iterations, the longer it takes to encrypt/decrypt.*

- **AES Key:** 32-byte random value derived from the main key with the KDF, hashed with SHA256 (1 time or [50..100000] times based on the chosen number of iterations) mixed with the Salt.
- **HMAC Key:** 32-byte random value derived from the main key with  the KDF, hashed with SHA256 (1 time or [50..100000] times based on the chosen number of iterations) mixed with the Pepper.
- **IV:** 16-byte random value.
- **Salt:** 16-byte random value.
- **Pepper:** 16-byte random value.
- **Iterations:** 4-byte fixed value.
- **KDF ID:** 4-byte fixed value used to auto-determine the Key Derivation Function (KDF) to use.
- **Ciphertext:** Variable size.


<h3>Supported Databases</h3>

Currently, supports MySQL, PostgresSQL and SQLite.
<br>Check the  **[docs](https://ashgw.github.io/litecrypt)** for more info.

###  GUI

![alt text](docs/assets/GUI.png)

<details><summary>Here's how it works</summary>

https://github.com/AshGw/litecrypt/assets/126174609/190b6ab8-3f8a-4656-9525-dbaf5e56db5e

</details>


## License

Litecrypt is open-source project & licensed under the [MIT License](https://github.com/AshGw/litecrypt/blob/main/LICENSE).
