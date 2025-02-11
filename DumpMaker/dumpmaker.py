import csv
import json
import random
import time, pprint
from functools import reduce
from passlib.context import CryptContext

HEADER = """
DROP TABLE IF EXISTS covoitureur CASCADE;
DROP TABLE IF EXISTS etape CASCADE;
DROP TABLE IF EXISTS trajet CASCADE;
DROP TABLE IF EXISTS localisation CASCADE;
DROP TABLE IF EXISTS sponsor CASCADE;
DROP TABLE IF EXISTS vehicules CASCADE;

DROP TABLE IF EXISTS sponsorise CASCADE;
DROP TABLE IF EXISTS commente CASCADE;
DROP TABLE IF EXISTS evalue CASCADE;


CREATE TABLE covoitureur(
    email  Varchar(100) primary key,
    nom  Varchar(50) NOT NULL,
    prenom  Varchar(50) NOT NULL,
    addresse  Varchar(100) NOT NULL,
    date_naissance date NOT NULL,    
    mdp char(60) NOT NULL,  -- Changer de 64 avec la nouvelle lib de hash
    numero_permis char(12), 
    argent numeric(11,2),
    parrain Varchar(100) references covoitureur(email) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE localisation( 
    id_localisation serial primary key,
    nom Varchar(50) NOT NULL,
    addresse Varchar(100) NOT NULL,
    description Varchar(500),
    ville  Varchar(64) NOT NULL
);

CREATE TABLE sponsor(
    id_sponsor serial primary key, 
    nom  Varchar(75) NOT NULL,
    nature_pub Varchar(500) NOT NULL,
    duree_trajet interval NOT NULL,
    remuneration numeric(11,2) NOT NULL
); 
    

CREATE TABLE vehicules(
    immatriculation char(7) primary key,
    modele Varchar(55) NOT NULL,
    nombre_places int NOT NULL,
    couleur Varchar(60) NOT NULL,
    type_carburant Varchar(50) NOT NULL,
    crit_Air char(1) NOT NULL CHECK(crit_Air IN ('E', '1', '2', '3', '4', '5')),
    proprietaire Varchar(100) REFERENCES covoitureur(email) ON DELETE CASCADE ON UPDATE CASCADE,
    CHECK (proprietaire IS NOT NULL)
);

CREATE TABLE trajet( 
    id_trajet serial primary key,
    date date NOT NULL,
    cout_trajet numeric(9,2) NOT NULL, 
    status  boolean default FALSE,
    duree_trajet interval NOT NULL, -- ajout par rapport au shemas 
    nb_km numeric(6,3) NOT NULL, -- ajout par rapport aux shemas 
    vehicule char(7) references vehicules(immatriculation)  ON DELETE SET NULL ON UPDATE CASCADE , 
    --email  Varchar(100) references covoitureur(email)  ON DELETE CASCADE ON UPDATE CASCADE,
    CHECK (vehicule IS NOT NULL ),
    CHECK (nb_km >= 0)
);

CREATE TABLE etape( 
    id_etape serial primary key,
    heure_prevu time NOT NULL,
    heure_reel time ,
    status boolean default FALSE,
    -- date date NOT NULL,
    id_trajet int references trajet(id_trajet) ON DELETE CASCADE , 
    id_localisation int references localisation(id_localisation)  ON DELETE CASCADE ,
    est_depart_de Varchar(100) references covoitureur(email) ON DELETE CASCADE ON UPDATE CASCADE,
    est_arrive_de  Varchar(100) references covoitureur(email) ON DELETE CASCADE ON UPDATE CASCADE
    CHECK (((est_depart_de IS NULL AND est_arrive_de IS NOT NULL)) OR (est_depart_de IS NOT NULL AND est_arrive_de IS NULL))
);


CREATE TABLE sponsorise(
    id_sponsor int references sponsor(id_sponsor)ON DELETE CASCADE,
    immatriculation char(7) references vehicules(immatriculation)ON DELETE CASCADE ON UPDATE CASCADE ,
    primary key(id_sponsor,immatriculation)
);
   
CREATE TABLE commente(
    email Varchar(100) references covoitureur(email) ON DELETE CASCADE ON UPDATE CASCADE ,
    id_localisation int references localisation(id_localisation) ON DELETE CASCADE,
    commentaire Varchar(500) NOT NULL,
    primary key(email,id_localisation)
);
  
CREATE TABLE evalue(
    source  Varchar(100) references covoitureur(email) ON DELETE CASCADE ON UPDATE CASCADE,
    cible Varchar(100) references covoitureur(email) ON DELETE CASCADE ON UPDATE CASCADE,
    note int NOT NULL,
    primary key(source,cible),
    CHECK (source <> cible)
);


CREATE VIEW TopLocation AS (
SELECT addresse , ville , COUNT(id_etape) FROM etape
NATURAL JOIN localisation
GROUP BY addresse , ville
ORDER BY COUNT(id_etape) DESC
LIMIT 10
);

CREATE VIEW SponsorKm AS (

SELECT id_sponsor , nom, SUM(nb_km) FROM Sponsor
NATURAL JOIN sponsorise NATURAL JOIN vehicules
JOIN trajet ON trajet.vehicule = vehicules.immatriculation
GROUP BY id_sponsor , nom
) ;
"""

