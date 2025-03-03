
from random import choice, choices
from itertools import chain
from typing import Iterable
from pathlib import Path


def generate_random_strings(number_of_strings: int, lengths: Iterable, *iterables_of_codepoints):
    """Egy olyan generátorobjektummal tér vissza, amely az első argumentumban megadott darabszámú karakterláncot állít elő
    véletlenszerű hosszokkal. Ugyanazon hossz többször is szerepelhet.
    A lehetséges hosszokat a második argumentum mint iterálható objektum elemei határozzák meg.
    Egy adott hosszúságú karakterlánc olyan karaktereket tartalmaz, amely a harmadik vagy további argumentumokként
    felsorolt iterálható objektumokkal definiált Unicode kódpontoknak megfelelő karakterekből véletlenszerűen lesznek kiválasztva.
    Egy adott karakterláncban azonos karakterek megengedettek.
    """
    # A generált karakterláncok lehetséges hosszai.
    lengths = tuple(lengths)
    # A generált karakterláncokban megengedett karakterek Unicode kódpontjai.
    codepoints = tuple(chain(*iterables_of_codepoints))
    return (''.join(map(chr, choices(codepoints, k=choice(lengths)))) for _ in range(number_of_strings))


input_file_path = Path('dataset.txt')   # A véletlenszerűen generált karakterláncokat ebbe a fájlba mentjük.
number_of_random_strings = 100_000_000  # A rendezendő adatfájlban ennyi sor lesz, mert egy karakterlánc egy sor.

# Mindene egyes véletlenszerűen generált karakterláncot a fájl egy soraként mentjük el.
# A karakterláncok hossza minimum 1, maximum 15. A generált karakterláncokban a magyar abc kis- és nagybetűi szerepelnek.
with open(input_file_path, 'w', encoding='UTF-8', newline='\n') as f_dataset:
    f_dataset.writelines((s + '\n' for s in generate_random_strings(number_of_random_strings,
                                                                    range(1, 16),
                                                                    range(97, 123), range(65, 91),
                                                                    {225, 233, 237, 243, 246, 337, 250, 252, 369},
                                                                    {193, 201, 205, 211, 214, 336, 218, 220, 368})))



