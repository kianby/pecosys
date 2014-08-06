Title: Supervisor, gestion de processus
Date: 2014-05-25 13:00
Tags: GNU/Linux, sysadmin
Planet: true

Quand il s'agit de déployer des programmes de son cru sur un serveur 
GNU/Linux, on réalise généralement deux actions :

-    l'écriture d'un script de démarrage et arrêt du programme
-    la *démon-isation* du programme

Le premier point n'est pas complexe mais il peut être contraignant. Si  on
envisage de déployer sur Debian, Ubuntu et Fedora, il faut prévoir trois
scripts différents : un pour les scripts à la saucce Sys V, un pour  Upstart
et un autre pour systemd. L'avantage c'est qu'on  peut gérer finement les
dépendances à d'autres services.

Le second point consiste à veiller à ne pas bloquer le script d'init en
lançant le programme. On peut le gérer dans le code de notre programme  en
prévoyant deux modes de lancement de notre programme : *daemon* et
interactif. Python, par exemple, propose [la librairie
daemonize](https://pypi.python.org/pypi/daemonize) pour réaliser cela. JAVA
propose des outils comme JAVA Service Wrapper pour gérer le lancement et
garantir l'arrêt du processus. On peut aussi le gérer de manière externe  au
code, de manière rustique avec un
[nohup](https://en.wikipedia.org/wiki/Nohup), auquel cas il faut gérer
l'arrêt fiable du processus en manipulant son PID.

Voici un exemple de script d'init à la sauce Debian pour un programme 
JAVA :

     #!/bin/sh
     ### BEGIN INIT INFO
     # Provides:          monprog
     # Required-Start:    $local_fs $remote_fs $network $syslog
     # Required-Stop:     $local_fs $remote_fs $network $syslog
     # Default-Start:     2 3 4 5
     # Default-Stop:      0 1 6
     # X-Interactive:     true
     # Short-Description: Start/stop monprog
     ### END INIT INFO
    
     BOOT_LOG=/var/log/monprog-boot.log
     PID_FILE=/opt/monprog/pid
    
     start_java () {
         nohup java -cp "/opt/monprog/lib/*" fr.yax.monprog.Main >$BOOT_LOG 2>&1 &
         echo $! > $PID_FILE
         echo "Monprog started ..."
     }
    
     do_start () {
         echo "Starting Monprog ..."
         if [ ! -f $PID_FILE ]; then
             start_java
         else
             PID=$(cat $PID_FILE)
             if [ -d /proc/$PID ]; then
                 echo "Monprog is already running ..."
             else
                 start_java
             fi
         fi
     }
    
     do_stop() {
         echo "Stopping Monprog ..."
         if [ -f $PID_FILE ]; then
             PID =$(cat $PID_FILE);
             kill $PID 2>/dev/null
             echo "Monprog stopped ..."
             rm -f $PID_FILE
         else
             echo "Monprog seems not running ..."
         fi
     }
    
     case $1 in
             start)
                 do_start
             ;;
             stop)
                 do_stop
             ;;
             restart)
                 do_stop
                 sleep 1
                 do_start
             ;;
     esac

C'est perfectible. Il faudrait tenter l'arrêt avec un signal moins violent
que SIGKILL de façon à l'intercepter dans le code et faire un arrêt  propre.
Si cette méthode ne fonctionne pas au bout de plusieurs secondes, le script d'init pourrait alors opter pour un arrêt radical.

Cette méthode fonctionne bien mais elle nécessite une connaissance  système
pour écrire et maintenir les scripts en fonction des déploiements cible.  Si
on veut donner la possibilité à un utilisateur standard (non *root*) de
démarrer ou arrêter un programme, il faut aussi maîtriser un peu la gestion
des  droits UNIX (avec sudo par exemple).

Une alternative simple pour la plupart des systèmes UNIX (GNU/Linux,  FreeBSD,
Solaris et Mac OS X) est le [programme  Supervisor](http://supervisord.org).
C'est écrit en Python (comme la plupart des  programmes de qualité !  **Troll
inside** ) et de même que MongoDB permet au développeur de reprendre la main
au DBA sur  l'administration de base de donnée, Supervisor permet au
développeur de reprendre un peu  la main à l'admin sys sur le déploiement de
ses applications.

