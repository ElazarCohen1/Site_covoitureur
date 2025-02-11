import decimal

from flask import Flask, render_template, request, redirect, url_for, session
import db as d
import functools
from passlib.context import CryptContext
ALLOWED_KWORD_TRAJET_EN_COURS = ("past", "all", "post", "mine")

import  psycopg2 as pg
import random, db, datetime, time, pprint

def force_two_char(value):
    if value < 0: return str(value)
    if value < 10: return '0' + str(value)
    return str(value)
app = Flask(__name__)
app.secret_key = "gjHXBc4DTLUqpM6_AKMDhaR0-8GuceDTAr-sGSywAb0a06WehR4Yf5KUrAk5burb4umoyqXI7Sq6GjLkOpyOrgiinYSHUWh3SvQCYmUuse3q85R0MRIz62OxtLiqZ76VvdzolA"
password_ctx = CryptContext(schemes=['bcrypt'])


def needs_login(func):
    @functools.wraps(func)
    def news(*args, **kwargs):
        if not session.get("email"): return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        return func(*args, **kwargs)

    return news


#des qu'on arrive sur le site
@app.route("/")
def main()->None:
    return redirect(url_for("accueil"))


#page d'accueil
@app.route("/accueil")
def accueil()->str:
    if session:
        return render_template("accueil.html",connecte = True)
    else:
        return render_template("accueil.html",connecte = False)


# la page du formulaire de connexion
@app.route("/connexion",methods = ["GET"])
def connexion()->None:
    return render_template("connexion.html")


#verifier le formulaire de connexion
@app.route("/res_form_connexion",methods = ["POST"])
def res_form_connexion()->None:
    email:str = request.form.get("email",None)
    mdp:str = request.form.get("mdp",None)
    mdp_hash = None
    emailb = None
    connected = None
    with db.connect() as connect:
        with connect.cursor() as cur:
            cur.execute("SELECT mdp,email,prenom,nom,addresse,date_naissance,argent FROM covoitureur WHERE email = %s;",(email,))
            for val in cur:
                mdp_hash = val.mdp
                emailb = val.email
                nom = val.nom
                prenom = val.prenom
                addresse = val.addresse
                date_naissance = val.date_naissance

    if not email or not mdp:
        return redirect(url_for("connexion"))


    elif not emailb or email != emailb :
        if session:
            connected = True
        else:
            connected = False
        return render_template("erreur.html",connected = connected,error = "mail")

    elif email == emailb and password_ctx.verify(mdp, mdp_hash) == False:
        if session:
            connected = True
        else:
            connected = False
        return render_template("erreur.html",connected = connected,error = "mdp")
    
    if "email" not in session :
        session["email"] = emailb
        session["nom"] = nom
        session["prenom"] = prenom
        session["addresse"] = addresse
        session["date_naissance"] = date_naissance

    return render_template("accueil.html",connecte= True)

@app.route("/inscription",methods = ["GET"])
def inscription()->None:
    return render_template("inscription.html")

#verifier l'inscription
@app.route("/res_form",methods = ["POST"])
def res_form():
    email:str = request.form.get("email",None)
    nom:str = request.form.get("nom",None)
    prenom:str = request.form.get("prenom",None)
    addresse:str= request.form.get("addresse",None)
    date_naissance:int = request.form.get("date_naissance",None)
    mdp1:str = request.form.get("mdp1",None)
    mdp2:str = request.form.get("mdp2",None)
    if len(email) <= 5:
        return redirect(url_for("inscription"))
    
    elif mdp1 != mdp2:
        return redirect(url_for("inscription"))
    
    elif len(nom) < 2 or len(prenom) < 2 or len(addresse) < 2:
        return redirect(url_for("inscription"))
    
    else:
        hash_pw = password_ctx.hash(mdp1)
        with d.connect() as connect:
            with connect.cursor() as cur:
                cur.execute(
                    "Select email FROM covoitureur WHERE email = %s",
                    (email,)
                )
                for val in cur:
                    if val.email:
                        return redirect(url_for("inscription"))
            with connect.cursor() as cur2:
                cur2.execute(
                    "INSERT INTO covoitureur (email,nom,prenom,addresse,date_naissance,mdp) VALUES (%s,%s,%s,%s,%s,%s);",
                    (email,nom,prenom,addresse,date_naissance,hash_pw)
                )
        session["email"] = email
        session["nom"] = nom
        session["prenom"] = prenom
        session["addresse"] = addresse
        session["date_naissance"] = date_naissance
        return redirect(url_for("connexion"))
    
       
