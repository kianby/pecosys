Title: Installation de Shinken
Date: 2014-09-15 14:00
Tags: GNU/Linux,sysadmin
Planet: true

Dans la série "ma vie de sysadmin en semi-pro", je me suis frotté à la mise
en place d'une supervision de type Nagios. Mon besoin est la surveillance de
quelques serveurs et services critiques et la remontée d'alertes en cas de
souci. Nagios est la référence dans le domaine avec des centaines de greffons
pour surveiller la plupart des applications existantes et la possiblité de
créer ses propres greffons pour ses applications spécifiques. Par goût de la
démarcation (mais pas seulement), j'ai opté pour
[Shinken](https://fr.wikipedia.org/wiki/Shinken_%28logiciel%29), un
*fork* de Nagios qui a plusieurs avantages à mes yeux :

-   c'était une branche expérimentale de Nagios qui aurait dû succéder au Nagios actuel dont les critiques disent que le noyau n'évolue pas assez vite par rapport aux demandes des utilisateurs,
-   son architecture est saluée pour sa capacité de montée en charge (distribuée, balance de charge),
-   c'est écrit en Python et la compatibilité est totale avec les greffons Nagios.

La supervision en général et Nagios en particulier est un vaste sujet et des
IT administrant des milliers de serveurs et de services ont beaucoup plus de
légitimité que moi pour en parler. Je vais me borner à décrire les étapes
d'une installation sans problème sur un serveur Debian Wheezy.

### Installation de Shinken

Ce qui suit s'inspire directement du [10 minutes Shinken installation guide](https://shinken.readthedocs.org/en/latest/02_gettingstarted/installations/shinken-installation.html) avec quelques adaptations pour Debian Wheezy.

Installation des paquets Debian nécessaires :

    $ apt-get install python-cherrypy3 python-pip \
        python-pycurl nagios-plugins

Création d'un utilisateur **shinken** dédié :

    $ adduser shinken

Et finalement installation de shinken lui-même avec le programme PIP (je suppose que Python et PIP 2.x sont installés sur votre Debian) :

    $ pip install shinken

C'est aussi simple que cela. On a installé le moteur de Shinken mais aucune
interface graphique. Je découvre petit à petit mais l'interface est une
composante optionnelle et plusieurs sont proposées. J'ai choisi
d'installer **webui**, celle recommandée qui apporte de la visualisation (la
configuration se fait en modifiant des fichiers et en redémarrant les
services Shinken).

### Installation de Webui

Shinken propose son propre gestionnaire de greffons avec le programme **shinken**.

    $ shinken --init
    $ shinken install webui
    $ shinken install auth-cfg-password

Webui nécessite un stockage en base pour stocker les préférences
utilisateurs. On peut se limiter à SQLite, j'ai choisir MongoDB (la base
NoSQL) qui me sert à d'autres usages.

    $ apt-get install mongodb python-pymongo
    $ shinken install mod-mongodb

Editer */etc/shinken/modules/webui.cfg* et rajouter les modules dépendants :

    modules auth-cfg-password,mongodb

Editer */etc/shinken/brokers/broker-master.cfg* et rajouter le module webui :

    modules webui

Il reste à définir les contacts (personnes) du système dans
*/etc/shinken/contacts*. Par défaut, un administrateur est défini dans
*/etc/shinken/contacts/admin.cfg*, son mot de passe est utilisé pour
l'interface Webui.

Deux commandes servent régulièrement quand on modifie la configuration.

Vérifier que la configuration est syntaxiquement correcte :

    $ service shinken check

Redémarrer les services Shinken :

    $ service shinken restart

Si tout est correct, on peut se connecter sur Webui depuis un navigateur à l'adresse :

    http://<SERVER>:7767



### les objets supervisés

Nagios introduit la notion de *host* et de *service* pour désigner les
machines et les services s'exécutant sur ces machines. La configuration de
Shinken après installation est minimale :

-    les notifications par email sont activées et seront utilisées si [votre serveur peut envoyer des emails](http://blogduyax.madyanne.fr/smtp-relay-avec-qmail-sur-debian-wheezy.html)
-    la machine locale est elle-même supervisée de manière générique, je crois que le seul indicateur c'est le Ping pour vérifier qu'elle est accessible.

On va enrichir tout cela en installant un agent SNMP sur le serveur Shinken ce qui permet de surveiller, entre autre, l'utilisation CPU, RAM, occupation des disques.

On installe un agent SNMP sur la machine locale avec le paquet **snmpd** qui, par défaut, n'est accessible que par localhost :

     $ apt-get install snmpd

On rajoute le greffon linux-snmp dans Shinken :

    $ shinken install linux-snmp

On corrige deux soucis de l'installation sous Debian :

le script **check_icmp** doit avoir les droits setuid :

    $ chmod u+s /usr/lib/nagios/plugins/check_icmp

Le module PERL **utils.pm** est mal référencé par les greffons Nagios ; on le
fait pointer sur celui de notre installation de PERL dans */usr/share/perl5*

    /usr/share/perl5$ ln -s /usr/lib/nagios/plugins/utils.pm

On peut modifier la configuration du *host* **localhost** en éditant le fichier */etc/shinken/hosts/localhost.cfg* :

    define host{
        use                 linux-snmp
        contact_groups      admins
        host_name           localhost
        address             127.0.0.1
    }

On vérifie la configuration et on redémarre Shinken :

    $ service shinken check
    $ service shinken restart

Si la configuration est correcte, la machine locale avec ses services CPU,
Mémoire apparaît désormais dans Webui. La fréquence du *polling*, les
notifications, tout est configurable finement par *host* , par groupe de
*host*, par service. La documentation est riche et bien détaillée.

Dans le cas de GNU/Linux, la supervision par SNMP apporte les indicateurs de
base d'un serveur. Pour avoir plus, on peut donner l'accès SSH au superviseur
Shinken sur les serveurs ou on peut installer NRPE (Nagios Remote Plugin
Executer). Je préfère NRPE car on ne demande pas l'accès total au serveur à
superviser. L'installation de [NRPE est bien décrite dans cet
article](http://xmodulo.com/2014/03/nagios-remote-plugin-executor-nrpe-
linux.html). Pour finir, beaucoup de resources Nagios sont disponibles sur
le site [Nagios Exchange](http://exchange.nagios.org).







