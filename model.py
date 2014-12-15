import sqlite3


baza = sqlite3.connect(datoteka_baze, isolation_level = None)
datoteka_baze = 'miniIMDb.sqlite3'

def filmi_iskanje(beseda = '', leto_zacetek = 2000, leto_konec = 2015, ocena_min = 7, ocena_max = 10, id_zvrsti):
    with baza:
        baza.execute('''SELECT id, naslov FROM  Filmi JOIN Zvrsti_filma ON id = film WHERE
                  naslov LIKE %?%
                  AND leto IS BETWEEN ? AND ?
                  AND ocena IS BETWEEN ? AND ?
                  AND zvrst = ?''' ,
                  [beseda, leto_zacetek, leto_konec, ocena_min, ocena_max, id_zvrsti])
    naslovi = baza.fetchall()
    return naslovi

def filmi_zvrsti():
    with baza:
        baza.execute('''SELECT * FROM Zvrsti''')
    zvrsti = baza.fetchall()
    return zvrsti

def filmi_igralci(ime_igralca):
    with baza:
        baza.execute('''SELECT id, naslov FROM Filmi JOIN Vloga ON id = film JOIN Igralci ON igralec = id
                WHERE ime LIKE ?% OR priimek LIKE ?%''', [ime_igralca])
    naslovi = baza.fetchall()
    return naslovi

def dodaj_uporabnika(up_ime, geslo):
    with baza:
        baza.execute('''INSERT INTO Uporabniki (up_ime, geslo) VALUES (?, ?)''', [up_ime, geslo])
    id_uporabnika = c..#dobi zadnji id, ...lastid
    return id_uporabnika


def dodaj_filmiZaPogledat(id_uporabnika, id_filma):
    with baza:
        baza.execute('''INSERT INTO Filmi_za_pogledat (uporabnik, film) VALUES (?, ?)''', [id_uporabnika, id_filma])
    
def dodaj_ogledaniFilmi(id_uporabnika, id_filma)
    with baza:
        baza.execute('''INSERT INTO Filmi_za_pogledat (uporabnik, film) VALUES (?, ?)''', [id_uporabnika, id_filma])

def pokazi_filmiZaPogledat(id_uporabnika):
    with baza:
        baza.execute('''SELECT id, naslov FROM Film JOIN Filmi_za_pogledat ON id = film WHERE uporabnik = ?''', [id_uporabnika])

    
    