#acces au profil 
@app.route("/profil",methods = ["GET","POST"])
@needs_login
def profil()->str:
    email:str = None
    dico_donnee:dict = {}
    lst_vehicules:list  = []
    lst_trajet:list = [] # liste de dictionnaire
    lst_filleul:list = []
    lst_argent:list = []
    lst_operation_passager:list = []

    today = datetime.date.today()
    email:str = session["email"]
    
    with d.connect() as connect:
        with connect.cursor() as cur:
            cur.execute(
                "SELECT nom,prenom,addresse,date_naissance,numero_permis,argent,parrain FROM covoitureur WHERE email = (%s)",
                (email,)
            )
            for val2 in cur:
                dico_donnee["nom"] = val2.nom
                dico_donnee["prenom"] = val2.prenom
                dico_donnee["email"] = email
                dico_donnee["addresse"] = val2.addresse
                dico_donnee["date_naissance"] = val2.date_naissance
                if not val2.numero_permis:
                    dico_donnee["numero_permis"] = None
                else:
                    dico_donnee["numero_permis"] = val2.numero_permis
                if not val2.argent:
                    dico_donnee["argent"] = 0
                else:
                    dico_donnee["argent"] = val2.argent
                if not val2.parrain:
                    dico_donnee["parrain"] = None
                else :
                    dico_donnee["parrain"] = val2.parrain
        with connect.cursor() as cur2:
            cur2.execute(
                "SELECT email FROM covoitureur WHERE parrain = %s;",
                (email,)
            )
            res = cur2.fetchall()
            for val in res:
                if val.email:
                    lst_filleul.append(val.email)
                    dico_donnee["filleul"] = lst_filleul
                else:
                    dico_donnee["filleul"] = None

        with connect.cursor() as cur3:
            cur3.execute(
                "SELECT immatriculation FROM vehicules WHERE proprietaire = %s;",
                (email,)
            )
            res = cur3.fetchall()
            for i in range(len(res)):
                lst_vehicules.append(res[i].immatriculation)

        with connect.cursor() as cur4:
            cur4.execute(
                "SELECT id_trajet,duree_trajet,nb_km,vehicule,cout_trajet, date" 
                " FROM trajet JOIN vehicules ON trajet.vehicule = vehicules.immatriculation " 
                " JOIN covoitureur ON vehicules.proprietaire = covoitureur.email" 
                " WHERE email = %s AND status = True AND date <= %s ORDER BY date DESC;",
                (email,today,)
            )
            res = cur4.fetchall()
            for val in res:
                dico_trajet:dict = {}
                dico_trajet["duree_trajet"] = val.duree_trajet
                dico_trajet["nb_km"] = val.nb_km
                dico_trajet["vehicule"] = val.vehicule
                dico_trajet["cout_trajet"] = val.cout_trajet
                dico_trajet["date"] = val.date
                dico_trajet["id_trajet"] = val.id_trajet
                lst_trajet.append(dico_trajet)

        if dico_donnee["numero_permis"]:
            with connect.cursor() as cur5:
                cur5.execute(
                    "SELECT id_trajet,cout_trajet,date FROM trajet "
                    " JOIN vehicules ON vehicules.immatriculation = trajet.vehicule "
                    " JOIN covoitureur ON covoitureur.email = vehicules.proprietaire  "
                    "WHERE email = %s AND date <= %s AND status = True ORDER BY date ;",
                    (email,today,)
                )
                res = cur5.fetchall()
                for val in res:
                    cout = 80/100* int(val.cout_trajet)
                    cout = round(cout,5)
                    lst_argent.append((val.date,cout,val.id_trajet))
            with connect.cursor() as cur7:
                cur7.execute(
                "SELECT trajet.id_trajet,trajet.date,cout_trajet FROM etape "
                " JOIN trajet ON etape.id_trajet = trajet.id_trajet "
                " JOIN vehicules ON trajet.vehicule = vehicules.immatriculation "
                "JOIN covoitureur ON covoitureur.email = vehicules.proprietaire"
                " WHERE est_depart_de = %s AND est_depart_de <> email  AND trajet.date <= %s  AND trajet.status = True ORDER BY trajet.date; ",
                (email,today,)
                )

                with connect.cursor() as cur8:
                    cur8.execute(
                        "SELECT count(est_depart_de) AS nb_passager FROM etape "
                    " JOIN trajet ON etape.id_trajet = trajet.id_trajet "
                    " JOIN vehicules ON trajet.vehicule = vehicules.immatriculation "
                    "JOIN covoitureur ON covoitureur.email = vehicules.proprietaire"
                    " WHERE est_depart_de = %s AND est_depart_de <> email AND trajet.date <= %s  AND trajet.status = True"
                    "  GROUP BY trajet.id_trajet ORDER BY trajet.date;",
                    (email,today,)
                    )
                    res = cur7.fetchall()
                    res2 = cur8.fetchone()
                    for val in res:
                        cout:float = val.cout_trajet/res2.nb_passager
                        lst_operation_passager.append((val.date,cout,val.id_trajet))



    return render_template("profil.html",dico_donnee = dico_donnee,lst_vehicules = lst_vehicules,lst_trajet = lst_trajet,lst_operation = lst_argent,lst_operation_passager = lst_operation_passager)