EMAIL_HOST = ["orange.fr", "wanadoo.fr", "gmail.com", "univ-eiffel.fr", "proton.me"]
PASSWORD_CTX = CryptContext(schemes=["bcrypt"])
with open("liste-des-voies-de-la-commune.csv", "r", encoding="utf-8") as csvfile:
    csv_reader = csv.DictReader(csvfile, delimiter=";")
    STREET_LIST = [line["Libellé Voie"] for line in csv_reader]
with open("cities.json", "r", encoding="utf-8") as city:
    CITY_LIST = json.loads(city.read())["cities"]
with open("mots.txt", "r", encoding="utf-8") as mots:
    DICTIONARY = mots.read().split("\n")

def remove_accent(chaine: str) -> str:
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
    new_chaine = ""
    for char in chaine:
        new_chaine += char if char in allowed else "_"
    return new_chaine

def generate_covoitureur(nb_covoitureuer: int) -> tuple[str, set[str]]:
    start_time = time.perf_counter()
    with open("prenoms.txt", "r", encoding="utf-8") as prenoms:
        list_prenom = prenoms.read().split("\n")
    with open("nom_famille.txt", "r", encoding="utf-8") as noms:
        list_nom = noms.read().split("\n")
    chaine = "INSERT INTO covoitureur (email, nom, prenom, addresse, date_naissance, mdp, numero_permis, argent, parrain) VALUES\n"
    email_in = set()
    current_permis_num = random.randint(1111, 2222)
    iteration_end_time = []
    for i in range(nb_covoitureuer):
        iteration_start_time = time.perf_counter()
        nom : str = random.choice(list_nom)
        prenom : str = random.choice(list_prenom)
        initial_host_id : int =  random.randint(0, len(EMAIL_HOST) - 1)
        host_id : int = initial_host_id
        if " " in nom:
            mail_name = remove_accent(reduce(lambda acc, x: acc + x, nom.split(" "), ""))
        else: mail_name = nom
        email : str = f"{mail_name}.{remove_accent(prenom)}@{EMAIL_HOST[host_id]}"
        nb_email : int = random.randint(10, 30)
        while email in email_in:
            next_host_id : int = (host_id + 1) % len(EMAIL_HOST)
            if next_host_id != initial_host_id:
                host_id : int = next_host_id
                email : str = f"{mail_name}.{prenom}@{EMAIL_HOST[host_id]}"
            else:
                email : str = f"{mail_name}.{prenom}@{EMAIL_HOST[host_id]}"
                nb_email += 1
        ville: str = random.choice(CITY_LIST)
        mdp = reduce(lambda acc, x: acc + x, random.choice(list_prenom).split(" "), "") + "_" + reduce(lambda acc, x: acc + x, random.choice(CITY_LIST)["label"].split(" "), "") + str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9))
        mdp_hash = PASSWORD_CTX.hash(mdp)
        money = str(random.randint(25, 10_000)) + ".00"
        if email_in == set():
            parain = "NULL"
        else:
            parain = "NULL" if random.random() > 0.5 else f"'{random.choice(tuple(email_in))}'"
        num_permis = "NULL" if random.random() > 0.75 else f"'B{str(current_permis_num).ljust(5, '0')}'"
        current_permis_num += random.randint(1, 10)
        rue = random.choice(STREET_LIST)
        true_rue = ""
        for char in rue:
            if char == "'": true_rue += "''"
            else: true_rue += char
        separator = ";" if  i == nb_covoitureuer - 1 else ","
        chaine += f"\t('{email}', '{nom}', '{prenom}', '{random.randint(1, 200)} {true_rue}, {ville['zip_code']} {ville['label']}', '{random.randint(1960, 2015)}-{random.randint(1, 12)}-{random.randint(1, 28)}', '{mdp_hash}', {num_permis}, {money}, {parain}){separator} -- Mdp: {mdp}\n"
        email_in.add(email)
        iteration_end_time.append(time.perf_counter() - iteration_start_time)
        print(f"{i}e covoitureur généré en {iteration_end_time[-1]} seconde")
    end_time = time.perf_counter()
    print(f"""\n{nb_covoitureuer} covoitureur générée en {end_time - start_time}s
-----------------------------------------------------------------
Temps de création moyen d'un covoitureur : {sum(iteration_end_time)/nb_covoitureuer}
Plus longue itération : {max(iteration_end_time)}s
Plus courte itération : {min(iteration_end_time)}s
""")
    return chaine, email_in

