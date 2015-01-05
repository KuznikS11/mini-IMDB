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
        id_uporabnika = baza.fetchone()
        if id_uporabnika is None: #?
            raise Exception('vnešeno uporabniško ime ali geslo je napacno')


def dodaj_predlog(id_uporabnika, id_filma):
    '''Uporabniku dodamo film, med filme, ki jih želi pogledati'''
    with baza:
        baza.execute('''SELECT vsec FROM Predlogi WHERE uporabnik = ? AND film = ?''', [id_uporabnika, id_filma])
        ocena = baza.fetchone()
        if ocena is None:
            baza.execute('''INSERT INTO Predlogi (uporabnik, film, vsec) VALUES (?, ?)''', [id_uporabnika, id_filma, None])
    
def dodaj_predloge_glede_na_oceno(id_uporabnika):
    with baza:
        baza.execute('''SELECT film, vsec FROM Predlogi WHERE uporabnik = ?''', [id_uporabnika])
        par = fetchone()
        id_filma = par[0]
        ocena = par[1]
        if ocena == (True, ):
            baza.execute('''SELECT uporabnik FROM Predlogi WHERE film = ? AND vsec = ?''', [id_filma, ocena])
            uporabnik2 = baza.fetchone()
            baza.execute('''SELECT film FROM Predlogi WHERE uporabnik = ? AND vsec = ?''', [uporabnik2, 1])
            predlogi = baza.fetchall()
            for predlog in predlogi:
                baza.execute('''SELECT vsec FROM Predlogi WHERE uporabnik = ? AND film = ?''', [id_uporabnika, predlog[0]])
                ocena2 = baza.fetchone()
                if ocena2 is None:
                    baza.execute('''INSERT INTO Predlogi (film, vsec) VALUES (?, ?)''', [predlog[0], None])

        
        
    

def dodaj_ogled(id_uporabnika, id_filma, ocena): #oceni film 
#    None
#    (None, )
#    (True, )
#    (False, )
    
    with baza:
        baza.execute('''SELECT vsec FROM Predlogi WHERE uporabnik = ? AND film = ?''', [id_uporabnika, id_filma])
        vsec = fetchone()
        if vsec is None:  #ce film ni med predlogi
            baza.execute('''INSERT INTO Predlogi (uporabnik, film, vsec) VALUES (?, ?, ?)''', [id_uporabnika, id_filma, ocena])

        else: #ce film je med predlogi
            if ocena == True:
                baza.execute('''UPDATE Predlogi SET vsec = ?''', [1])
            if ocena == False:
                baza.execute('''UPDATE Predlogi SET vsec = ?''', [0])

def pokazi_filmiZaPogledat(id_uporabnika): #spremeni!
    '''Vrnemo vse filme, ki jih uporabnik želi pogledati'''
    with baza:
        baza.execute('''SELECT id, naslov FROM Film JOIN Filmi_za_pogledat ON id = film WHERE uporabnik = ?''', [id_uporabnika])
        return baza.fetchall()

def pokazi_ogledaniFilmi(id_uporabnika):#spremeni!
    '''Vrnemo vse filme, ki jih je uporabnik že pogledal'''
    with baza:
        baza.execute('''SELECT id, naslov FROM Filmi JOIN Ogledani_filmi ON id = film WHERE uporabnik = ?''', [id_uporabnika])
        return baza.fetchall()

    
    
# dodaj/ uredi filme, igralce, zvrsti