#que si on a pas de permis 
@app.route("/ajout_permis",methods = ["POST"])
@needs_login
def ajout_permis():
    permis:str = request.form.get("permis",None)
    email = session["email"]
    if not permis:
        return render_template("erreur.html",connected = True,error = "permis")

    with d.connect() as connect:
        with connect.cursor() as cur:
            cur.execute(
                "UPDATE covoitureur SET numero_permis = %s WHERE email = %s;",
                (permis,email,)
            )
    return redirect("profil")


@app.route("/supprimer_permis/<string:num_permis>",methods = ["POST"])
@needs_login
def supprimer_permis(num_permis):
    email:str = session["email"]
    with d.connect() as connect:
        with connect.cursor() as cur:
            cur.execute(
                "UPDATE covoitureur SET numero_permis = NULL WHERE email = %s",
                (email,)
            )

    return redirect("/profil")

#fonction pour verifier le critair si on modifie le vehicule ou on en ajoute un 
def verifier_crit_air(crit_Air:str)->bool:
    lst_crit_Air:list = ["E","1","2","3","4","5"]
    if str(crit_Air) not in lst_crit_Air:
        return False
    else:
        return True

#la page pour voir sa voiture 
@app.route("/res_voiture",methods = ["POST"])
def res_voiture():
    dico_vehicules:dict = {}
    immatriculation:str = request.form.get("vehicule",None)
    lst_sponsor:list = []
    lst_dic_sponsor:list = []

    with d.connect() as connect:
        with connect.cursor() as cur:
            cur.execute(
                "SELECT immatriculation,modele,nombre_places,couleur,type_carburant,crit_Air "
                " FROM vehicules WHERE immatriculation  = %s;",
                (immatriculation,)
            )
            for val in cur:
                dico_vehicules["immatriculation"] = val.immatriculation
                dico_vehicules["modele"] = val.modele
                dico_vehicules["nombre_places"] = val.nombre_places
                dico_vehicules["couleur"] = val.couleur
                dico_vehicules["type_carburant"] = val.type_carburant
                dico_vehicules["crit_Air"] = val.crit_air
        with connect.cursor() as cur2:
            cur2.execute(
                "SELECT nom,nature_pub,remuneration FROM sponsorise NATURAL JOIN sponsor "
                " WHERE immatriculation = %s;",
                (immatriculation,)
            )
            res = cur2.fetchall()
            for val in res:
                dico_sponsor:dict = {}
                dico_sponsor["nom"] = val.nom
                dico_sponsor["nature_pub"] = val.nature_pub
                dico_sponsor["remuneration"] = val.remuneration
                lst_dic_sponsor.append(dico_sponsor)
                
    with connect.cursor() as cur3:
            cur3.execute(
                "SELECT id_sponsor,nom,remuneration,nature_pub,duree_trajet FROM sponsor;"
            )
            res = cur3.fetchall()
            for val in res:
                lst_sponsor.append((val.nom,val.id_sponsor))
    return render_template("vehicule.html",dico_vehicules = dico_vehicules,lst_sponsor = lst_sponsor,lst_dic_sponsor = lst_dic_sponsor)


@app.route("/modif_vehicule",methods=["POST"])
@needs_login
def modif_vehicule():
    
    immatriculation:str = request.form.get("immatriculation",None)
    modele:str = request.form.get("modele",None)
    nombre_place:str = request.form.get("nombre_place",None)
    couleur:str = request.form.get("couleur",None)
    type_carburant:str = request.form.get("type_carburant",None)
    crit_Air:str = request.form.get("crit_Air",None)
    email:str = session["email"]
    lst_vehicule:list = [immatriculation,modele,nombre_place,couleur,type_carburant,crit_Air]
    
    if not verifier_type_carburant(type_carburant) or not verifier_crit_air(crit_Air):
        return render_template("erreur.html",connected = True,error = "carburant")
    
    with d.connect() as connect:
                
        with connect.cursor() as cur2:
            cur2.execute(
                " UPDATE vehicules SET"
                " modele = %s,"
                " nombre_places = %s,"
                " couleur = %s,"
                " type_carburant = %s,"
                " crit_Air = %s"
                " WHERE proprietaire = %s AND immatriculation = %s ",
                (modele,nombre_place,couleur,
                    type_carburant,crit_Air,email,immatriculation)
            )
    return redirect(url_for("profil"))
