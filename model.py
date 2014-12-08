import sqlite3


datoteka_baze = 'miniIMDb.sqlite3'

def filmi_iskanje(beseda = '', leto_zacetek = 2000, leto_konec = 2015, ocena_min = 7, ocena_max = 10, id_zvrsti):
    c = baza.cursor()
    c.execute('''SELECT id, naslov FROM  Filmi JOIN Zvrsti_filma ON id = film WHERE
                  naslov LIKE %?%
                  AND leto IS BETWEEN ? AND ?
                  AND ocena IS BETWEEN ? AND ?
                  AND zvrst = ?''' ,
                  [beseda, leto_zacetek, leto_konec, ocena_min, ocena_max, id_zvrsti])
    naslovi = c.fetchall()
    c.close()
    return naslovi

def filmi_zvrsti():
    c = baza.cursor()
    c.execute('''SELECT * FROM Zvrsti''')
    zvrsti = c.fetchall()
    c.close()
    return zvrsti

def film_igralci(ime_igralca):
    c = baza.cirsor()
    c.execute('''SELECT id, naslov FROM Filmi JOIN 

    
    


    
baza = sqlite3.connect(datoteka_baze, isolation_level = None)
