import sqlite3
import hashlib

datoteka_baze = 'miniIMDb.sqlite3'
baza = sqlite3.connect(datoteka_baze, isolation_level=None)


def iskanje_filmov(beseda='', leto_zacetek=1000, leto_konec=3000, ocena_min=0, ocena_max=10, zvrst=''):
    '''Vrne seznam vseh filmov, ki ustrezajo vsem danim kriterijem.'''
    with baza:
        cur = baza.cursor()
        cur.execute('''SELECT Filmi.id, Filmi.naslov
                  FROM Filmi
                  JOIN Zvrsti_filma ON Filmi.id = Zvrsti_filma.film
                  JOIN Zvrsti ON Zvrsti_filma.zvrst = Zvrsti.id
                  WHERE Filmi.naslov LIKE ?
                  AND Filmi.leto BETWEEN ? AND ?
                  AND Filmi.ocena BETWEEN ? AND ?
                  AND Zvrsti.zvrst LIKE ?''' ,
                  ['%'+beseda+'%', leto_zacetek, leto_konec, ocena_min, ocena_max, zvrst+'%'])
        filmi = cur.fetchall()
        if len(filmi) != 0:
            sez = []
            sez.append(filmi[0])
            for i in range(len(filmi)-1):
                if filmi[i] != filmi[i+1]:
                    sez.append(filmi[i+1])
            return sez
        return filmi



def zvrsti_filma():
    '''Vrne vse zvrsti in njihove id-je'''
    with baza:
        cur = baza.cursor()
        cur.execute('''SELECT * FROM Zvrsti''')
        return cur.fetchall()


def iskanje_po_igralcih(ime_igralca=''):
    '''Vrne vse filme v katerih je igral igralec, ki ga vpišemo'''
    with baza:
        cur = baza.cursor()
        cur.execute('''SELECT Filmi.id, Filmi.naslov
                        FROM Filmi
                        JOIN Vloga ON Filmi.id = Vloga.film
                        JOIN Igralci ON Vloga.igralec = Igralci.id
                        WHERE ime_igralca LIKE ? OR priimek_igralca LIKE ?''', [ime_igralca+'%', ime_igralca+'%'])
   
        igralci = cur.fetchall()
        if len(igralci) != 0:
            sez = []
            sez.append(igralci[0])
            for i in range(len(igralci)-1):
                if igralci[i] != igralci[i+1]:
                    sez.append(igralci[i+1])
            return sez
        return igralci


def podatki_filma(id_filma):
    '''vrne vse podatke o filmi'''

    with baza:

        cur = baza.cursor()
        cur.execute('''SELECT Filmi.naslov, Filmi.trajanje, Filmi.ocena, Filmi.opis, Filmi.reziser, Filmi.scenarist, Filmi.leto, Zvrsti.zvrst
                  FROM Filmi
                  JOIN Zvrsti_filma ON Filmi.id = Zvrsti_filma.film
                  JOIN Zvrsti ON Zvrsti_filma.zvrst = Zvrsti.id
                  WHERE Filmi.id =?''', [id_filma])
        return cur.fetchone()


def podatki_igralci(id_filma):
    '''vrne ime, priimek igralca in njegovo vlogo za podani film'''
    
    with baza:
        cur = baza.cursor()
        cur.execute('''SELECT Igralci.ime_igralca, Igralci.priimek_igralca, Vloga.vloga
                        FROM Igralci
                        JOIN Vloga ON Vloga.igralec = Igralci.id
                        JOIN Filmi ON Filmi.id = Vloga.film
                        WHERE Filmi.id = ?''', [id_filma])
        
        return cur.fetchall()


    

def zakodiraj(geslo):
    return hashlib.md5(geslo.encode()).hexdigest()

def dodaj_uporabnika(up_ime, geslo):
    '''V bazo dodamo uporabnika: njegovo uporabniško ime in zakodirano geslo'''
    cur = baza.cursor()
    cur.execute('''SELECT Uporabniki.id FROM Uporabniki WHERE up_ime = ? ''', [up_ime])
    id_uporabnika = cur.fetchone()
    if id_uporabnika is None:
        cur.execute('''INSERT INTO Uporabniki (up_ime, geslo) VALUES (?, ?)''', [up_ime, zakodiraj(geslo)])
        cur.close()
        id_uporabnika = cur.lastrowid #dobi zadnji id
        return id_uporabnika
    else:
        return None

def preveri_geslo(up_ime, geslo):
    '''Preveri èe je v bazi uporabnik z podanim uporabniškim imenom in podanim geslom'''
    with baza:
        cur = baza.cursor()
        kodirano = zakodiraj(geslo)
        cur.execute('''SELECT Uporabniki.id FROM Uporabniki WHERE up_ime = ? AND geslo = ?''', [up_ime, kodirano])
        id_uporabnika = cur.fetchone()
        if id_uporabnika is None:
            return None
        return id_uporabnika[0]