#sponsoriser son vehicule 
@app.route("/sponso_vehicule/<string:immatriculation>",methods = ["POST"])
@needs_login
def sponso_vehicule(immatriculation):
    sponsor:str = request.form.get("sponsor",None)
    if not sponsor:
        return render_template("erreur.html",connected = True,error = "not_sponsor")
    with d.connect() as connect:
        with connect.cursor() as cur:
            cur.execute(
                "SELECT id_sponsor, immatriculation FROM sponsorise WHERE id_sponsor = %s AND immatriculation = %s",
                (sponsor,immatriculation,)
            )
            for val in cur:
                if val.immatriculation  == immatriculation and int(sponsor) == int(val.id_sponsor):
                    return render_template("erreur.html",connected = True,error = "immatriculation_existante")

            with connect.cursor() as cur2 :
                cur2.execute(
                    "INSERT INTO sponsorise (id_sponsor,immatriculation) VALUES (%s,%s);",
                    (sponsor,immatriculation,)
                )
    return redirect("/profil")

@app.route("/deconnexion",methods=["GET","POST"])
@needs_login
def deconnexion():
    session.clear()
    return redirect(url_for("accueil"))



@app.route("/trajet")
@needs_login
def _trajet()->str:
    start = time.perf_counter()
    offset = request.args.get("page", 0)
    print(time.perf_counter() - start)
    with db.connect() as conn:
        print(time.perf_counter() - start)
        with conn.cursor() as cur:
            today = datetime.date.today();
            print(time.perf_counter() - start)
            cur.execute("SELECT id_trajet, date, cout_trajet, nom, prenom, nombre_places FROM trajet AS t JOIN vehicules AS v"
                        " ON t.vehicule = v.immatriculation "
                        " JOIN covoitureur AS c ON c.email = v.proprietaire"
                        " WHERE date >= '%s-%s-%s' AND NOT status"
                        " ORDER BY date LIMIT 20 OFFSET %s;", (today.year, today.month, today.day, offset))

            ids = []
            date = []
            couts = []
            prop = []
            nb_pl = []
            for elt in cur:
                ids.append(elt.id_trajet)
                date.append(f"{elt.date.day}/{elt.date.month}/{elt.date.year}")
                couts.append(elt.cout_trajet)
                prop.append(elt.prenom + " " + elt.nom)
                nb_pl.append(elt.nombre_places)
    print(time.perf_counter() - start)
    return render_template(
        "trajet.html",
        previousOffset=max(0, int(offset) - 20),
        nextPageOffset=int(offset) + 20,
        nbtrajet=len(ids),
        id_s=ids,
        dates=date,
        couts=couts,
        proprio=prop,
        nb_places=nb_pl
    )

@app.route("/trajet_en_cours/<string:param>")
@needs_login
def trajet_en_cours(param)->str:
    user = session.get("email")
    if param not in ALLOWED_KWORD_TRAJET_EN_COURS:
        return redirect("/trajet_en_cours/post")
    past = param == "past"
    mine = param == "mine"
    all = param == "all" or mine
    cmp = ">=" if not past else "<="
    date = datetime.date.today() if not all else datetime.date.min if not past else datetime.date.max
    lst = []
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT t.id_trajet AS idt, c.nom || ' ' || c.prenom AS name, t.date, c.email FROM etape AS e "
                        "JOIN trajet AS t ON t.id_trajet = e.id_trajet "
                        "JOIN vehicules AS v ON v.immatriculation = t.vehicule "
                        "JOIN covoitureur AS c ON c.email = v.proprietaire "
                        f"WHERE est_depart_de = %s AND t.date {cmp} %s "
                        "ORDER BY t.date ASC;", (user, date))
            for line in cur:
                if mine and line.email != user: continue # On le fais ici pour éviter de faire 20 variantes de la requète SQL
                lst.append(tuple(line))
    return render_template(
        "trajet_en_cours.html",
                          list_trajet=lst,
                          isEmpty= not len(lst)
                           )


@app.route("/trajet_form")
@needs_login
def t_form() -> str:
    user = session.get("email")
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT immatriculation AS id FROM vehicules WHERE proprietaire = %s;", (user,))
            immatriculations = [item.id for item in cur]
    return render_template("new_trajet_form.html", immatriculations=immatriculations)

def time_cmp(string_1: str, string_2 : str) -> bool:
    a = string_1.split(":")
    b = string_2.split(":")
    if int(a[0]) == int(b[0]):
        return int(a[1]) >= int(b[1])
    return int(a[0]) >= int(b[0])


def append_localisation(conn, name:str, adresse : str, desc: str, ville: str) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT id_localisation FROM localisation WHERE"
                    " nom = %s AND addresse = %s AND ville = %s;",
                    (name, adresse, ville))
        old_idl = cur.fetchone()
    if old_idl:
        print("On prend le vieux")
        return old_idl.id_localisation
    with conn.cursor() as cur:
        cur.execute("INSERT INTO localisation(nom, addresse, description, ville) VALUES"
                    "(%s, %s, %s, %s) RETURNING id_localisation;",
                    (name, adresse, desc, ville))
        idl: int = cur.fetchone().id_localisation
    print(f"""
Id : {idl},
Nom : {name},
Adresse : {adresse},
Description : {desc},
Ville : {ville}
""")
    return idl

