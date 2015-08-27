import bottle
import model
import sqlite3
import hashlib
import random

bottle.debug(True)

static_dir = "./static"

@bottle.route("/static/<filename:path>")
def static(filename):
    """Splošna funkcija, ki servira vse statične datoteke iz naslova
       /static/..."""
    return bottle.static_file(filename, root=static_dir)

# Skrivnost za kodiranje cookijev
secret = 'najajca skrivnost evrrr njvsoancsahucdhucbsu'

# Funkcija, ki v cookie spravi sporocilo
def set_sporocilo(tip, vsebina):
    bottle.response.set_cookie('message', (tip, vsebina), path='/', secret=secret)

# Funkcija, ki iz cookija dobi sporočilo, če je
def get_sporocilo():
    sporocilo = bottle.request.get_cookie('message', default=None, secret=secret)
    bottle.response.delete_cookie('message')
    return sporocilo

def get_user():
    """Poglej cookie in ugotovi, kdo je prijavljeni uporabnik,
       vrni njegov username in ime. Če ni prijavljen, presumeri
       na stran za prijavo ali vrni None (advisno od auto_login).
    """
    # Dobimo username iz piškotka
    username = bottle.request.get_cookie('username', secret=secret)
    # Preverimo, ali ta uporabnik obstaja
    if username is not None:
        r = model.kukiji(username)
        if r is not None:
            # uporabnik obstaja, vrnemo njegove podatke
            return r[0]
    # Če pridemo do sem, uporabnik ni prijavljen
    else:
        return None

################################################
@bottle.route('/')
@bottle.view('homepage')
def homepage_get():
    up_ime = get_user()
    id_up = model.id_uporabnika(up_ime)
    filmi = model.iskanje_filmov()
    random.shuffle(filmi)
    od = random.randint(0,len(filmi)-5)
    return{'up_ime' : up_ime,
           'id_up' : id_up,
           'filmi' : filmi[od:od+5]
           }

@bottle.route('/iskanje/')
@bottle.view('iskanje')
def iskanje():
    ime = bottle.request.query.ime
    letoOd = bottle.request.query.letoOd
    letoDo = bottle.request.query.letoDo
    ocenaMin = bottle.request.query.ocenaMin
    ocenaMax = bottle.request.query.ocenaMax
    zvrst = bottle.request.query.zvrst
    igralec = bottle.request.query.igralec

    if letoOd == '' : letoOd = 1000
    if letoDo == '' : letoDo = 3000
    if ocenaMin == '' : ocenaMin = 0
    if ocenaMax == '' : ocenaMx = 10
    
    filmi1 = model.iskanje_filmov(beseda=ime, leto_zacetek=letoOd, leto_konec=letoDo, ocena_min=ocenaMin, ocena_max=ocenaMax, zvrst=zvrst)
    filmiIgralec = model.iskanje_po_igralcih(ime_igralca=igralec)

    if igralec == '': filmi = filmi1
    else: filmi = filmiIgralec
    
    return {'filmi': filmi
            }



@bottle.route('/film/<id>')
@bottle.view('film')
def film(id):
    id_filma = id
    up_ime = get_user()
    id_up = model.id_uporabnika(up_ime)
    naslov, trajanje, ocena, opis, reziser, scenarist, leto = model.podatki_filma(id)
    zvrsti = model.zvrsti_filma(id)
    igralci = model.podatki_igralci(id)
    komentarji = model.pokazi_komentarje(id)
    if up_ime:
        predlog = model.lahko_doda_predlog(id_up[0], id)
    else:
        predlog = None
    return {'naslov' : naslov,
                'trajanje' : trajanje,
                'ocena' : ocena,
                'opis': opis,
                'reziser' : reziser,
                'scenarist': scenarist,
                'leto' : leto,
                'zvrsti' : zvrsti,
                'igralci' : igralci,
                'komentarji' : komentarji,
                'id_filma' : id_filma,
                'up_ime' : up_ime,
                'id_up' : id_up,
                'predlog' : predlog
                }
@bottle.route('/zelimPogledat/<id>/')
def zelimPogledat(id):
    up_ime = get_user()
    id_up = model.id_uporabnika(up_ime)
    model.dodaj_predlog(id_up[0], id)
    naslov = '/film/' + str(id)
    bottle.redirect(naslov)

@bottle.route('/komentiraj/<id>/')
def komentiraj(id):
    up_ime = get_user()
    id_up = model.id_uporabnika(up_ime)
    komentar = bottle.request.query.komentar
    model.komentiranje(id_up[0], id, komentar)
    naslov = '/film/' + str(id)
    bottle.redirect(naslov)

@bottle.route('/vseckanje/<id_filma>/<id:int>/')
def vseckanje(id_filma,id):
    up_ime = get_user()
    id_up = model.id_uporabnika(up_ime)

    if id == 1 : ocena = True
    if id == 0 : ocena = False
    
    model.oceni(id_up[0], id_filma, ocena)
    naslov = '/film/' + str(id_filma)
    bottle.redirect(naslov)


@bottle.route('/vsi/')
@bottle.view('iskanje')
def vsi():
    filmi = model.iskanje_filmov()
    return {'filmi' : filmi
            }
    


@bottle.route('/uporabnik/')
@bottle.view('uporabnik')
def uporabnik():
    up_ime = bottle.request.query.up_ime
    geslo = bottle.request.query.geslo
    id_up = model.preveri_geslo(up_ime, geslo)
    if id_up is None:
        return {'obstaja' : False,
                'up_ime' : up_ime,
                'id_up' : id_up}
    else:
        bottle.response.set_cookie('username', up_ime, path='/', secret=secret)
        naslov = '/uporabnik/' + str(id_up)
        bottle.redirect(naslov)



@bottle.route('/uporabnik/<id>')
@bottle.view('uporabnik')
def uporabnikID(id):
    # Iz cookieja dobimo uporabnika (ali ga preusmerimo na zaèetno stran, če
    # nima cookija)
    up_ime = get_user()
    if up_ime is None:
        bottle.redirect('/')
    
    vsecni = model.pokazi_vsecniFilmi(id)
    nevsecni = model.pokazi_nevsecniFilmi(id)
    za_pogledat= model.pokazi_filmiZaPogledat(id)

    return {'obstaja' : True,
                'vsecni' : vsecni,
                'nevsecni' : nevsecni,
                'poglej' : za_pogledat,
                'id_up' : id,
                'up_ime' : up_ime
                }


@bottle.route('/predlogi/<id>')
def predlog(id):
    model.dodaj_predloge_glede_na_oceno(id)
    naslov = '/uporabnik/' + str(id)
    bottle.redirect(naslov)


@bottle.get('/registracija/')
@bottle.view('registracija')
def registracija_get():
    """Prikaži formo za registracijo."""
    return {'napaka' : None,
            'up_ime' : None
            }

@bottle.post('/registracija/')
@bottle.view('registracija')
def registracija_post():
    up_ime = bottle.request.forms.up_ime
    geslo = bottle.request.forms.geslo
    id_up = model.dodaj_uporabnika(up_ime, geslo)
    if id_up is None:
 
        return {'napaka' : 'Uporabniško ime že obstaja',
                'up_ime' : up_ime
                }
    else:
        bottle.response.set_cookie('username', up_ime, path='/', secret=secret)
        naslov = '/uporabnik/' + str(id_up)
        bottle.redirect(naslov)

    
@bottle.get("/odjava/")
def logout():
    """Pobriši cookie in preusmeri na login."""
    bottle.response.delete_cookie('username', path='/')
    bottle.redirect('/')


################################################

bottle.run(host='localhost', port=8080)
