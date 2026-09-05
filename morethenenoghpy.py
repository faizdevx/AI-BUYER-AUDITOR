"""
PYTHON REVISION NOTES
=====================


1. VARIABLES, LISTS, DICTS
==========================

Variable revise done.

List revise done.

Dictionary revise done.


2. TYPE HINTS
=============

Type hints are nothing but specifying the particular
datatype of a variable.

Example:

name: str = "hello"

age: int = 23

student: dict[str, str] = {
    "name": "john",
    "age": 23
}

skills: list[str] = ["Python", "AI"]


Function type hint:

def greet(a: str):
    return f"Hello, {a}!"


PARAMETER VS ARGUMENT
---------------------

When a variable inside the function definition has no value:

def greet(a):
    ...

'a' is called a PARAMETER.

When we call the function and give a value:

greet("Faizal")

"Faizal" is called an ARGUMENT.


3. DEFAULT ARGUMENTS
====================

We can give a parameter a default value.

Example:

def greet(a="hello"):
    print(a)

If we call:

greet()

The default value is automatically used:

hello

If we call:

greet("Faizal")

Then the provided value is used instead of the default.


4. *args
=========

When we want to accept multiple positional arguments,
we can use *args.

Example:

def total(*args):
    print(args)

total(10, 20, 30)

Output:

(10, 20, 30)

Important:

*args -> tuple

So multiple positional arguments are collected into a tuple.


5. **kwargs
===========

**kwargs is used for multiple named arguments.

Example:

def profile(**kwargs):
    print(kwargs)

profile(
    name="Faizal",
    age=20,
    role="student"
)

Output:

{
    "name": "Faizal",
    "age": 20,
    "role": "student"
}

Important:

**kwargs -> dictionary


6. CLASSES
==========

Basic class:

class Animal:

    def __init__(self, name):
        self.name = name

    def speak(self):
        return f"{self.name} makes a sound"


__init__
--------

__init__ acts as a constructor.

It runs automatically when an object is created.

Example:

animal = Animal("Tom")


Instance Method
---------------

Example:

def speak(self):
    return f"{self.name} makes a sound"

'speak' is an instance method because it works
with the particular object.


7. INHERITANCE
==============

Basic inheritance:

class Dog(Animal):

    def speak(self):
        return f"{self.name} barks"


Dog inherits from Animal.

The speak() method inside Dog replaces the
speak() method inherited from Animal.

This is called:

METHOD OVERRIDING.


8. LIST COMPREHENSION
====================

Basic structure:

[expression for item in iterable]


Example:

even_numbers = [
    n
    for n in range(10)
    if n % 2 == 0
]


Odd numbers:

odd_numbers = [
    i
    for i in range(10)
    if i % 2 != 0
]


Basic idea:

loop
  +
condition
  +
create result


9. DICTIONARY COMPREHENSION
===========================

Dictionary comprehensions also exist.

Example:

squares = {
    n: n * n
    for n in range(6)
}


Result:

{
    0: 0,
    1: 1,
    2: 4,
    3: 9,
    4: 16,
    5: 25
}

Not studying this too deeply for now.


10. if __name__ == "__main__"
=============================

Basic pattern:

def main():
    print("Program started")


if __name__ == "__main__":
    main()


The main() function runs when the file is
executed directly.


11. PROJECT STRUCTURE + __init__.py
===================================

Suppose project structure is:

my_project/
│
├── my_package/
│   ├── __init__.py
│   ├── file1.py
│   └── file2.py
│
└── pipeline.py


file1.py
--------

Contains func1:

def func1():
    ...


file2.py
--------

Contains func2:

def func2():
    ...


__init__.py
-----------

from .file1 import func1
from .file2 import func2


This allows cleaner imports from the package.


pipeline.py
-----------

from my_package import func1, func2


def run_pipeline():

    step1 = func1()

    final_result = func2(step1)

    print(final_result)


if __name__ == "__main__":

    print("Starting the pipeline...")

    run_pipeline()


The idea:

pipeline.py
    |
    v
my_package
    |
    +---- file1.py -> func1
    |
    +---- file2.py -> func2


12. FILE I/O
============

READING A FILE
--------------

with open("file.txt", "r") as file:

    content = file.read()

print(content)


WRITING TO A FILE
-----------------

with open("hello.txt", "w", encoding="utf-8") as file:

    file.write("Hello Python\n")

    file.write("This is a file.")


Important:

with open(...)

automatically closes the file after the
block is executed, even if an error occurs.


13. JSON
========

Python dictionary:

student = {
    "name": "Faizal",
    "age": 20,
    "skills": ["Python", "AI"]
}


Import JSON:

import json


json.dump()
-----------

Python object -> file


with open("student.json", "w", encoding="utf-8") as file:

    json.dump(student, file, indent=2)


json.load()
-----------

file -> Python object


with open("student.json", "r", encoding="utf-8") as file:

    student = json.load(file)

print(student)


Remember:

json.dump() -> Python object -> file

json.load() -> file -> Python object


14. EXCEPTION HANDLING
======================

Basic try/except:

try:

    number = int(input("Enter a number: "))

except ValueError:

    print("Please enter a valid integer.")


If the entered value cannot be converted
into an integer, ValueError is caught.


15. finally
===========

finally always runs.

Example:

try:

    print("Trying something")

except ValueError:

    print("Something went wrong")

finally:

    print("This always runs")


Output:

Trying something
This always runs


Basic structure:

try:
    ...

except SomeError:
    ...

finally:
    ...


16. CUSTOM EXCEPTIONS
====================

We can create our own exceptions.

class InvalidAgeError(Exception):
    pass


Then:

def validate_age(age):

    if age < 0:

        raise InvalidAgeError("Age cannot be negative")


Flow:

invalid condition
        |
        v
raise custom exception
        |
        v
except catches it


17. os
======

We can work with paths and environment
variables using os.

import os


Current working directory:

print(os.getcwd())


Environment variable:

print(os.environ.get("HOME"))


18. pathlib
===========

Import:

from pathlib import Path


Create directory path:

data_dir = Path("data")


Create JSON file path:

json_path = data_dir / "student.json"


The / operator is used to combine paths.

Example:

data_dir / "student.json"

This creates a Path object representing:

data/student.json

On Windows it may appear using backslashes.


19. AUTOMATED FILE ORGANIZER
============================

Example using pathlib:

from pathlib import Path


target_dir = Path("./my_downloads")


CATEGORY_MAPPING = {

    ".pdf": "Documents",

    ".docx": "Documents",

    ".txt": "Documents",

    ".jpg": "Images",

    ".png": "Images",

    ".mp3": "Audio",

    ".wav": "Audio",
}


Create target directory:

target_dir.mkdir(exist_ok=True)


Function:

def organize_folder(folder: Path):

    for item in folder.iterdir():

        if item.is_dir():
            continue

        file_extension = item.suffix.lower()

        if file_extension in CATEGORY_MAPPING:

            category_name = CATEGORY_MAPPING[file_extension]

            destination_folder = folder / category_name

            destination_folder.mkdir(exist_ok=True)

            new_destination = destination_folder / item.name

            item.rename(new_destination)

            print(
                f"Moved: {item.name} -> {category_name}/"
            )


Run:

organize_folder(target_dir)


Important pathlib methods:

iterdir()
----------

Loops through items inside a folder.


is_dir()
--------

Checks whether an item is a directory.


suffix
------

Gets the file extension.

Example:

item.suffix

".jpg"


rename()
--------

Moves the file.

item.rename(new_destination)


What does this do?

destination_folder = folder / category_name


Example:

folder:
my_downloads

category_name:
Images


Result:

my_downloads / Images


On Windows it may appear as:

Windows\my_downloads\Images


20. dotenv + ENVIRONMENT VARIABLES
==================================

Import:

from dotenv import load_dotenv

import os


Load the .env file:

load_dotenv()


Read environment variable:

api_key = os.getenv("API_KEY")


Example .env:

API_KEY=abc123


Important:

Add:

.env

to:

.gitignore

so secrets are not accidentally committed.


21. uv
======

Initialize a project:

uv init --name python-teacher-lab --python 3.13


Add a dependency:

uv add requests


The dependency is recorded in:

pyproject.toml


And the lock file:

uv.lock


Run application:

uv run python main.py


This is the workflow to get used to:

uv init
uv add
uv run


Development dependency:

uv add --dev pytest


Run pytest:

uv run pytest


22. requirements.txt
====================

With uv, the main project files are:

pyproject.toml

uv.lock


Export requirements.txt:

uv export --format requirements.txt


Meaning:

pyproject.toml
    ->
project configuration + declared dependencies


uv.lock
    ->
exact locked dependency versions


requirements.txt
    ->
compatibility/export format


23. TYPE HINTS - REVISION
========================

Basic:

name: str

age: int

height: float


Function:

def greet(name: str) -> str:

    return f"Hello {name}"


Meaning:

name: str

The parameter is expected to be a string.


-> str

The function is expected to return a string.


List:

skills: list[str] = ["Python", "AI"]


Meaning:

skills is a list containing strings.


Dictionary:

from typing import Any


student: dict[str, Any] = {

    "name": "Faizal",

    "age": 20,

    "skills": ["Python", "AI"]

}


dict[str, Any]

means:

keys   -> str
values -> anything


24. Optional
============

You might encounter:

from typing import Optional


def find_user(user_id: int) -> Optional[str]:
    ...


This means:

returns str OR None


Modern Python can also write:

def find_user(user_id: int) -> str | None:
    ...


So:

Optional[str]

and:

str | None

represent the same basic idea.


QUICK REVISION
==============

VARIABLES
    |
    +-- str
    +-- int
    +-- float
    +-- bool
    +-- list
    +-- dict


FUNCTIONS
    |
    +-- parameter
    +-- argument
    +-- default argument
    +-- *args      -> tuple
    +-- **kwargs   -> dict


OOP
    |
    +-- class
    +-- __init__
    +-- instance method
    +-- inheritance
    +-- method overriding


COMPREHENSIONS
    |
    +-- list comprehension
    +-- dict comprehension


MODULES
    |
    +-- __init__.py
    +-- imports
    +-- if __name__ == "__main__"


FILE HANDLING
    |
    +-- open()
    +-- read()
    +-- write()
    +-- json.dump()
    +-- json.load()


EXCEPTIONS
    |
    +-- try
    +-- except
    +-- finally
    +-- raise
    +-- custom exception


PATHS
    |
    +-- os
    +-- pathlib


CONFIGURATION
    |
    +-- environment variables
    +-- dotenv
    +-- .env


DEPENDENCY MANAGEMENT
    |
    +-- uv init
    +-- uv add
    +-- uv run
    +-- pyproject.toml
    +-- uv.lock
    +-- requirements.txt


TYPE HINTS
    |
    +-- str
    +-- int
    +-- float
    +-- list[str]
    +-- dict[str, Any]
    +-- Optional
    +-- str | None
"""


