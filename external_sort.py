from itertools import count, groupby
from pathlib import Path
from collections import deque
from tempfile import TemporaryDirectory

# Python 3.12+ szükséges.

def text_file_char_count(file_path: str | Path) -> int:
    """Visszaadja a megadott fájlban tárolt karakterek számát."""
    file_size = Path(file_path).stat().st_size  # A fájl mérete bájtban.
    # A memóriába egyszerre beolvasható karakterek számát becsüljük úgy, hogy a fájlméret tizedét vesszük és
    # minden karaktert 4 bájt méretűnek feltételezünk.
    max_chars_read = int(file_size / 10 / 4)
    character_count = 0
    with open(Path(file_path), 'r', encoding='utf8', newline='\n') as f:
        while chars := f.read(max_chars_read):
            character_count += len(chars)
    return character_count

def sort_large_dataset(input_file_path: str | Path, output_file_path: str | Path, sort_func=None, reverse=False,
                       tempdir=True, max_chunk_size_in_megabyte=10):
    """Az első argumentumban megadott szövegfájl soraiként szereplő karakterláncokat rendezi a sort_func függvény által
    meghatározott ismérv szerint növekvő sorrendben. Ha a reverse True, akkor csökkenő sorrendben.
    A rendezett adatokat a második argumentummal megadott fájlba lesznek mentve.
    Ha a tempdir True értékű, akkor a közbenső munkafájlok nem maradnak meg. Ha értéke False, akkor a munkafájlok egy
    létrehozott TMP nevű mappában lesznek tárolva, ami a függvény lefutása után is megmarad. Új hívás esetén a TMP mappa
    korábbi tartalma törlődik.
    A közbenső munkafájlok alapértelmezettől eltérő méretét az utolsó argumentummal változathatjuk meg megabájtban megadva.
    """

    input_file_character_count = text_file_char_count(input_file_path)  # A rendezni kívánt fájlban tárolt karakterek száma.
    input_file_size = Path(input_file_path).stat().st_size  # A rendezni kívánt fájl mérete bájtban.

    # ----- Szétdarabolási fázis: a rendezett részadatokat tartalmazó fájlok (chunk fájlok) előállítása -----

    # Legfeljebb ekkora méretű listát (chunk list) engedünk a memóriában rendezni a sort() metódussal, amelynek eredményét
    # ki fogjuk írni egy fájlba (chunk file).
    max_chunk_size = int(max_chunk_size_in_megabyte * 1024 ** 2)  # bájt

    # Meghatározzuk, hogy a rendezendő adatfájlból egyszerre mennyi karaktert olvasunk be (ami általában több sort jelent).
    # Ezt az értéket a rendezendő fájl karakterszámából a chunk list és a rendezendő fájl méretének arányában szűmoljuk.
    chunkfile_chars_limit: int = int(max_chunk_size / input_file_size * input_file_character_count)

    # A tempdir argumentum értékétől függően a chunk fájlokat vagy egy ideiglenes könyvtárban hozzuk létre, ami a
    # függvényből való kilépéskor törlődik a tartalmával együtt, vagy egy TMP nevű mappa jön létre, ami a függvény
    # végrehajtása után is megmarad a benne levő fájlokkal együtt. Ez tesztelést és utólagos elemzést tesz lehetővé.
    if tempdir:
        tempdir_obj = TemporaryDirectory(dir=Path(r'.'), delete=False)
        chunk_files_folderpath = Path(tempdir_obj.name)
    else:
        chunk_files_folderpath = Path('TMP')
        chunk_files_folderpath.mkdir(exist_ok=True)
        # Ha a rendezett részadatokat tartalmazó chunk fájlok tárolására szolgáló mappa nem üres, akkor töröljük a tartalmát.
        for file in chunk_files_folderpath.glob('*'):
            file.unlink()

    # A rendezni kívánt fájlból beolvassuk a meghatározott hosszúságú szakaszokat egy listába (chunk_list).
    # E lista elemeit rendezzük az sort_func argumentumban megadott függvény által meghatározott ismérv szerint.
    # A rendezett lista elemeit egy chunk fájlba mentjük.
    with open(Path(input_file_path), 'r', encoding='utf8', newline='\n') as f_input:
        chunk_file_counter = count(1)  # A létrejövő chunk fájlokat számolja.
        while chunk_list := f_input.readlines(chunkfile_chars_limit):
            chunk_list.sort(key=sort_func, reverse=reverse)
            with open(chunk_files_folderpath / Path(f'chunkfile{str(next(chunk_file_counter))}.txt'), 'w', encoding='utf8', newline='\n') as chunkfile:
                chunkfile.writelines(chunk_list)

    # --- Összefésülési fázis: a rendezett adatokat tartalmazó chunk fájlokból egy olyan eredményfájl előálítása, amelyben az összes adat rendezett ---

    # Egy új üres kimeneti eredményfájlt hozunk létre akár létezett, akár nem.
    output_file_path = Path(output_file_path)
    if output_file_path.exists():
        output_file_path.unlink()
    output_file_path.touch()
    # Az új üres fájlt megnyitjuk hozzáfűzés módban.
    out_file_obj = open(output_file_path, 'a', encoding='utf8', newline='\n')

    # A chunk fájlokat tartalmazó mappában levő összes fájlt olvasásra megnyitjuk.
    sorted_chunk_fileobjects = [file.open('r', encoding='utf8', newline='\n') for file in chunk_files_folderpath.glob('chunkfile*.txt')]
    # Beállítjuk azt a maximális karakterszámot, amelynek megfelelő számú elemet a chunk fájlok számának megfelelő pufferek mindegyike
    # tárolhat. Ez a chunkfile_chars_limit osztva a chunk file-ok számával
    max_chars_read_from_chunk_files: int = int(chunkfile_chars_limit / (next(chunk_file_counter) - 1))  # darab karakter.
    # Minden chunk fájlhoz társítunk egy puffert, amit kétvégú sor (deque) konténerrel valósítunk meg.
    # A puffereket feltöltjük a chunk fájlokból beolvasott első adaggal.
    buffers_chunk_files = [(deque(chunk_file.readlines(max_chars_read_from_chunk_files)), chunk_file) for chunk_file in sorted_chunk_fileobjects]

    while buffers_chunk_files:  # Mivel az időközben kiürült puffereket töröljük, ezért akkor állunk le, ha nincs már puffer

        # Vesszük a pufferek első elemét.
        current_examined_items = (buff[0] for buff, _ in buffers_chunk_files)
        # Megvizsgáljuk, hogy ezek közül melyik a minimális (maximális).
        item = min(current_examined_items, key=sort_func) if not reverse else max(current_examined_items, key=sort_func)
        # A minimum (maximum) értéket kiírjuk a kimeneti eredményfájlba.
        out_file_obj.write(item)
        # Meghatározzuk, hogy melyik puffer első eleme volt a kiírt item. E puffer első elemét eltávolítjuk.
        for buffer, chunk_file in buffers_chunk_files:
            if buffer[0] == item:
                buffer.popleft()
                # Ha az elemetávolítás után üres lesz a buffer, akkor feltöltjük.
                if not buffer:
                    buffer.extend(chunk_file.readlines(max_chars_read_from_chunk_files))
                    # Ha már nincs több beolvasható adat, amivel fel lehetne tölteni a puffert, és így az üres marad, akkor
                    # töröljük ezt a pufferek nyilvántartásából.
                    if not buffer:
                        buffers_chunk_files.remove((buffer, chunk_file))
                break

    # A összes chunk fájlt bezárjuk.
    for fileobj in sorted_chunk_fileobjects:
        fileobj.close()
    # A kimeneti eredményfájlt lezárjuk.
    out_file_obj.close()
    # Ha ideiglenes könyvtár lett létrehozva, akkor azt eltávolítjuk a tartalmával együtt.
    if tempdir:
        tempdir_obj.cleanup()


