Title: SMTP Relay avec qmail sur Debian Wheezy
Date: 2014-01-22 21:00
Tags: GNU/Linux, Debian, sysadmin
Planet: false

J'ai cherché une alternative plus simple qu'Exim et Postfix pour que mes
serveurs Debian puissent envoyer des emails d'alerte. C'est une fonctionnalité
utile si on installe fail2ban ou logwatch. Je n'ai pas besoin de gérer des
utilisateurs ou de recevoir des emails, juste d'en envoyer en utilisant le
serveur SMTP du FAI comme relais. J'ai trouvé
[**qmail**](http://en.wikipedia.org/wiki/Qmail) en faisant quelques recherches,
un antique MTA dont la dernière version stable 1.0.3 date de 1998 (gasp !) mais
qui est toujours disponible dans les dépôts Debian.

Avant de lancer l'installation, il faut s'assurer que le hostname du serveur
est un FQDN, c'est à dire un nom DNS complet. Si ce n'est pas le cas, qmail
refuse de s'installer.  Si le serveur n'a pas de nom DNS, on peut mettre
n'importe quel domaine, ça ne gêne dans la configuration que nous allons mettre
en place. On peut modifier le hostname de manière persistente en deux étapes :

1. éditer le fichier /etc/hostname
2. forcer sa mise à jour avec la commande /etc/init.d/hostname.sh

L'installation de qmail désinstalle Postfix ou Exim4 car un seul MTA peut
s'approprier le port 25.

    apt-get install qmail qmail-run

Il s'agit d'un service local, on ne veut surtout pas ouvrir le port 25 sur
Internet. On peut forcer qmail à n'écouter que sur l'interface loopback en
modifiant le script de démarrage. Ce n'est pas l'idéal mais vu la fréquence de
mise à jour de qmail, on ne craint pas trop de voir cette modification écrasée.
Il faut remplacer *0* par *127.0.0.1* dans le fichier
**/etc/qmail/qmail-smtpd/run**. 

Voici la version modifiée :

    #!/bin/sh

    QMAILDUID=`id -u qmaild`
    NOFILESGID=`id -g qmaild`
    MAXSMTPD=`cat /var/lib/qmail/control/concurrencyincoming`
    LOCAL=`head -1 /var/lib/qmail/control/me`

    if [ -z "$QMAILDUID" -o -z "$NOFILESGID" -o -z "$MAXSMTPD" -o -z "$LOCAL" ]; then
        echo QMAILDUID, NOFILESGID, MAXSMTPD, or LOCAL is unset in
        echo /var/qmail/supervise/qmail-smtpd/run
        exit 1
    fi

    if [ ! -f /var/lib/qmail/control/rcpthosts ]; then
        echo "No /var/lib/qmail/control/rcpthosts!"
        echo "Refusing to start SMTP listener because it'll create an open relay"
        exit 1
    fi

    exec softlimit -m 7000000 \
        tcpserver -v -R -l "$LOCAL" -x /etc/qmail/tcp.smtp.cdb -c "$MAXSMTPD" \
            -u "$QMAILDUID" -g "$NOFILESGID" 127.0.0.1 smtp qmail-smtpd 2>&1

On modifie la configuration pour envoyer des emails en utilisant le serveur
SMTP Orange en tant que root@orange.fr si on est l'utilisateur root. On
remplace le contenu du fichier **/etc/qmail/defaulthost** avec ceci :

    orange.fr

On supprime le contenu du fichier **/etc/qmail/defaultdomain** et on configure
le relais dans le fichier **/etc/qmail/smtproutes** :

    smtp.orange.fr <utilisateur> <mot de passe>

Pour tester on relance qmail :

    # qmailctl stop 
    # qmailctl start

Et on tente l'envoi d'un email avec la commande mail :

    # mail -s "Hello" someone@somewhere.fr
    Ceci est un test
    ^D

Le fichier de log **/var/log/qmail/current** permet de vérifier l'état de l'envoi.