'''
async python 


Async Python is mainly about not sitting around doing nothing while you're waiting for something else.

Blocking vs Non-Blocking


sync ??




'''


"""
import time


def task(name, delay):
    print(f"{name} started")
    time.sleep(delay)
    print(f"{name} finished")


task("A", 2)
task("B", 2)
task("C", 2)



6 seconds later, all tasks are done.
"""


"""
non blocking 

async def task(name, delay):
    print(f"{name} started")

    await asyncio.sleep(delay)

    print(f"{name} finished")

    
    At await, the async function says:

"I'm waiting. You can work on something else."

"""
'''





import asyncio
import time


async def task(name, delay):
    print(f"{name} started")

    await asyncio.sleep(delay)

    print(f"{name} finished")


async def main():
    start = time.perf_counter()

    await asyncio.gather(
        task("A", 2),
        task("B", 2),
        task("C", 2),
    )

    elapsed = time.perf_counter() - start

    print(f"elapsed: {elapsed:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())

''''''

it wait for 2 seconds and then all tasks are done.




A: ██████████████████
B: ██████████████████
C: ██████████████████

Time →
0                  2 sec

Concurrency

Tasks make progress during the same period.

Parallelism

Two pieces of work literally execute at the same time on different CPU cores.

Asyncio is mainly about concurrency, not CPU parallelism


it can start 100 api together 

now we go towards 
aiohttp

then 

async HTTP client/server library

import aiohttp


async def fetch(url: str) -> str:

    async with aiohttp.ClientSession() as session:

        async with session.get(url) as response:

            response.raise_for_status()

            return await response.text()


async def main():

    html = await fetch("https://example.com")

    print(html[:200])


if __name__ == "__main__":
    asyncio.run(main())



asyncio.run()
      ↓
main()
      ↓
fetch()
      ↓
ClientSession
      ↓
HTTP GET
      ↓
await response.text()
      ↓
HTML
'''


'''
async def
    ↓
defines an asynchronous function


await
    ↓
wait for an async operation without blocking
the whole event loop


asyncio.run()
    ↓
starts and runs an async program


asyncio.gather()
    ↓
runs multiple awaitables concurrently


asyncio.sleep()
    ↓
non-blocking sleep, useful for testing


aiohttp
    ↓
async HTTP requests


I/O-bound
    ↓
mostly waiting


CPU-bound
    ↓
mostly computing



'''



