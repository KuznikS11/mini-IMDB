import sqlite3
import hashlib

datoteka_baze = 'miniIMDb.sqlite3'
baza = sqlite3.connect(datoteka_baze, isolation_level = None)


def iskanje_filmov(beseda='', leto_zacetek=2000, leto_konec=2015, ocena_min=7, ocena_max=10, id_zvrsti=1):
    '''Vrne seznam vseh filmov, ki ustrezajo vsem danim kriterijem.'''
    with baza:
        baza.execute('''SELECT Filmi.id, Filmi.naslov
                  FROM Filmi
                  JOIN Zvrsti_filma ON Filmi.id = Zvrsti_filma.film
                  WHERE naslov LIKE %?%
                  AND leto IS BETWEEN ? AND ?
                  AND ocena IS BETWEEN ? AND ?
                  AND zvrst = ?''' ,
                  [beseda, leto_zacetek, leto_konec, ocena_min, ocena_max, id_zvrsti])
        return baza.fetchall()

def zvrsti_filma():
    '''Vrne vse zvrsti in njihove id-je'''
    with baza:
        baza.execute('''SELECT id, zvrst FROM Zvrsti''')
        return baza.fetchall()

def iskanje_po_igralcih(ime_igralca):
    '''Vrne vse filme v katerih je igral igralec, ki ga vpišemo'''
    with baza:
        baza.execute('''SELECT Filmi.id, Filmi.naslov
                        FROM Filmi
                        JOIN Vloga ON Filmi.id = Vloga.film
                        JOIN Igralci ON Vloga.igralec = Igralci.id
                        WHERE ime_igralca LIKE ?% OR priimek_igralca LIKE ?%''', [ime_igralca])
   
        return baza.fetchall()

def zakodiraj(geslo):
    return hashlib.md5(geslo.encode()).hexdigest()

def dodaj_uporabnika(up_ime, geslo):
    '''V bazo dodamo uporabnika: njegovo uporabniško ime in zakodirano geslo'''
    cur = baza.cursor()
    cur.execute('''INSERT INTO Uporabniki (up_ime, geslo) VALUES (?, ?)''', [up_ime, zakodiraj(geslo)])
    cur.close()
    id_uporabnika = cur.lastrowid #dobi zadnji id
    return id_uporabnika

def preveri_geslo(up_ime, geslo):
    '''Preveri èe je v bazi uporabnik z podanim uporabniškim imenom in podanim geslom'''
    with baza:
        baza.execute('''SELECT id FROM Uporabnik WHERE up_ime = ? AND geslo = ?''', [up_ime, zakodiraj(geslo)])
        id_uporabnika = fetchone()
        if id_uporabnika == 0: #?
            print('vnešeno uporabniško ime ali geslo je napaèno')


def dodaj_filmiZaPogledat(id_uporabnika, id_filma):
    '''Uporabniku dodamo film, med filme, ki jih želi pogledati'''
    cur = baza.cursor()
    cur.execute('''INSERT INTO Filmi_za_pogledat (uporabnik, film) VALUES (?, ?)''', [id_uporabnika, id_filma])
    cur.close()
    return id_uporabnika #???

def dodaj_ogledaniFilmi(id_uporabnika, id_filma):
    '''Uporabniku dodamo film, med filme, ki jih je že pogledal'''
    with baza:
        baza.execute('''INSERT INTO Filmi_za_pogledat (uporabnik, film) VALUES (?, ?)''', [id_uporabnika, id_filma])

def pokazi_filmiZaPogledat(id_uporabnika):
    '''Vrnemo vse filme, ki jih uporabnik želi pogledati'''
    with baza:
        baza.execute('''SELECT id, naslov FROM Film JOIN Filmi_za_pogledat ON id = film WHERE uporabnik = ?''', [id_uporabnika])
        return baza.fetchall()

def pokazi_ogledaniFilmi(id_uporabnika):
    '''Vrnemo vse filme, ki jih je uporabnik že pogledal'''
    with baza:
        baza.execute('''SELECT id, naslov FROM Filmi JOIN Ogledani_filmi ON id = film WHERE uporabnik = ?''', [id_uporabnika])
        return baza.fetchall()

    
    