#    None
#    (None, )
#    (True, )
#    (False, )

def dodaj_predlog(id_uporabnika, id_filma):
    '''Uporabniku dodamo film, med filme, ki jih želi pogledati'''
    
    with baza:
        cur = baza.cursor()
        cur.execute('''SELECT Predlogi.vsec FROM Predlogi WHERE uporabnik = ? AND film = ?''', [id_uporabnika, id_filma])
        ocena = cur.fetchone()
        if ocena is None:
            cur.execute('''INSERT INTO Predlogi (uporabnik, film, vsec) VALUES (?, ?, ?)''', [id_uporabnika, id_filma, None])

    
def dodaj_predloge_glede_na_oceno(id_uporabnika):
    '''ce je uporabniku nek film usec, mu predlagamo filme, ki so usec uporabnikom, katerim je biu usec tudi ta film'''
    
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

        
        
    

def oceni(id_uporabnika, id_filma, ocena): 
    '''uporabnik oceni film (mu je vsec/ni vsec). Ce je film ze v bazi mu spremenimo oceno, ce ga ni ga dodamo v bazo skupaj z oceno'''
    
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

def pokazi_vsecniFilmi(id_uporabnika):
    '''Vrnemo vse filme, ki jih je uporabnik že pogledal'''

    with baza:
        cur = baza.cursor()
        
        cur.execute('''SELECT Filmi.id, Filmi.naslov FROM Filmi JOIN Predlogi ON Filmi.id = Predlogi.film
                               WHERE uporabnik = ? AND vsec = ?''', [id_uporabnika, True])
        return cur.fetchall()

def pokazi_nevsecniFilmi(id_uporabnika):
    '''Vrnemo vse filme, ki jih je uporabnik že pogledal'''

    with baza:
        cur = baza.cursor()
        
        cur.execute('''SELECT Filmi.id, Filmi.naslov FROM Filmi JOIN Predlogi ON Filmi.id = Predlogi.film
                               WHERE uporabnik = ? AND vsec = ?''', [id_uporabnika, False])
        return cur.fetchall()

    
def pokazi_filmiZaPogledat(id_uporabnika): 
    '''Vrnemo vse filme, ki jih uporabnik želi pogledati'''

    with baza:
        cur = baza.cursor()
        
        cur.execute('''SELECT Filmi.id, Filmi.naslov FROM Filmi JOIN Predlogi ON Filmi.id = Predlogi.film
                               WHERE uporabnik = ? AND vsec IS NULL''', [id_uporabnika])
        return cur.fetchall()

    
##    with baza:
##        cur = baza.cursor()
##        cur.execute('''SELECT Filmi.id, Filmi.naslov FROM Filmi JOIN Predlogi ON Filmi.id = Predlogi.film
##                               WHERE uporabnik = ?''', [id_uporabnika])
##        vsi_filmi = cur.fetchall()
##
##
##        ogledani = pokazi_ogledaniFilmi(id_uporabnika)
##
##        for film in vsi_filmi:
##            if film in ogledani:
##                vsi_filmi.remove(film)
##                
##
##        return vsi_filmi

def lahko_doda_predlog(id_uporabnika, id_filma):
    ''' Preveri, èe uporabnik doloèenega filma še ni pogledal in ga nima med predlogi za ogled '''
    with baza:
        cur = baza.cursor()
        
        cur.execute('''SELECT * FROM Predlogi WHERE uporabnik = ? AND film = ?''', [id_uporabnika, id_filma])
        sez = cur.fetchall()

        if sez == []:
            return True
        return False



def komentiranje(id_uporabnika, id_filma, komentar):
    '''dodamo komentar na film v bazo'''
    
    with baza:
        cur = baza.cursor()
        cur.execute('''INSERT INTO Komentarji (film, uporabnik, komentar) VALUES (?, ?, ?)''', [id_filma, id_uporabnika, komentar])


def pokazi_komentarje(id_filma):
    '''pogledamo vse komentarje za doloèen film'''
    with baza:
        cur = baza.cursor()
        cur.execute('''SELECT Komentarji.uporabnik, Komentarji.komentar FROM Komentarji WHERE film = ?''', [id_filma])

        komentarji = cur.fetchall()
        vrni = []
        for (id_uporabnika, komentar) in komentarji:
            cur.execute('''SELECT Uporabniki.up_Ime FROM Uporabniki WHERE ID = ?''', [id_uporabnika])
            par = (cur.fetchone()[0], komentar)
            vrni.append(par)
        return vrni


    
    
def id_uporabnika(up_ime):

    with baza:
        cur = baza.cursor()
        cur.execute('''SELECT Uporabniki.id FROM Uporabniki WHERE up_ime = ?''', [up_ime])
        id_up = cur.fetchone()
        return id_up
    
def kukiji(username):
    c = baza.cursor()
    c.execute("SELECT up_ime FROM Uporabniki WHERE up_ime=?",[username])
    r = c.fetchone()
    c.close ()
    return r
    
    
