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
    mdp char(60) NOT NULL,   
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
    email  Varchar(100) references covoitureur(email)  ON DELETE CASCADE ON UPDATE CASCADE,
    CHECK (vehicule IS NOT NULL )
);

CREATE TABLE etape( 
    id_etape serial primary key,
    heure_prevu time NOT NULL,
    heure_reel time ,
    status boolean default FALSE,
    date date NOT NULL,
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
    note int NOT NULL ,
    primary key(source,cible),
    CHECK (source <> cible),
    CHECK (note> 0 and note <6)
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




INSERT INTO covoitureur (email, nom, prenom, addresse, date_naissance, mdp, numero_permis, argent, parrain)
VALUES
('alice@gmail.com', 'Dupont', 'Alice', '1 rue de Paris, 75001 Paris', '1990-05-15', '$2b$12$xmIQUk3SMqWaLuSFC6JqV.NaD962Z3EzXMFuY.x2SRBSvwdnTtNsC', 'B12345', 1500.50, NULL), -- Mdp: jenesuispasbob12
('bob@gmail.com', 'Martin', 'Bob', '2 rue de Lyon, 69001 Lyon', '1985-10-20', '$2b$12$PyVvd3af43pSgWnkmYUscuMhN88m.CwmhJm1w6rbbTfQ.7JSKLi1S', 'B98765', 1200.00, 'alice@gmail.com'), -- Mdp: jesuisb0b
('carol@gmail.com', 'Lemoine', 'Carol', '3 avenue de Nice, 06000 Nice', '1992-02-10', '$2b$12$sYiJ/YjJkDql/RkWH4bN0eerT4OhHm6Antbv8APSbKqep3XCEs0de', 'B12312', 2000.00, 'alice@gmail.com'), -- Mdp: K_rolle12 
('david@gmail.com', 'Petit', 'David', '4 boulevard de Bordeaux, 33000 Bordeaux', '1988-07-30', '$2b$12$m/B6D7M0Ugzh9MiD3enp8eK9dVEytEAJfDQLEbT.OS1g1Tw1/NgcC', 'B98798', 1800.00, 'bob@gmail.com'), -- Mdp: davidBowI
('emily@gmail.com', 'Dupuis', 'Emily', '5 rue de Marseille, 13001 Marseille', '1993-08-22', '$2b$12$aFf0Ee6BRXRVunKrk32T0uSUtc7lpdpHXncyCoCzsKBpZzYKxD7Ry', 'B55555', 2200.00, 'carol@gmail.com'), -- Mdp: Em1lyKebek
('frank@gmail.com', 'Durand', 'Frank', '6 avenue de Toulouse, 31000 Toulouse', '1995-11-11', '$2b$12$l/dJ3H5c1uVN2cZjt.mMou57bILgW9Yi/UxFJ7FhlePbX8y3S5Wzy', 'B66666', 1600.00, 'david@gmail.com'), -- Mdp: abc123
('george@gmail.com', 'Dubois', 'George', '7 rue de Lille, 59000 Lille', '1982-01-13', '$2b$12$IEs2/QtTUv7bmGfgv10MtOWKYAkwl6umyaBGcuL9zyiDxbmPkryzq', 'B77777', 1400.00, 'alice@gmail.com'), -- Mdp: ge0rge3
('hannah@gmail.com', 'Fournier', 'Hannah', '8 place de Strasbourg, 67000 Strasbourg', '1990-09-30', '$2b$12$w2mgDhSn5fOTz0GztXiqJuwWQkAXKI1kGNe530RUdjdDHh8ouFWxC', 'B88888', 2300.00, 'bob@gmail.com'), -- Mdp: laS0eurdElza
('isabelle@gmail.com', 'Bernard', 'Isabelle', '9 rue de Nantes, 44000 Nantes', '1996-04-16', '$2b$12$vi1BLYPxM2HzhlgStc8EPeh7x9mK6eAWDbkUQifmxP5ES2nMi1Y5q', 'B99999', 2100.00, 'carol@gmail.com'), -- Mdp: rAinedEspagne1492
('james@gmail.com', 'Leclerc', 'James', '10 boulevard de Rennes, 35000 Rennes', '1989-06-05', '$2b$12$1hnePDxBtHoX0FzX59CuEuCgQotW5DTag4IqzXFxrWxrqTYpduHyu', 'B11111', 2500.00, 'david@gmail.com'); -- Mdp: bondJ@mesb0nd

INSERT INTO localisation (nom, addresse, description, ville) VALUES
('Centre commercial', 'Place de la République', 'Centre commercial avec de nombreux magasins', 'Paris'),
('Gare de Lyon', 'Place Louis-Armand', 'Gare ferroviaire à Paris', 'Paris'),
('Aéroport de Nice', 'Aéroport de Nice-Côte dAzur', 'Aéroport international de Nice', 'Nice'),
('Hotel de Ville', '1 place de l Hôtel de Ville', 'Mairie de Lyon', 'Lyon'),
('Musée d Orsay', '1 rue de la Légion dHonneur', 'Musée des beaux-arts', 'Paris'),
('Louvre', 'Rue de Rivoli', 'Le plus grand musée du monde', 'Paris'),
('Basilique du Sacré-Cœur', '35 rue du Chevalier de la Barre', 'Église emblématique de Montmartre', 'Paris'),
('Château de Versailles', 'Place d"Armes', 'Palais royal français', 'Versailles'),
('Place de la Concorde', 'Place de la Concorde', 'une des places les plus célèbres de Paris', 'Paris'),
('Jardin des Tuileries', '117 Rue de Rivoli', 'Jardin public entre le Louvre et la place de la Concorde', 'Paris'),
('Tour Eiffel', '5 Avenue Anatole France', 'Monument emblématique de Paris', 'Paris'),
('Promenade des Anglais', 'Promenade des Anglais', 'Avenue côtière célèbre de Nice', 'Nice'),
('Cathédrale Notre-Dame', '6 Parvis Notre-Dame - Pl. Jean-Paul II', 'Cathédrale gothique iconique', 'Paris'),
('La Croisette', 'Boulevard de la Croisette', 'Promenade en bord de mer à Cannes', 'Cannes'),
('Place Masséna', 'Place Masséna', 'Place centrale et historique de Nice', 'Nice'),
('Opéra Garnier', '8 Rue Scribe', 'Théâtre historique de l’opéra de Paris', 'Paris'),
('Mont-Saint-Michel', 'Route du Mont-Saint-Michel', 'Îlot rocheux avec abbaye célèbre', 'Pontorson'),
('Pointe du Raz', 'Plogoff', 'Cap emblématique de la Bretagne', 'Bretagne'),
('La Défense', 'Parvis de la Défense', 'Quartier d’affaires avec architecture moderne', 'Courbevoie'),
('Zoo de Vincennes', 'Avenue Daumesnil', 'Grand parc zoologique', 'Paris');

INSERT INTO sponsor (nom, nature_pub, duree_trajet, remuneration) VALUES
('Orange', 'Publicité pour la fibre optique', '1 hour', 200.00),
('Renault', 'Publicité pour des voitures écologiques', '30 minutes', 150.00),
('Coca-Cola', 'Publicité pour des boissons rafraîchissantes', '45 minutes', 100.00),
('Adidas', 'Publicité pour des vêtements de sport', '15 minutes', 180.00),
('Nike', 'Publicité pour des chaussures de sport', '20 minutes', 160.00),
('Samsung', 'Publicité pour des téléphones', '35 minutes', 250.00),
('Sony', 'Publicité pour des produits électroniques', '50 minutes', 210.00),
('Toyota', 'Publicité pour des voitures hybrides', '25 minutes', 220.00),
('Peugeot', 'Publicité pour des voitures', '40 minutes', 190.00),
('McDonald', 'Publicité pour des menus', '30 minutes', 150.00);


INSERT INTO vehicules (immatriculation, modele, nombre_places, couleur, type_carburant, crit_Air, proprietaire) VALUES
('AB123CD', 'Peugeot 208', 5, 'Bleu', 'Essence', '1', 'alice@gmail.com'),
('EF456GH', 'Renault Clio', 4, 'Rouge', 'Diesel', '2', 'bob@gmail.com'),
('IJ789KL', 'Citroën C3', 5, 'Blanc', 'Essence', '3', 'carol@gmail.com'),
('MN012OP', 'Tesla Model 3', 5, 'Noir', 'Électrique', 'E', 'david@gmail.com'),
('PQ345RS', 'Ford Fiesta', 5, 'Vert', 'Diesel', '3', 'emily@gmail.com'),
('ST678UV', 'Volkswagen Golf', 4, 'Gris', 'Essence', '2', 'frank@gmail.com'),
('WX901YZ', 'Audi A3', 5, 'Bleu', 'Essence', '1', 'george@gmail.com'),
('YZ234AB', 'BMW Série 1', 4, 'Blanc', 'Diesel', '4', 'hannah@gmail.com'),
('GH567IJ', 'Honda Civic', 5, 'Rouge', 'Essence', '1', 'isabelle@gmail.com'),
('LM890NO', 'Nissan Leaf', 5, 'Noir', 'Électrique', 'E', 'james@gmail.com');

INSERT INTO trajet (date, cout_trajet, status, duree_trajet,nb_km, vehicule, email) VALUES
('2024-11-10', 15.50, FALSE, '01:30:00',12.2, 'AB123CD', 'alice@gmail.com'),
('2024-11-11', 10.00, TRUE, '00:45:00',15.71, 'EF456GH', 'bob@gmail.com'),
('2024-11-12', 12.00, FALSE, '01:15:00',120, 'IJ789KL', 'carol@gmail.com'),
('2024-11-13', 20.00, TRUE, '02:00:00',200.700, 'MN012OP', 'david@gmail.com'),
('2024-11-14', 18.50, FALSE, '01:20:00',172, 'PQ345RS', 'emily@gmail.com'),
('2024-11-15', 14.30, TRUE, '00:55:00',50.7, 'ST678UV', 'frank@gmail.com'),
('2024-11-16', 16.40, FALSE, '01:45:00',12.5, 'WX901YZ', 'george@gmail.com'),
('2024-11-17', 13.70, TRUE, '01:10:00',156.1, 'YZ234AB', 'hannah@gmail.com'),
('2024-11-18', 17.80, FALSE, '02:30:00',54.8, 'GH567IJ', 'isabelle@gmail.com'),
('2024-11-19', 22.00, TRUE, '01:40:00',34.8, 'LM890NO', 'james@gmail.com'),
('2024-11-20', 11.25, FALSE, '00:35:00',12.0, 'AB123CD', 'alice@gmail.com'),
('2024-11-21', 19.90, TRUE, '01:50:00',156.1, 'EF456GH', 'bob@gmail.com'),
('2024-11-22', 23.00, FALSE, '02:15:00',34.6, 'IJ789KL', 'carol@gmail.com'),
('2024-11-23', 14.75, TRUE, '00:40:00',78.56, 'MN012OP', 'david@gmail.com'),
('2024-11-24', 16.50, FALSE, '01:05:00',12.5, 'PQ345RS', 'emily@gmail.com'),
('2024-11-25', 21.00, TRUE, '01:25:00',13.8, 'ST678UV', 'frank@gmail.com'),
('2024-11-26', 18.35, FALSE, '01:55:00',45.1, 'WX901YZ', 'george@gmail.com'),
('2024-11-27', 20.10, TRUE, '02:10:00',700.5, 'YZ234AB', 'hannah@gmail.com'),
('2024-11-28', 12.45, FALSE, '00:50:00',12.8, 'GH567IJ', 'isabelle@gmail.com'),
('2024-11-29', 24.00, TRUE, '02:00:00',20.2, 'LM890NO', 'james@gmail.com');



INSERT INTO etape (heure_prevu, heure_reel, status, date, id_trajet, id_localisation, est_depart_de, est_arrive_de) VALUES
('08:00:00', '08:10:00', TRUE, '2024-11-10', 1, 9, 'alice@gmail.com', NULL),
('09:00:00', '09:05:00', TRUE, '2024-11-11', 2, 9, NULL, 'carol@gmail.com'),
('10:00:00', '10:20:00', FALSE, '2024-11-12', 10, 9, 'carol@gmail.com', NULL),
('07:30:00', '07:45:00', TRUE, '2024-11-13', 11, 10, 'david@gmail.com', NULL),
('11:30:00', '11:45:00', TRUE, '2024-11-14', 4, 16, NULL, 'bob@gmail.com'),
('13:00:00', '13:05:00', TRUE, '2024-11-15', 20, 14, 'frank@gmail.com', NULL),
('14:30:00', '14:40:00', FALSE, '2024-11-16', 7, 8, NULL, 'david@gmail.com'),
('15:00:00', '15:10:00', TRUE, '2024-11-17', 8, 20, 'hannah@gmail.com', NULL),
('16:30:00', '16:35:00', TRUE, '2024-11-18', 10, 3, 'isabelle@gmail.com', NULL),
('17:00:00', '17:20:00', FALSE, '2024-11-19', 14, 4, NULL, 'carol@gmail.com'),
('07:45:00', '08:00:00', TRUE, '2024-11-20', 18, 6, 'alice@gmail.com', NULL),
('08:15:00', '08:25:00', TRUE, '2024-11-21', 20, 13, NULL, 'frank@gmail.com'),
('09:30:00', '09:50:00', FALSE, '2024-11-22', 15, 18, 'bob@gmail.com', NULL),
('10:00:00', '10:30:00', TRUE, '2024-11-23', 2, 13, NULL, 'isabelle@gmail.com'),
('11:00:00', '11:10:00', FALSE, '2024-11-24', 13, 15, 'hannah@gmail.com', NULL),
('12:45:00', '13:00:00', TRUE, '2024-11-25', 16, 9, NULL, 'alice@gmail.com'),
('14:15:00', '14:20:00', TRUE, '2024-11-26', 19, 10, 'david@gmail.com', NULL),
('15:30:00', '15:45:00', TRUE, '2024-11-27', 2, 15, NULL, 'bob@gmail.com'),
('16:45:00', '16:50:00', FALSE, '2024-11-28', 1, 14, 'carol@gmail.com', NULL),
('17:30:00', '17:55:00', TRUE, '2024-11-29', 4, 10, NULL, 'david@gmail.com');


INSERT INTO sponsorise (id_sponsor, immatriculation) VALUES
(1, 'AB123CD'),
(2, 'EF456GH'),
(3, 'IJ789KL'),
(4, 'MN012OP'),
(5, 'PQ345RS'),
(6, 'ST678UV'),
(7, 'WX901YZ'),
(8, 'YZ234AB'),
(9, 'GH567IJ'),
(10, 'LM890NO');

INSERT INTO commente (email, id_localisation, commentaire) VALUES
('alice@gmail.com', 1, 'Très bien situé, pratique pour faire du shopping.'),
('bob@gmail.com', 2, 'Gare très pratique mais un peu bruyante.'),
('carol@gmail.com', 3, 'Bel aéroport, mais trop de monde le week-end.'),
('david@gmail.com', 4, 'L Hôtel de Ville est très bien pour des événements en plein air.'),
('emily@gmail.com', 5, 'Musée très intéressant et bien conçu.'),
('frank@gmail.com', 6, 'Louvre est un incontournable, mais trop de monde.'),
('george@gmail.com', 7, 'Belle vue sur Paris depuis le Sacré-Cœur.'),
('hannah@gmail.com', 8, 'Château magnifique et très bien entretenu.'),
('isabelle@gmail.com', 9, 'Très belle place, idéale pour des promenades.'),
('james@gmail.com', 10, 'Le jardin est parfait pour une pause détente.');

INSERT INTO evalue (source, cible, note) VALUES
('alice@gmail.com', 'bob@gmail.com', 4),
('bob@gmail.com', 'carol@gmail.com', 5),
('carol@gmail.com', 'david@gmail.com', 3),
('david@gmail.com', 'alice@gmail.com', 4),
('emily@gmail.com', 'frank@gmail.com', 5),
('frank@gmail.com', 'george@gmail.com', 4),
('george@gmail.com', 'hannah@gmail.com', 4),
('hannah@gmail.com', 'isabelle@gmail.com', 5),
('isabelle@gmail.com', 'james@gmail.com', 3),
('james@gmail.com', 'alice@gmail.com', 4);

INSERT INTO etape (heure_prevu, heure_reel, status, date, id_trajet, id_localisation, est_depart_de, est_arrive_de) VALUES
('08:00:00', NULL, FALSE, '2024-11-10', 4511, 9, 'Germain.Lana@proton.me', NULL),
('08:20:00', NULL, FALSE, '2024-11-10', 4511, 9, NULL, 'Germain.Lana@proton.me');