# TESZT

input_file_path = Path('dataset.txt')          # A rendezendő adatokat tartalmazó fájl.
output_file_path = Path('sorted_dataset.txt')  # A rendezett adatokat tartalmazó fájl.

# A rendezés végrehajtása.
sort_large_dataset(input_file_path, output_file_path, sort_func = len, reverse = False, tempdir=True, max_chunk_size_in_megabyte=100)

# Ellenőrizzük, hogy a rendezetlen és rendezett adatokat tartalmazó fájl mérete azonos.
print('A rendezendő fájl mérete: {:,.2f} kB'.format(input_file_path.stat().st_size / 1024))
print('A rendezett fájl mérete:  {:,.2f} kB'.format(output_file_path.stat().st_size / 1024))

# Mivel már rendezetten állnak elő az adatok (karakterláncok), így tudjuk azokat a groupby() függvénnyel csoportosítani.
# A csoportosítással most azt nézzük meg, hogy adott karakterlánchossz hányszor fordul elő.
with open(output_file_path, 'r', encoding='UTF-8', newline='\n') as f_output:
    grouped_by_len = {k: sum(1 for _ in iterator) for k, iterator in groupby((s[:-1] for s in f_output), key=len)}

# A csoportosított adatokat kiírva láthatjuk, hogy az egyes hosszok gyakorisága közel egyenlő, vagyis a hosszok egyenletes eloszlásúak.
print(grouped_by_len)
# Ha az egyes hosszokhoz tartozó gyakoriság értékeket összeadjuk, akkor megkapjuk az összes karakterlánc számát.
# Ennek egyezni kell a rendezetlen fájl sorainak számával.
print('A rendezett fájl sorainak száma: {:_}'.format(sum(grouped_by_len.values())))

# Eredmények:
# A rendezendő fájl mérete: 1,079,733.62 kB
# A rendezett fájl mérete:  1,079,733.62 kB
# {1: 6669647, 2: 6666426, 3: 6663643, 4: 6662386, 5: 6669571, 6: 6667494, 7: 6671073, 8: 6666827, 
#  9: 6669221, 10: 6664562, 11: 6667095, 12: 6665419, 13: 6669616, 14: 6663141, 15: 6663879}
# A rendezett fájl sorainak száma: 100_000_000