def generate_location(nb_location : int) -> str:
    start_time = time.perf_counter()
    chaine: str = "INSERT INTO localisation (nom, addresse, description, ville) VALUES\n"
    iteration_end_time = []
    for i in range(nb_location):
        iteration_start_time = time.perf_counter()
        city = random.choice(CITY_LIST)["label"]
        rue = random.choice(STREET_LIST)
        true_rue = ""
        for char in rue:
            if char == "'":
                true_rue += "''"
            else:
                true_rue += char
        separator: str = ";" if  i == nb_location - 1 else ","
        description : str = f"Localisation se trouvant à {true_rue} {city} "
        chaine += f"\t('{f'{true_rue} {city}'[:50]}', '{random.randint(1, 200)} {true_rue}', '{description}', '{city}'){separator}\n"
        iteration_end_time.append(time.perf_counter() - iteration_start_time)
        print(f"{i}e localisation en {iteration_end_time[-1]} seconde")

    end_time = time.perf_counter()
    print(f"""\n{nb_location} localisation générée en {end_time - start_time}s
-----------------------------------------------------------------
Temps de création moyen d'une localisation : {sum(iteration_end_time) / nb_location}
Plus longue itération : {max(iteration_end_time)}s
Plus courte itération : {min(iteration_end_time)}s
""")
    return chaine
def sanitize(chaine: str) -> str:
    s = ""
    for char in chaine:
        if char == "'":
            s += "''"
        else:
            s += char
    return s


def generate_sponsor(nb_sponsor: int) -> str:
    start_time = time.perf_counter()
    with open("entreuprises.txt", "r", encoding="utf-8") as ent:
        entreuprises = ent.read().split("\n")
    chaine: str = "INSERT INTO sponsor (nom, nature_pub, duree_trajet, remuneration) VALUES\n"
    iteration_end_time = []
    for i in range(nb_sponsor):
        iteration_start_time = time.perf_counter()
        entreuprise = sanitize(random.choice(entreuprises))
        separator: str = ";" if i == nb_sponsor - 1 else ","
        chaine += f"\t('{entreuprise}', 'Publicité pour le/la  {random.choice(DICTIONARY)}', '{random.randint(20, 250)} minutes', {random.randint(100, 300)}.00){separator}\n"
        iteration_end_time.append(time.perf_counter() - iteration_start_time)
        print(f"{i}e sponsor {entreuprise} en {iteration_end_time[-1]} seconde")

    end_time = time.perf_counter()
    print(f"""\n{nb_sponsor} sponsors générée en {end_time - start_time}s
-----------------------------------------------------------------
Temps de création moyen d'une sponsor : {sum(iteration_end_time) / nb_sponsor}
Plus longue itération : {max(iteration_end_time)}s
Plus courte itération : {min(iteration_end_time)}s
""")
    return chaine


def next_imatriculation(tab: list[int]):
    assert len(tab) == 7
    nb_chiffres = 23, 23, 10, 10, 10, 23, 23
    for i in range(6, -1, -1):
        tab[i] = (tab[i] + 1) % nb_chiffres[i]
        if tab[i] != 0: break


def imatriculation_str(tab: list[int]) -> str:
    assert len(tab) == 7
    letters: str = "ABCDEFGHJKLMNPQRSTVWXYZ"
    chaine = ""
    for i in range(7):
        if 2 <= i <= 4: chaine += str(tab[i])
        else: chaine += letters[tab[i]]
    return chaine