def get_average_note(conn, user_email: str) -> tuple[float, int]:
    with conn.cursor() as cur:
        cur.execute("SELECT note FROM evalue WHERE cible = %s;", (user_email,))
        lst = list(map(lambda elt: elt.note, cur))
        moyenne = sum(lst) / max(len(lst), 1)
    return round(moyenne, 2), len(lst)

@app.route("/trajet_form_post", methods=["POST"])
@needs_login
def post_tform() -> str:
    user = session.get("email")
    start_time = request.form.get("start_time")
    # start_loc = request.form.get("loc_id_s")
    end_time = request.form.get("end_time")
    # end_loc = request.form.get("loc_id_e")
    vehicule = request.form.get("vehicules")
    date = request.form.get("date")
    kms = min(float(request.form.get("kms")), 999.99)
    cost = request.form.get("cost")
    tdate = datetime.datetime.strptime(date, "%Y-%m-%d")
    a = datetime.datetime.strptime(start_time, "%H:%M")
    b = datetime.datetime.strptime(end_time, "%H:%M")
    #if a > b:
      #  return redirect("/trajet")
    #if tdate < datetime.datetime.today():
     #   return redirect("/trajet")
    with db.connect() as conn:
        start_loc = append_localisation(conn,
                                        request.form.get("start_name", ""),
                                        request.form.get("start_adresse", ""),
                                        request.form.get("start_desc", ""),
                                        request.form.get("start_city", ""))
        end_loc = append_localisation(conn,
                                        request.form.get("end_name", ""),
                                        request.form.get("end_adresse", ""),
                                        request.form.get("end_desc", ""),
                                        request.form.get("end_city", ""))
        # Ajout du trajet
        with conn.cursor() as cur:
            cur.execute("INSERT INTO trajet(date, cout_trajet, status, duree_trajet, nb_km, vehicule) VALUES "
                             "(%s, %s, FALSE, %s, %s, %s) RETURNING id_trajet;", (date, cost, b - a, kms, vehicule))
            id = cur.fetchone().id_trajet
        with conn.cursor() as cur:
            cur.execute("INSERT INTO etape(heure_prevu, status, id_trajet, id_localisation, est_depart_de, est_arrive_de) VALUES"
                        "(%s, TRUE, %s, %s, %s, NULL), "
                        "(%s, TRUE, %s, %s, NULL, %s);",
                        (a, id, start_loc, user, b, id, end_loc, user))
    return redirect("/trajet")


@app.route("/loc/<int:id_loc>/post_comment", methods=["POST"])
@needs_login
def post_comment(id_loc):
    user = session.get("email")
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM commente where email = %s AND id_localisation = %s", (user, id_loc))
            exist = cur.fetchone() is not None
        if exist:
            with conn.cursor() as cur:
                cur.execute("UPDATE commente SET commentaire = %s WHERE email = %s AND id_localisation = %s",
                            (request.form.get("com"),user, id_loc))
        else:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO commente VALUES (%s, %s, %s)", (user, id_loc, request.form.get("com")))
    return redirect(f'/loc/{id_loc}')

@app.route("/loc/<int:id_loc>")
@needs_login
def pres_loc(id_loc):
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT nom, addresse || ' ' || ville AS adrs, description FROM localisation WHERE id_localisation = %s ", (id_loc,))
            misc = cur.fetchone()
        with conn.cursor() as cur:
            cur.execute("SELECT email, commentaire FROM commente WHERE id_localisation = %s", (id_loc,))
            comments = list(map(lambda elt: (elt.email, elt.commentaire), cur))
    if not misc:
        return redirect("/")
    return render_template("localisation_pres.html",
                           name= misc.nom,
                           addresse=misc.adrs,
                           id_loc=id_loc,
                           description=misc.description,
                           comments=comments)


def verifier_type_carburant(carburant: str) -> bool:
    lst_types_carburant: list = [
        "essence", "diesel", "gpl", "ethanol", "bioéthanol", "biodiesel",
        "gaz naturel", "electricité", "eybride", "hybride rechargeable",
        "hydrogène", "e-carburants", "hvo", "kérosène", "charbon", "electrique",
        "sp-95", "electicite"
    ]
    return not carburant.lower() not in lst_types_carburant


