Title: Installation de Horde Groupware 
Date: 2014-01-02 19:00
Tags: Hébergement, Mobilité, GNU/Linux, Debian
Planet: true

Je remets en place progressivement les outils nécessaires sur mon serveur
Debian. Je me suis posé à nouveau la problématique de la synchronisation des
contacts et du calendrier entre mes appareils, c'est à dire mon ordinateur
portable sous ArchLinux avec le logiciel de courrier *Thunderbird* et son
module de gestion de calendrier *Lightning*, mon antique téléphone BlackBerry
Bold 9780. Un accès Web à mon calendrier et mes contacts depuis n'importe
quelle machine quand je suis en déplacement serait un plus. 

Le téléphone supporte la synchronisation Google de facto et SyncML en
installant le client [Funambol](http://www.funambol.com). Je n'ai trouvé aucune
possibilité gratuite pour faire de la synchronisation CardDAV, CalDAV ou
ActiveSync. SyncML reste ma meilleure option. On peut installer le client
Funambol du BlackBerry Store mais il fait plus que nécessaire car il
s'interface avec le serveur Funambol ou bien on peut installer une version plus
ancienne qui suffit pour la synchro des contacts, du calendrier et des tâches
depuis [ce lien](http://www.memotoo.com/how-to-sync-your-blackberry-phone.php).
Côté ordinateur, Lightning supporte nativement le protocole CalDav et le carnet
d'adresse peut être synchronisé avec CardDAV en installant le [module
complémentaire pour Sogo](http://www.sogo.nu/english/downloads/frontends.html).

<img src="images/2014/logo-horde.jpg" style="float:left; margin: 0px 20px;"/>A
l'époque de mon Motorola Droid, j'avais déjà utilisé le client Funambol pour
synchroniser mes données avec
[eGroupware](http://www.egroupware.org/community_edition) et je m'étais
intéressé à *Horde*. Ce dernier semblait plus difficile à installer,
l'interface Web était peu conviviale et j'avais mis en place eGroupware que
j'avais utilisé 1 an avec satisfaction. J'ai su qu'une version 5 de Horde était
sortie dans l'année et j'ai décidé de l'évaluer. Horde supporte SyncML,
CardDAV, CalDav et son interface graphique a été rajeunie.

Ma cible de déploiement est mon serveur privé virtuel avec
l'environnement technique suivant : 

- Distribution Debian Wheezy
- Serveur Web NginX

L'installation est plus complexe que la moyenne mais avec un bon tuto on s'en
sort. Horde est modulaire : un Framework et des applications. Moi j'ai besoin
de Kronolith (la gestion du calendrier) et de Turba (la gestion des contacts).
J'ai décliné l'installation par le système de paquets car généralement cela
tire le serveur Apache alors que j'utilise NginX et j'ai opté pour PEAR,
l'outil d'installation PHP que ne connaissais pas. De ma compréhension, c'est
l'équivalent de CPAN pour PERL ou d'APT pour Debian. Horde publie ses
composants pour l'infrastructure PEAR [sur ce serveur](http://pear.horde.org).

L'installation de PEAR sur Debian est galette.

    apt-get install php-pear

Puis, on enregistre le canal Horde sur Pear et on installe les composants
nécessaires :

    mkdir -p /var/www/horde
    cd /var/www/horde
    pear channel-discover pear.horde.org
    pear install horde/horde_role
    pear run-scripts horde/horde_role
    pear install -a -B horde/horde
    pear install horde/turba
    pear install horde/kronolith
    pear install horde/mnemo
    pear install horde/Horde_SyncMl

Dans le cas de NginX sur Debian, il faut ajuster les permissions du répertoire.

    chown -R www-data:www-data /var/www/horde

Et il faut créer les fichiers de configuration de chaque application à partir
des modèles fournis :

    cd /var/www/horde/config
    for f in *.dist; do cp $f `basename $f .dist`; done
    cd /var/www/horde/kronolith/config
    for f in *.dist; do cp $f `basename $f .dist`; done
    cd /var/www/horde/turba/config
    for f in *.dist; do cp $f `basename $f .dist`; done
    cd /var/www/horde/nag/config
    for f in *.dist; do cp $f `basename $f .dist`; done
    cd /var/www/horde/mnemo/config
    for f in *.dist; do cp $f `basename $f .dist`; done

Il reste à configurer NginX. Je force l'utilisation de HTTPS en redirigeant les
requêtes HTTP vers la version sécurisée du site.

    server {
      listen 80;
      server_name groupware.exemple.fr;
      rewrite ^ https://$server_name$request_uri? permanent;
    }

    server {
      listen 443 ssl;
      server_name groupware.exemple.fr;
      root /var/www/horde;
      index index.php;

      ssl_certificate  /etc/ssl/exemple.fr.cert;
      ssl_certificate_key  /etc/ssl/exemple.fr.key;

      access_log /var/log/nginx/horde-access.log;
      error_log /var/log/nginx/horde-error.log;

      location / {
        try_files $uri $uri/ /rampage.php?$args;
      }

      location ~ \.php {
        fastcgi_split_path_info ^(.+\.php)(/.+)$;
        fastcgi_param PATH_INFO $fastcgi_path_info;
        fastcgi_param PATH_TRANSLATED $document_root$fastcgi_path_info;
        fastcgi_param PHP_VALUE "cgi.fix_pathinfo=1";
        fastcgi_pass unix:/var/run/php5-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
      }

    }

Horde propose le choix entre plusieurs bases de données J'utilise déjà MySQL,
j'ai donc créé une nouvelle base pour Horde en utilisant les outils
en ligne de commande de MySQL.

    mysql -u root -p 
    mysql> CREATE DATABASE horde;
    mysql> GRANT ALL ON horde.* TO horde@localhost IDENTIFIED BY 'horde';
    mysql> FLUSH PRIVILEGES;
    mysql> EXIT;

A la première connexion Web, il n'y a pas d'authentification, on est connecté
en tant qu'administrateur sans mot de passe. 

#### 1ère étape : définir la base de donnée.

1. Aller dans le menu Administration / Configuration

    <img src="images/2014/horde-config.png"/>

2. Cliquer sur le composant Horde (horde)

    <img src="images/2014/horde-application.png"/>

3. Configurer la base de donnée dans l'onglet Database

    <img src="images/2014/horde-database.png"/>

#### 2ème étape : créer un utilisateur avec les droits d'administration. 

1. Aller dans le menu Administration / Utilisateur

    <img src="images/2014/horde-user.png"/>

2. Créer un nouvel utilisateur 

    <img src="images/2014/horde-adduser.png"/>

3. Retourner dans le menu Administration / Configuration et rajouter
   l'utilisateur nouvellement créé dans les admins de l'onglet
   Authentification.

    <img src="images/2014/horde-setadmin.png"/>

4. Il est conseillé de tester le nouvel utilisateur en se déconnectant et en se
   reconnectant. Si cela fonctionne, on peut enlever l'utilisateur
   Administrator de la liste des admins.

#### 3ème étape : finaliser l'installation des applications

Dans le menu Administration / Configuration, tous les composants installés
apparaîssent. Les boutons *mettre à jour toutes les configurations* et *mettre
à jour les schémas de la base* doivent être cliqués pour finaliser l'installation.

#### Conclusion

L'URL CalDAV pour s'inscrire au calendrier se trouve dans les propriétés du
calendrier de l'application Agenda, dans l'onglet *inscription*. De manière
similaire, l'URL CardDAV se trouve dans les propriétés du carnet d'adresses.
Quant à l'URL SyncML, c'est un point d'entrée unique pour la synchronisation de
toutes les applications ; dans notre exemple ce serait
http://groupware.exemple.fr/rpc.php.

J'ai mis en place Horde depuis 1 semaine avec une synchronisation SyncML par
Funambol sur mon téléphone et une synchronisation CardDAV et CalDAV depuis
Thunderbird. J'ai lu que SyncML n'était pas très bon pour gérer les conflits de
synchronisation mais je n'ai pas rencontré de souci. L'évaluation se passe très
bien pour l'instant.