def generate_vehicules(nb: int, list_email: tuple):
    start_time = time.perf_counter()
    couleurs = ["Bleu", "Rouge", "Noir", "Blanc", "Vert", "Jaune", "Gris", "Orange", "Violet", "Rose"]
    carburants = ["SP-95", "Diesel", "Electicite"]
    with open("car.json") as car:
        cars = [f"{c['make']} {c['model']}" for c in json.loads(car.read())["results"]]
    chaine: str = "INSERT INTO vehicules (immatriculation, modele, nombre_places, couleur, type_carburant, crit_Air, proprietaire) VALUES\n"
    indices: list[int] = [0, 0, 0, 0, 0, 0, 0]
    iteration_end_time = []
    list_imm = {}
    for i in range(nb):
        iteration_start_time = time.perf_counter()
        imatriculation : str = imatriculation_str(indices)
        next_imatriculation(indices)
        carburant = random.choice(carburants)
        critair = "E" if carburant == "Electicite" else random.choice("12345")
        separator: str = ";" if i == nb - 1 else ","
        proprio = random.choice(list_email)
        chaine += f"\t('{imatriculation}', '{random.choice(cars)}', {random.randint(2, 9)}, '{random.choice(couleurs)}', '{carburant}', '{critair}', '{proprio}'){separator}\n"
        list_imm.setdefault(proprio, set()).add(imatriculation)
        iteration_end_time.append(time.perf_counter() - iteration_start_time)
        print(f"{i}e vehicules en {iteration_end_time[-1]} seconde")
    end_time = time.perf_counter()
    print(f"""\n{nb} vehicules générée en {end_time - start_time}s
-----------------------------------------------------------------
Temps de création moyen d'une vehicules : {sum(iteration_end_time) / nb}
Plus longue itération : {max(iteration_end_time)}s
Plus courte itération : {min(iteration_end_time)}s
""")
    return chaine, list_imm


def generate_trajet(nb: int, dict_imm):
    start_time = time.perf_counter()
    iteration_end_time = []
    chaine: str = "INSERT INTO trajet (date, cout_trajet, status, duree_trajet,nb_km, vehicule) VALUES\n"
    conducteurs = []
    for i in range(nb):
        iteration_start_time = time.perf_counter()
        separator: str = ";" if i == nb - 1 else ","
        conducteur = random.choice(tuple(dict_imm.keys()))
        plaque = random.choice(tuple(dict_imm[conducteur]))
        chaine += f"\t('20{random.randint(24, 26)}-{random.randint(1, 12)}-{random.randint(1, 28)}', {random.randint(10, 120)}.{random.randint(0, 9)}0, {random.choice(('TRUE', 'FALSE'))}, '0{random.randint(0, 9)}:{random.randint(10, 59)}:00', {random.randint(100, 50000)/100}, '{plaque}'){separator}\n"
        iteration_end_time.append(time.perf_counter() - iteration_start_time)
        conducteurs.append(conducteur)
        print(f"{i}e trajet en {iteration_end_time[-1]} seconde")
    end_time = time.perf_counter()
    print(f"""\n{nb} trajet générée en {end_time - start_time}s
    -----------------------------------------------------------------
    Temps de création moyen d'une trajet : {sum(iteration_end_time) / nb}
    Plus longue itération : {max(iteration_end_time)}s
    Plus courte itération : {min(iteration_end_time)}s
    """)
    return chaine, conducteurs

def int_to_heure(n: int):
    return f"{(n // 60) % 24}:{n % 60}"

def generate_etapes(nb_pairs_sup: int, nb_trajet: int, nb_localisation: int, email_list, conducteurs):
    emails_in = {}
    chaine: str = "INSERT INTO etape (heure_prevu, status, id_trajet, id_localisation, est_depart_de, est_arrive_de) VALUES\n"
    for i in range(1, nb_trajet + 1):
        heure_depart = random.randint(0, 1439)
        heure_arriver = heure_depart + random.randint(30, 240)
        date =f"{random.randint(2024, 2026)}-{random.randint(1, 12)}-{random.randint(1, 28)}"
        chaine += f"\t('{int_to_heure(heure_depart)}:00', TRUE, {i}, {random.randint(1, nb_localisation)}, '{conducteurs[i - 1]}', NULL),\n"
        chaine += f"\t('{int_to_heure(heure_arriver)}:00', TRUE, {i}, {random.randint(1, nb_localisation)}, NULL, '{conducteurs[i - 1]}'),\n"
        emails_in.setdefault(i, set()).add(conducteurs[i - 1])
    for i in range(nb_pairs_sup):
        trajet = random.randint(1, nb_trajet)
        participant = random.choice(email_list)
        while participant in emails_in[trajet]:
            participant = random.choice(email_list)
        heure_depart = random.randint(0, 1439)
        heure_arriver = heure_depart + random.randint(30, 240)
        statut = random.choice(("TRUE", "FALSE"))
        separateur : str = ";" if i == nb_pairs_sup - 1 else ","
        chaine += f"\t('{int_to_heure(heure_depart)}:00', {statut}, {trajet}, {random.randint(1, nb_localisation)}, '{participant}', NULL),\n"
        chaine += f"\t('{int_to_heure(heure_arriver)}:00', {statut}, {trajet}, {random.randint(1, nb_localisation)}, NULL, '{participant}'){separateur}\n"
        emails_in.setdefault(i, set()).add(participant)
    return chaine