@app.route("/gerer_vehicule", methods=["POST"])
def gerer_vehicule():
    immatriculation: str = request.form.get("immatriculation", None)
    modele: str = request.form.get("modele", None)
    nombre_place: str = request.form.get("nombre_place", None)
    couleur: str = request.form.get("couleur", None)
    type_carburant: str = request.form.get("type_carburant", None)
    crit_Air: str = request.form.get("crit_Air", None)
    email: str = session["email"]
    print("irjieozqfiazrhjsfomlzihrgo", str(crit_Air), type_carburant.lower())
    if not immatriculation or not modele or not nombre_place or not type_carburant or not crit_Air:
        return "erreur vous avez mal rentre un truc"

    if not verifier_type_carburant(type_carburant) or not verifier_crit_air(crit_Air):
        return render_template("erreur.html",connected = True,error = "carburant")

    with d.connect() as connect:
        with connect.cursor() as cur:
            cur.execute(
                "SELECT immatriculation FROM vehicules WHERE immatriculation = %s;",
                (immatriculation,)
            )
            res = cur.fetchall()
            for val in res:
                if val.immatriculation:
                    return render_template("erreur.html",connected = True,error = "immatriculation_existante")

        with connect.cursor() as cur2:
            cur2.execute(
                "INSERT INTO vehicules (immatriculation,modele,nombre_places,couleur,type_carburant,crit_Air,proprietaire)"
                "  VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (immatriculation, modele, nombre_place, couleur, type_carburant, crit_Air, email)
            )
    return redirect(url_for("profil"))

@app.route("/t-<int:trajet_id>/note_conducteur", methods=["POST"])
@needs_login
def grade(trajet_id):
    note = request.form.get("note", 0)
    actual_note = int(note) if note else 0
    with db.connect() as conn:
        with conn.cursor() as cur:
            if int(request.form.get("exists", 0)) :
                cur.execute("UPDATE evalue SET note = %s WHERE cible = %s AND source = %s",
                            (actual_note, request.form.get("cible"), session.get("email")))
            else:
                cur.execute("INSERT INTO evalue VALUES (%s, %s, %s)",
                            (session.get("email"), request.form.get("cible"), actual_note))
    return redirect(f"/t-{trajet_id}")

@app.route("/t-<int:id_trajet>/e-<int:id_etape>/post_true_time", methods=["POST"])
@needs_login
def post_true_time(id_trajet, id_etape) -> str:
    time = (request.form.get("time"))
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE etape SET heure_reel = %s WHERE id_etape = %s", (time,id_etape))
    return redirect(f"/t-{id_trajet}")


@app.route("/t-<int:trajet_id>")
@needs_login
def trajet(trajet_id) -> str:
    # Misc info du trajet
    user = session.get("email", None)
    if not user: return redirect('/')
    misc = None
    depart: tuple = None
    arrive: tuple = None
    tab: dict = {}
    note = -1
    with (db.connect() as conn):
        with conn.cursor() as cur:
            cur.execute("SELECT date, cout_trajet, status, duree_trajet, nb_km, modele, nombre_places, nom, prenom, email FROM trajet AS t "
                        "JOIN vehicules AS v ON t.vehicule = v.immatriculation "
                        "JOIN covoitureur AS c ON c.email = v.proprietaire "
                        "WHERE id_trajet = %s", (trajet_id,))
            misc = cur.fetchone()
        with conn.cursor() as cur:
            cur.execute("SELECT id_etape, heure_prevu, heure_reel, status, est_depart_de, est_arrive_de, l.nom AS lnom, c.email,"
                        " l.addresse AS laddresse, description, ville, c.nom AS cnom, prenom, id_localisation"
                        " FROM etape AS e NATURAL JOIN localisation AS l"
                        " LEFT JOIN covoitureur AS c ON c.email = e.est_depart_de WHERE id_trajet = %s;", (trajet_id,))
            for elt in cur:
                if elt.est_depart_de == misc.email:
                    depart = (elt.lnom, elt.laddresse, elt.ville, elt.description, elt.id_localisation)
                elif elt.est_arrive_de == misc.email:
                    arrive = (elt.lnom, elt.laddresse, elt.ville, elt.description, elt.id_localisation)
                elif elt.est_depart_de:
                    tab.setdefault(elt.est_depart_de, {})["user"] = elt.email
                    tab.setdefault(elt.est_depart_de, {})["valid"] = elt.status
                    tab.setdefault(elt.est_depart_de, {})["start_id"] = elt.id_etape
                    tab.setdefault(elt.est_depart_de, {})["heure_start"] = elt.heure_prevu
                    tab.setdefault(elt.est_depart_de, {})["true_start"] = elt.heure_reel
                    print("A:", elt.heure_reel)
                    tab.setdefault(elt.est_depart_de, {})["depart"] = (elt.lnom, elt.laddresse, elt.ville, elt.description, elt.id_localisation)
                elif elt.est_arrive_de:
                    tab.setdefault(elt.est_arrive_de, {})["heure_end"] = elt.heure_prevu
                    tab.setdefault(elt.est_arrive_de, {})["true_end"] = elt.heure_reel
                    print("B:", elt.heure_reel)
                    tab.setdefault(elt.est_arrive_de, {})["end_id"] = elt.id_etape
                    tab.setdefault(elt.est_arrive_de, {})["arrive"] = (elt.lnom, elt.laddresse, elt.ville, elt.description, elt.id_localisation)
        with conn.cursor() as cur:
            cur.execute("SELECT note FROM evalue WHERE source = %s AND cible = %s;", (user, misc.email))
            current_tuple = cur.fetchone()
            note = current_tuple.note if current_tuple is not None else -1
        avgn, nb_note = get_average_note(conn, misc.email)
    pprint.pprint(tab);
    return render_template("pres_trajet.html",
                           conducteur=misc.prenom + " " + misc.nom,
                           date=misc.date,
                           cost=misc.cout_trajet,
                           status=misc.status,
                           duree=str(misc.duree_trajet),
                           km_s=misc.nb_km,
                           dep=depart,
                           arr=arrive,
                           nbUsersEtapes=len(tab.keys()),
                           users=tuple(tab.keys()),
                           etapes=tab,
                           id=trajet_id,
                           isAdmin=(user == misc.email),
                           note=note,
                           orga=misc.email,
                           avgn=avgn, # Ha ha (C'est pour average note mais c'est rigolo)
                           nbnote=nb_note,
                           current_user=user,
                           )

