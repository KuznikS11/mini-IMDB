import sqlite3
import hashlib

datoteka_baze = 'miniIMDb.sqlite3'
baza = sqlite3.connect(datoteka_baze)


def iskanje_filmov(beseda='', leto_zacetek=2000, leto_konec=2015, ocena_min=7, ocena_max=10, id_zvrsti=3):
    '''Vrne seznam vseh filmov, ki ustrezajo vsem danim kriterijem.'''
    with baza:
        cur = baza.cursor()
        cur.execute('''SELECT Filmi.id, Filmi.naslov
                  FROM Filmi
                  JOIN Zvrsti_filma ON Filmi.id = Zvrsti_filma.film
                  WHERE Filmi.naslov LIKE ?
                  AND Filmi.leto BETWEEN ? AND ?
                  AND Filmi.ocena BETWEEN ? AND ?
                  AND Zvrsti_filma.zvrst = ?''' ,
                  [beseda, leto_zacetek, leto_konec, ocena_min, ocena_max, id_zvrsti])
        return cur.fetchall()

def zvrsti_filma():
    '''Vrne vse zvrsti in njihove id-je'''
    with baza:
        cur = baza.cursor()
        cur.execute('''SELECT * FROM Zvrsti''')
        return cur.fetchall()

def iskanje_po_igralcih(ime_igralca):
    '''Vrne vse filme v katerih je igral igralec, ki ga vpišemo'''
    with baza:
        cur = baza.cursor()
        cur.execute('''SELECT Filmi.id, Filmi.naslov
                        FROM Filmi
                        JOIN Vloga ON Filmi.id = Vloga.film
                        JOIN Igralci ON Vloga.igralec = Igralci.id
                        WHERE ime_igralca LIKE ? OR priimek_igralca LIKE ?''', [ime_igralca, ime_igralca])
   
        return cur.fetchall()

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
        cur = baza.cursor()
        kodirano = zakodiraj(geslo)
        cur.execute('''SELECT Uporabniki.id FROM Uporabniki WHERE up_ime = ? AND geslo = ?''', [up_ime, kodirano])
        id_uporabnika = cur.fetchone()
        if id_uporabnika is None: 
            raise Exception('vnešeno uporabniško ime ali geslo je napacno')


def dodaj_predlog(id_uporabnika, id_filma):
    '''Uporabniku dodamo film, med filme, ki jih želi pogledati'''
    with baza:
        cur = baza.cursor()
        cur.execute('''SELECT Predlogi.vsec FROM Predlogi WHERE uporabnik = ? AND film = ?''', [id_uporabnika, id_filma])
        ocena = cur.fetchone()
        if ocena is None:
            cur.execute('''INSERT INTO Predlogi (uporabnik, film, vsec) VALUES (?, ?, ?)''', [id_uporabnika, id_filma, None])

    
def dodaj_predloge_glede_na_oceno(id_uporabnika):
    with baza:
        cur = baza.cursor()
        cur.execute('''SELECT Predlogi.film FROM Predlogi WHERE uporabnik = ? and vsec = ?''', [id_uporabnika, True])
        id_filma = cur.fetchone()
        cur.execute('''SELECT Predlogi.uporabnik FROM Predlogi WHERE film = ? AND vsec = ?''', [id_filma[0], True])
        uporabniki = cur.fetchall()
        for uporabnik2 in uporabniki:
            if uporabnik2[0] != id_uporabnika:
                cur.execute('''SELECT Predlogi.film FROM Predlogi WHERE uporabnik = ? AND vsec = ?''', [uporabnik2[0], True])
                predlogi = cur.fetchall()
                for predlog in predlogi:
                    cur.execute('''SELECT Predlogi.vsec FROM Predlogi WHERE uporabnik = ? AND film = ?''', [id_uporabnika, predlog[0]])
                    obstaja = cur.fetchone()
                    if obstaja is None:
                        cur.execute('''INSERT INTO Predlogi (uporabnik, film, vsec) VALUES (?, ?, ?)''', [id_uporabnika, predlog[0], None])

        
        
    

def dodaj_ogled(id_uporabnika, id_filma, ocena): #oceni film 
#    None
#    (None, )
#    (True, )
#    (False, )
    
    with baza:
        cur = baza.cursor()
        cur.execute('''SELECT Predlogi.vsec FROM Predlogi WHERE uporabnik = ? AND film = ?''', [id_uporabnika, id_filma])
        vsec = cur.fetchone()
        if vsec is None:  #ce film ni med predlogi
            cur.execute('''INSERT INTO Predlogi (uporabnik, film, vsec) VALUES (?, ?, ?)''', [id_uporabnika, id_filma, ocena])

        else: #ce film je med predlogi
            if ocena == True:
                cur.execute('''UPDATE Predlogi SET vsec = ? WHERE uporabnik = ? AND film = ?''', [True, id_uporabnika, id_filma])
            if ocena == False:
                cur.execute('''UPDATE Predlogi SET vsec = ? WHERE uporabnik = ? AND film = ?''', [False, id_uporabnika, id_filma])


def predlogi():
    with baza:
        cur = baza.cursor()
        cur.execute('''SELECT * FROM Predlogi''')
        return cur.fetchall()

    
def pokazi_ogledaniFilmi(id_uporabnika):
    '''Vrnemo vse filme, ki jih je uporabnik že pogledal'''

    with baza:
        cur = baza.cursor()
        
        cur.execute('''SELECT Filmi.id, Filmi.naslov FROM Filmi JOIN Predlogi ON Filmi.id = Predlogi.film
                               WHERE uporabnik = ? AND vsec IN (?,?)''', [id_uporabnika, True, False])
        return cur.fetchall()

    
def pokazi_filmiZaPogledat(id_uporabnika): 
    '''Vrnemo vse filme, ki jih uporabnik želi pogledati'''
    
    ogledani = pokazi_ogledaniFilmi(id_uporabnika)
    with baza:
        cur = baza.cursor()
        
        cur.execute('''SELECT Filmi.id, Filmi.naslov FROM Filmi JOIN Predlogi ON Filmi.id = Predlogi.film
                               WHERE uporabnik = ?''', [id_uporabnika])
        vsi_filmi = cur.fetchall()

        for film in vsi_filmi:
            if film in ogledani:
                vsi_filmi.remove(film)

        return vsi_filmi


    
    
# dodaj/ uredi filme, igralce, zvrsti