def generate_sposorise(nb, nb_sponsor, immatriculation):
    chaine = "INSERT INTO sponsorise (id_sponsor, immatriculation) VALUES\n"
    already_in = set()
    for i in range(nb):
        sep = ";" if i == nb - 1 else ","
        cpl = random.randint(1, nb_sponsor), random.choice(immatriculation)
        while cpl in already_in:
            cpl = random.randint(1, nb_sponsor), random.choice(immatriculation)
        chaine += f"\t({cpl[0]}, '{cpl[1]}'){sep}\n"
        already_in.add(cpl)
    return chaine

def generate_comment(nb, list_email, nb_localisation):
    chaine = "INSERT INTO commente (email, id_localisation, commentaire) VALUES\n"
    already_in = set()
    for i in range(nb):
        sep = ";" if i == nb - 1 else ","
        cpl = random.choice(list_email), random.randint(1, nb_localisation)
        while cpl in already_in:
            cpl = random.choice(list_email), random.randint(1, nb_localisation)
        syllabe = [f"{con}{voy}" for con in "bcdfghjklmnpqrstvwxz" for voy in "aeiouy"]
        giberish = ""
        for i in range(random.randint(10, 20)):
            for j in range(random.randint(2, 6)):
                giberish += random.choice(syllabe)
            giberish += " "
        chaine += f"\t('{cpl[0]}', {cpl[1]}, '{giberish}'){sep}\n"
        already_in.add(cpl)
    return chaine


def generate_note(nb_note: int, list_email: tuple):
    chaine = "INSERT INTO evalue (source, cible, note) VALUES\n"
    already_in = set()
    for i in range(nb_note):
        sep = ";" if (i == nb_note - 1) else ","
        cpl = random.choice(list_email), random.choice(list_email)
        while cpl in already_in or cpl[0] == cpl[1]:
            cpl = random.choice(list_email), random.choice(list_email)
        chaine += f"\t('{cpl[0]}', '{cpl[1]}', {random.randint(0, 5)}){sep}\n"
        already_in.add(cpl)
    return chaine

NB_COVOITUREUR = 500
NB_LOC = 1_500
NB_SPONSOR = 200
NB_VEHICULES = 1_000
NB_TRAJET = 7_650
NB_ETAPE = 3_000
NB_SPONSORISE = 600
NB_COMENTE = 1_500
NB_NOTE = 1_500

with open("auto_dump.sql", "w+", encoding="utf-8") as dump:
    dump.write("-- Dump générer automatiquement --\n")
    dump.write(HEADER)
    dump.write("\n-- insertion des covoitureurs --\n")
    txt, emails = generate_covoitureur(NB_COVOITUREUR)
    dump.write(txt)
    dump.write("\n-- insertion des localisations --\n")
    dump.write(generate_location(NB_LOC))
    dump.write("\n-- insertion des sponsor --\n")
    dump.write(generate_sponsor(NB_SPONSOR))

    dump.write("\n-- insertion des vehicules --\n")
    txt, dict_imm = generate_vehicules(NB_VEHICULES, tuple(emails))
    dump.write(txt)

    dump.write("\n-- insertion des trajets --\n")
    txt, conducteurs = generate_trajet(NB_TRAJET, dict_imm)
    dump.write(txt)

    dump.write("\n-- Insertion des etapes --\n")
    dump.write(generate_etapes(NB_ETAPE, NB_TRAJET, NB_LOC, tuple(emails), conducteurs))

    dump.write("\n-- Insertion Sponsorise -- \n")
    lst_imatriculation = set()
    for elt in dict_imm.values():
        lst_imatriculation = lst_imatriculation.union(elt)
    dump.write(generate_sposorise(NB_SPONSORISE, NB_SPONSOR, tuple(lst_imatriculation)))

    dump.write("\n-- Insertion des commentaire --\n")
    dump.write(generate_comment(NB_COMENTE, tuple(emails), NB_LOC))

    dump.write("\n-- Insertion  des notes --\n")
    dump.write(generate_note(NB_NOTE, tuple(emails)))

