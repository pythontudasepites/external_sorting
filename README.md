# Nagyméretű adathalmazok rendezése

Számos esetben igényként merülhet fel egy adathalmaz valamilyen ismérv szerinti sorbarendezése. Például ha a szabványos könyvtár *itertools* moduljának *groupby()* függvényét akarjuk használni, akkor a helyes működéshez az argumentumként átadott adatsorozatnak rendezettnek kell lenni. A sorbarendezést megtehetjük például a *sorted()* beépített függvénnyel, amely beállítástól függően növekvő vagy csökkenő sorrendben rendezi az értékeket és egy listában adja vissza azokat. Ez mindaddig jól működik, amíg az adatok számossága akkora, hogy ez a rendezett lista befér a számítógép memóriájába. 

Mi van azonban akkor, ha olyan nagy adathalmazzal kell dolgozni, amely már nem tölthető be a memóriába a rendezéshez?

Ebben az esetben olyan módszert kell alkalmazni, amely a rendezés folyamán a háttértárat is használja és a rendezett adatok is egy fájlban fognak tárolódni. Mivel tehát ilyenkor a rendezéshez nem csak a belső memóriát, hanem a külső háttértárat is használjuk, ezért az ilyen eljárást **külső rendezésnek** (*external sorting*) nevezik. Ennek megfelelően az olyan adatrendezést, amely csak a számítógép memóriájában történik belső rendezésnek (*internal sorting*) hívják.

A külső rendezés – mivel többszöri háttértárba írás és olvasás történik – természeteseb lassúbb a belső rendezésnél, ami úgy is felfogható, hogy ez az ára annak, hogy a nagy adathalmazunk rendezése egyáltalán megvalósítható.

Az alábbi ábrán a külső rendezés, pontosabban a külső, összefésüléses eljáráson alapuló rendezés (*external merge sort*) elvét és főbb lépéseit láthatjuk. Az egyes lépések számokkal jelennek meg és az ábra alján olvasható a szöveges kifejtésük.

<img src="https://github.com/pythontudasepites/external_sorting/blob/main/external_merge_sort_diagram.jpg" width="500" height="575">

Az *external_sort.py* modulfájlban a ***sort_large_dataset*** nevű függvény az ábrán bemutatott elvet követve egy adott nevű fájl soraiként tárolt véletlenszerű karakterláncokat képes valamilyen ismérv (pl. hossz) szerint sorban rendezni, és a rendezett adatokat tartalmazó fájlt egy megadott nevű fájlba menteni. A megértést a részletes kommentek és az ábra segítik. A futtatáshoz Python 3.12+ verzió szükséges.

E függvény teszteléséhez szükséges egy nagyméretű fájl, amely véletleszerűen előállított karakterláncokat tárol. Ezek generálásához a *make_large_input_file.py* modulban látható függvényt használjuk. E modult szkriptként futtatva egy 100 millió sort tartalmazó kb 1GB méretű dataset.txt nevű szövegfájl jön létre.

A függvényt az *external_sort.py* modulban látható kódsorokkal teszteljük. A rendezés eltart pár percig, és utána a hosszuk szerint rendezett karakterláncok a sorted_dataset.txt fájlban állnak elő. A helyes működés első ellenőrzőpontja, hogy a két fájl mérete egyezik-e. Ha nem, akkor biztos, hogy nem jó valami. Megnyugtató, hogy esetünkben ezek egyeznek. További teszthez a már említett *groupby()* függvényt használjuk. Ezzel azt nézzük meg, hogy adott karakterlánchossz hányszor fordul elő. Látható, hogy ez egyenletes eloszlású. Ezt is vártuk, hiszen a karakterlánc-előállító függvényben használt *choice()* egyenletes eloszlást produkál. A fájl sorainak ellenőrzéséhez pedig egyszerűen a hosszgyakoriságok összegét kell venni. Ez is egyezik a rendezendő adatfájl sorainak számával.