@app.route("/t-<int:trajet_id>/propose", methods=["POST"])
@needs_login
def push_trajet(trajet_id):
    user = session.get("email", None)
    if not user: return redirect(f"/t-{trajet_id}")
    heure_debut = request.form.get("start_time", None)
    if not heure_debut: return redirect(f"/t-{trajet_id}")
    end_time = request.form.get("end_time", None)
    if not end_time: return redirect(f"/t-{trajet_id}")
    with db.connect() as conn:
        with conn.cursor() as cur:
            start_loc = append_localisation(conn,
                                            request.form.get("start_name", ""),
                                            request.form.get("start_adresse", ""),
                                            request.form.get("start_desc", ""),
                                            request.form.get("start_city", ""))
            end_loc = append_localisation(conn,
                                          request.form.get("end_name", ""),
                                          request.form.get("end_adresse", ""),
                                          request.form.get("end_desc", ""),
                                          request.form.get("end_city", ""))
            cur.execute(
                "INSERT INTO etape (heure_prevu, status, id_trajet, id_localisation, est_depart_de, est_arrive_de) VALUES"
                " (%s, FALSE, %s, %s, %s, NULL),"
                " (%s, FALSE, %s, %s, NULL, %s);",
                (heure_debut, trajet_id, start_loc, user, end_time, trajet_id, end_loc, user))
    return redirect(f"/t-{trajet_id}")


def payement(conn, id_trajet):
    with conn.cursor() as cur:
        cur.execute("SELECT email, parrain, cout_trajet FROM trajet AS t "
                    "JOIN vehicules AS v ON v.immatriculation = t.vehicule "
                    "JOIN covoitureur AS c ON c.email = v.proprietaire "
                    " WHERE id_trajet = %s;", (id_trajet,))
        result = cur.fetchone()
        recever = result.email
        parrain = result.parrain
        cost = result.cout_trajet
    with conn.cursor() as cur:
        cur.execute("SELECT est_depart_de AS email FROM etape "
                    " WHERE id_trajet = %s AND status;", (id_trajet,))
        result = cur.fetchall()
        payeur = tuple(map(lambda elt: elt.email, result))


    # Problème d'arrondie...
    cost_per_user = decimal.Decimal(cost / len(payeur))
    with conn.cursor() as cur:
        cur.execute("UPDATE covoitureur SET argent = argent - %s WHERE email in %s;",
                    (cost_per_user, payeur))
    with conn.cursor() as cur:
        cur.execute("UPDATE covoitureur SET argent = argent + %s WHERE email = %s;",
                    (decimal.Decimal(.8) * cost, recever))
    with conn.cursor() as cur:
        cur.execute("UPDATE covoitureur SET argent = argent + %s WHERE email = %s;",
                    (decimal.Decimal(.05) * cost, parrain))


def rembourse(conn, id_trajet):
    with conn.cursor() as cur:
        cur.execute("SELECT email, parrain, cout_trajet FROM trajet AS t "
                    "JOIN vehicules AS v ON v.immatriculation = t.vehicule "
                    "JOIN covoitureur AS c ON c.email = v.proprietaire "
                    " WHERE id_trajet = %s;", (id_trajet,))
        result = cur.fetchone()
        recever = result.email
        parrain = result.parrain
        cost = result.cout_trajet
    with conn.cursor() as cur:
        cur.execute("SELECT est_depart_de AS email FROM etape "
                    " WHERE id_trajet = %s;", (id_trajet,))
        result = cur.fetchall()
        payeur = tuple(map(lambda elt: elt.email, result))

    cost_per_user = decimal.Decimal(cost / len(payeur))
    with conn.cursor() as cur:
        cur.execute("UPDATE covoitureur SET argent = argent + %s WHERE email in %s;",
                    (cost_per_user, payeur))
    with conn.cursor() as cur:
        cur.execute("UPDATE covoitureur SET argent = argent - %s WHERE email = %s;",
                    (decimal.Decimal(.8) * cost, recever))
    with conn.cursor() as cur:
        cur.execute("UPDATE covoitureur SET argent = argent - %s WHERE email = %s;",
                    (decimal.Decimal(.05) * cost, parrain))