Supervisor est fourni sur la plupart des distributions. On peut l'installer
avec le système de paquet de sa distribution ou bien opter pour une
installation à partir de PIP, l'installeur de programmes Python. Ce dernier
permet d'obtenir la version la plus récente de Supervisor.

Supervisor est composé de deux parties :

-   un service **Supervisord** 
-   un client en mode console : **Supervisorctl** 

Le client permet d'interagir avec les programmes gérés : démarrer, stopper.
Une interface RPC permet aussi de piloter Supervisord programmatiquement ; je
n'ai pas encore testé cet aspect.

La configuration principale est dans un fichier supervisord.conf qui décrit la
connexion du client supervisorctl (section unix_http_server), la config RPC
(section rpcinterface) et le répertoire des configuration des programmes à
gérer (section includes).

Voici une configuration type : 

#### /etc/supervisor/supervisord.conf

     [unix_http_server]
     file=/var/run//supervisor.sock   ; (the path to the socket file)
     chmod=0770                       ; sockef file mode (default 0700)
     chown=root:supervisor
    
     [supervisord]
     logfile=/var/log/supervisor/supervisord.log
     pidfile=/var/run/supervisord.pid
     childlogdir=/var/log/supervisor
    
     [rpcinterface:supervisor]
     supervisor.rpcinterface_factory = supervisorrpcinterface:make_main_rpcinterface
    
     [supervisorctl]
     serverurl=unix:///var/run//supervisor.sock
    
     [include]
     files = /etc/supervisor/conf.d/*.conf


Les droits sur la socket UNIX sont important. En donnant l'accès à ROOT et au
groupe supervisor, on peut facilement donner l'accès à supervisorctl en
ajoutant un utilisateur dans le groupe supervisor. Attention donner l'accès à
supervisorctl c'est donner le droit de stopper n'importe quel programme géré
par supervisor. C'est un privilège important.

Le reste de la configuration consiste à créer des configurations
additionnelles décrivant des programmes à lancer simplement :

-   par défaut un programme démarre en même temps que le service donc au
démarrage du serveur. C'est configurable.   
-   on peut définir si un programme doit être relancé automatiquement et définir sous quelle condition, par exemple en fonction du code de sortie du programme.   
-   on peut opter pour l'envoi d'un signal au programme afin de demander au programme de s'arrêter proprement plutôt que de forcer un arrêt brutal.   
-   on peut regrouper des programmes pour manipuler des
groupes, faire des démarrages groupés et des arrêts groupés. C'est utile si on a beaucoup de programmes.   
-   au sein d'un groupe on peut définir des
priorités pour ordonner le lancement des programmes du groupe.

Voici un exemple qui définit un groupe mesprogrammes composé de 2 programmes correspondant au même binaire.  
 
#### /etc/supervisor/conf.d/mesprogrammes.conf

     [group:mesprogrammes]
     programs=monprog1,monprog2
    
     [program:monprog1]
     directory=/opt/monprogram
     command=/usr/bin/java -DrunDir=/opt/monprog -cp "lib/*" fr.yax.monprog.Main --port 1234
     stopsignal=INT
     priority=500
    
     [program:monprog2]
     directory=/opt/monprogram
     command=/usr/bin/java -DrunDir=/opt/monprog -cp "lib/*" fr.yax.monprog.Main --port 1235
     stopsignal=INT
     priority=501


Dans cet exemple, on envoie un signal SIGINT à monprog pour lui demander un arrêt propre. Voici un snippet de code JAVA pour intercepter le signal :

#### Interception d'un signal SIGINT en JAVA

     // register a shutdown hook
     Runtime.getRuntime().addShutdownHook(new Thread() {
         @Override
         public void run() {
             logger.info("Shutting down has been requested");
             stopCleanly();
         }
     });

En conclusion, **Supervisor** est un bon outil de gestion de programmes :
fiable, facile à installer et à configurer. En complément d'un outil de
déploiement comme [Fabric](http://www.fabfile.org) un développeur peut
facilement automatiser le  déploiement de son programme sur une ou plusieurs
machines cibles.
