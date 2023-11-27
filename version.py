import re

with open("pyproject.toml") as f:
    content = f.read()

version_match = re.search(r'version="(\d+\.\d+\.\d+)"', content)
print(version_match.group(1))
