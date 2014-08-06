Title: Haute Disponibilité avec Redis
Date: 2014-04-15 20:00
Tags: GNU/Linux, Debian, sysadmin, Développement
Planet: true

[Redis](http://redis.io/) est une base de donnée de type clef-valeur. On la
range dans la grande famille plutôt hétérogène des bases **NoSQL** qui, pour
rappel, signifie plutôt *Not Only SQL* que *No SQL*. Ceci dit, dans le cas de
Redis, on est vraiment dans le *No SQL at all*. La base permet de stocker par
clef des chaînes, des listes de chaînes, des *hashtable*. Elle permet de
stocker des valeurs avec une date d'expiration au delà de laquelle la donnée
disparaît. Idéal pour gérer des données cache et c'est d'ailleurs
l'utilisation principale de Redis. On peut aussi facilement implémenter
producteur / consommateur entre plusieurs clients d'une base Redis. L'ensemble
des commandes supportées par Redis est parfaitement documenté
[ici](http://redis.io/commands).

La base est orientée performance et évolutivité : 

-    écrite en C, facilement portable car le code n'a pas de dépendance particulière, 
-    stockage des données en mémoire avec différents mécanismes optionnels pour conserver une copie sur disque,
-    réplication possible d'une base maître vers un grand nombre de bases esclaves. On peut écrire dans la base maître et seulement lire dans les bases esclaves.

Ce qui fait (aussi) le succès de Redis, c'est que le coeur est en C et qu'il
existe des [clients pour la plupart des langages](http://redis.io/clients).
Pour l'instant, j'ai utilisé Jedis pour JAVA et redis-py pour Python. Enfin,
un client en ligne de commande permet d'interagir avec la base sans écrire de
code.

La dernière version stable est Redis 2.8.8. Quant à la version 3.0 à venir,
encore en phase de bêta, elle embarque des fonctionnalités de répartition des
données dans des configuration de type cluster, ce qu'on appelle en langue de
Shakespeare le **sharding**. Dans le futur, elle embarquera aussi des
fonctionnalités de Haute Disponibilité pour basculer les données lorsqu'un
noeud du cluster s'écroule.

En attendant ce futur, la version actuelle apporte une solution de cluster
actif/passif basée sur la réplication maître / esclave surveillée par des
sentinelles chargées de promouvoir un Redis esclave en maître en cas de
défaillance.

Je me suis intéressé à monter une configuration avec seulement 2 machines sous
Debian qui peut fonctionner si l'une des machines tombe et automatiquement
réintégrer le cluster quand elle redevient opérationnelle, sans impact  pour
les clients Redis. Ce n'est pas si trivial et je me suis heurté à quelques
difficultés avant d'arriver à une configuration opérationnelle.

Comme dans la plupart des architectures clusterisées, un quorum (nombre
minimal de votants) est nécessaire pour élire un nouveau maître. La valeur
minimum possible est 1, signifiant qu'une sentinelle a besoin qu'au moins 1
autre sentinelle soit d'accord avec elle pour déclarer qu'un Redis maître est
défaillant. Il faut au minimum 2 sentinelles opérationnelles quel que soit
l'état du cluster donc sur chaque machine on va installer un Redis et 2
sentinelles.

Au début de mes expérimentations, j'attribuais un port différent aux
sentinelles pour les exécuter sans conflit sur la même machine mais j'avais
des problème d'indécision des sentinelles pour élire un nouveau noeud. Je
crois que toutes les sentinelles ne communiquaient pas. La situation s'est
arrangée quand j'ai configuré toutes mes sentinelles pour écouter sur le port
standard 26379. Pour que ce soit possible, j'ai attaché mes sentinelles à des
adresses IP différentes en déclarant une sous-interface sur chaque machine.

    +–––––––––––––––+––––––––––––––+     +–––––––––––––––+––––––––––––––+
    |  Sentinelle 1 |              |     |  Sentinelle 1 |              |
    +–––––––––––––––+              |     +–––––––––––––––+              |
    |    REDIS      | Sentinelle 2 |     |    REDIS      | Sentinelle 2 |
    +––––––––––––––––––––––––––––––+     +––––––––––––––––––––––––––––––+
    |     Eth0      |    Eth0:1    |     |     Eth0      |    Eth0:1    |
    | 192.168.0.51  |  10.25.14.1  |     | 192.168.0.52  |  10.25.14.2  |
    +–––––––––––––––+––––––––––––––+     +–––––––––––––––+––––––––––––––+
               Machine A                            Machine B


Voici la configuration réseau de la machine A (/etc/network/interfaces) : 

    iface eth0 inet static
        address 192.168.0.51
        netmask 255.255.255.0    
    
    iface eth0:1 inet static
        address 10.25.14.1
        netmask 255.255.255.0


La configuration des serveurs Redis est identique sur chaque machine : 

    port 6379
    
    loglevel warning
    logfile "/var/log/redis.log"
    
    maxmemory-policy noeviction
    
    appendonly yes
    appendfsync always
    
    auto-aof-rewrite-percentage 100
    auto-aof-rewrite-min-size 64mb
    aof-rewrite-incremental-fsync yes
    


Ce n'est pas le sujet de l'article mais je vous conseille de jeter un oeil à
la documentation pour les paramètres liés à l'AOF et au APPEND qui vont
réduire les risques de perte de données en configurant des écritures sur
disque. C'est peut-être inintéressant dans le cas d'une utilisation de Redis
comme cache mais ça le devient dans le cas d'une utilisation plus classique
comme base de données.

Quand les deux serveurs Redis sont démarrés, on peut initier le rôle initial
d'esclave de la machine B depuis le client Redis avec la commande :

    slaveof 192.168.0.51 6379

Par la suite, les sentinelles se chargent de décider quel rôle est joué en
fonction de la disponibilité des machines.

Voici la configuration de la sentinelle 1 sur la machine A : 

    port 26379    
    bind 192.168.0.51
    
    # master configuration
    sentinel monitor master 192.168.0.51 6379 1
    sentinel down-after-milliseconds master 3000
    sentinel failover-timeout master 10000
    sentinel parallel-syncs master 4


Et celle de la sentinelle 2, également sur la machine A : 

    port 26379
    bind 10.25.14.1
    
    # master configuration
    sentinel monitor master 192.168.0.51 6379 1
    sentinel down-after-milliseconds master 3000
    sentinel failover-timeout master 10000
    sentinel parallel-syncs master 4

La configuration des sentinelles de la machine B est identique à part les
directives **bind** pour attacher les services aux adresses 192.168.0.52 et
10.25.14.2.

Avec cette configuration, on a suffisamment de sentinelles pour basculer le
rôle d'une machine à l'autre dans cas extrème où la machine A est
injoignable par le réseau ou bien mise hors tension.

Je n'ai pas détaillé le code client mais il y a une étape avant de récupérer
une connexion valide à la base Redis : s'adresser au *pool* de sentinelles
pour obtenir l'adresse du maître et ensuite ouvrir une connexion vers celui-
ci. Dans le cas d'une bascule du cluster, la connexion est cassée et il faut à
nouveau s'adresser aux sentinelles pour récupérer l'adresse du Redis maître.

Voici un exemple typique de code en Python :

    #!/bin/env python
    
    from redis.sentinel import Sentinel
    sentinel = Sentinel(
        [('192.168.0.51', 26379), ('192.168.0.52', 6379)], socket_timeout=0.1)
    print("Master %s %d" % sentinel.discover_master('master'))


Je suis le projet Redis depuis un bout de temps avec intérêt car il offre beaucoup d'applications possibles dans des architectures distribuées multi-langages.