@app.route("/t-<int:id>/finalise", methods=["POST"])
@needs_login
def finalise(id):
    user = session.get("email", None)
    odl_status = request.form.get("is_locked", 0)
    with db.connect() as conn:
        if not (int(odl_status)):
            payement(conn, id)
            new_status = ("TRUE")
        else:
            rembourse(conn, id)
            new_status = "FALSE"
        with conn.cursor() as cur:
            cur.execute("SELECT proprietaire FROM trajet AS t JOIN vehicules AS v ON v.immatriculation = t.vehicule"
                        " WHERE t.id_trajet = %s;", (id,))
            t_user = cur.fetchone()
            if t_user.proprietaire != user:
                return redirect(f"/t-{id}")
        with conn.cursor() as cur:
            cur.execute("UPDATE trajet SET status = %s WHERE id_trajet = %s;", (new_status, id))
    return redirect(f"/t-{id}")

@app.route("/t-<int:id>/accept")
@needs_login
def accept_etape(id):
    tokens = request.args.get("token").split(">")
    id_a = int(tokens[0])
    id_b = int(tokens[1])
    result = "TRUE" if not int(tokens[2]) else "FALSE"
    user = session.get("email", None)
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT proprietaire FROM trajet AS t JOIN vehicules AS v ON v.immatriculation = t.vehicule"
                        " WHERE t.id_trajet = %s;", (id,))
            t_user = cur.fetchone()
            if t_user.proprietaire != user:
                return redirect("/")
        with conn.cursor() as cur:
            cur.execute("UPDATE etape SET status = %s WHERE id_etape = %s AND id_trajet = %s;", (result, id_a, id))
        with conn.cursor() as cur:
            cur.execute("UPDATE etape SET status = %s WHERE id_etape = %s AND id_trajet = %s;", (result, id_b, id))
    return redirect(f"/t-{id}")


@app.route("/statistiques")
def statistiques()->str:
    kms = 0
    s_kms = 0
    lieux = []
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT SUM(nb_km) AS sum FROM trajet;")
            kms = cur.fetchone().sum
        with conn.cursor() as cur:
            cur.execute("SELECT SUM(nb_km) AS sum FROM trajet "
                        "WHERE vehicule IN "
                        "(SELECT immatriculation FROM sponsorise);")
            s_kms = cur.fetchone().sum
        with conn.cursor() as cur:
            cur.execute("SELECT addresse || ' ' || ville AS place, count FROM TopLocation;")
            lieux = map(lambda elt: (elt.place, elt.count), cur.fetchall())
    return render_template("statistiques.html",
                           ttKm=kms,
                           nbSponso=s_kms,
                           topLieux=lieux,
                           connecte=session.get("email"))

@app.route("/search_result")
def search():
    terme = request.args.get("nom")
    if not request.args.get("nom"): return redirect("/accueil")
    print("ici !! ")
    with db.connect() as conn:
         with conn.cursor() as cur:
             today = datetime.date.today();
             cur.execute(
                 "SELECT id_trajet, date, cout_trajet, nom, prenom, nombre_places FROM trajet AS t JOIN vehicules AS v"
                 " ON t.vehicule = v.immatriculation "
                 " JOIN covoitureur AS c ON c.email = v.proprietaire"
                 " WHERE date >= '%s-%s-%s' AND EXISTS ("
                 " SELECT * FROM etape AS e NATURAL JOIN localisation WHERE "
                 " e.id_trajet = t.id_trajet AND ville LIKE %s "
                 ") AND NOT t.status"
                 " ORDER BY date;", (today.year, today.month, today.day, '%' + terme + '%'))


             ids = []
             date = []
             couts = []
             prop = []
             nb_pl = []
             for elt in cur:
                 ids.append(elt.id_trajet)
                 date.append(f"{elt.date.day}/{elt.date.month}/{elt.date.year}")
                 couts.append(elt.cout_trajet)
                 prop.append(elt.prenom + " " + elt.nom)
                 nb_pl.append(elt.nombre_places)
    return render_template(
        "trajet.html",
        previousOffset=-1,
        nextPageOffset=0,
        nbtrajet=len(ids),
        id_s=ids,
        dates=date,
        couts=couts,
        proprio=prop,
        nb_places=nb_pl
    )

if __name__=="__main__":
    app.run(debug=True)