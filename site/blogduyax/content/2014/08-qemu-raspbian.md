Title: Emuler la Raspbian avec Qemu
Date: 2014-08-12 14:00
Tags: Debian, Matériel
Planet: true

<img src="images/2014/rasplogo.png" alt="Raspberry logo" style="margin: 0px
20px; float:left;" />Je m'intéresse de plus en plus au Raspberry et je
franchirai peut-être le pas de l'achat dans quelque temps. J'ai voulu voir à
quoi ressemble sa distribution principale Raspbian (basée sur Debian) en
l'émulant sous Qemu. Je me suis basé sur [le tutorial pointé par beaucoup de
gens dans les forums](http://xecdesign.com/qemu-emulating-raspberry-pi-the-
easy-way/)  et j'ai effectué des recherches annexes pour résoudre
certains problèmes : taille des partitions, gestion de la souris sous Qemu. Ce
qui suit est le résultat de mes manipulations pour émuler Raspbian avec Qemu
depuis une distribution GNU/Linux 64 bits.

En pré-requis, on suppose que Qemu est installé sur le système hôte. On
vérifie que le processeur ARM du Raspberry est supporté par Qemu avec la
commande suivante :

    $ qemu-system-arm -cpu ?

Le résultat liste les types de processeur supportés. On s'assure que **arm1176** est mentionné. 

### Installation de base

On se crée un répertoire de travail dans lequel on va télécharger les fichiers nécessaires : 

-    le noyau Linux [depuis ce lien](http://xecdesign.com/downloads/linux-qemu/kernel-qemu) 
-    l'image de la Raspbian [depuis le site officiel](http://www.raspberrypi.org/downloads)

La modification d'un fichier est nécessaire pour que la distribution
fonctionne avec Qemu. On effectue donc un premier démarrage particulier avec
BASH en processus INIT pour la réaliser.

    $ qemu-system-arm -kernel kernel-qemu -cpu arm1176 -m 256 -M versatilepb -no-reboot -serial stdio -append "root=/dev/sda2 panic=1 rootfstype=ext4 rw init=/bin/bash" -hda 2014-06-20-wheezy-raspbian.img

Quand Qemu a démarré BASH on modifie le fichier /etc/ld.so.preload

    $ nano /etc/ld.so.preload

On commente la première ligne du fichier :

    #/usr/lib/arm-linux-gnueabihf/libcofi_rpi.so

On sauvegarde (CTRL-X avec nano) et on arrête l'émulation 
    
    exit

A ce stade, l'émulation Raspbian sous Qemu est fonctionnelle et on peut faire un vrai démarrage avec la commande : 

    $ qemu-system-arm -kernel kernel-qemu -cpu arm1176 -m 256 -M versatilepb -no-reboot -serial stdio -append "root=/dev/sda2 panic=1 rootfstype=ext4 rw" -hda 2014-06-20-wheezy-raspbian.img

### Elargir la partition

Il ne reste pas beaucoup d'espace disque sur la partition root. On  peut
élargir la partition, sinon on ne pourra même pas mettre à jour Raspbian avec
apt-get. Cela nécessite plusieurs étapes.

D'abord on élargit le disque avec l'utilitaire qemu-resize.

    $ qemu-img resize 2014-06-20-wheezy-raspbian.img +2G

Ensuite on démarre la Raspbian avec Qemu 

    $ qemu-system-arm -kernel kernel-qemu -cpu arm1176 -m 256 -M versatilepb -no-reboot -serial stdio -append "root=/dev/sda2 panic=1 rootfstype=ext4 rw" -hda 2014-06-20-wheezy-raspbian.img

On se connecte au Raspberry avec l'utilisateur **pi** et le mot de passe
**raspberry**. Attention si on se connecte depuis la fenêtre Qemu, le clavier
est probablement configuré en QWERTY.

On lancer l'utilitaire **fdisk** pour modifier les partitions

    $ fdisk /dev/sda

-    supprimer la partition 2 qui commence à l'offset 122880 : commande **d** puis indiquer la partition **2**
-    recréer une partition 2 qui commence à l'offset 122880 et utilise la totalité du disque : commande **n**
-    sauvegarder les modifications : commande **w**
-    arrêter le système avec la commande **reboot**. 

On démarre à nouveau la Raspbian avec Qemu et on lance la commande resize2fs
pour élargir la partition 2 :

    $ resize2fs /dev/sda2
    $ reboot

### Augmenter la résolution sous X

Par défaut, on a une résolution en 640x480 quand on lance LXDE avec
**startx**. On peut monter en 800x600 en créant un fichier *xorg.conf*.

    # sudo nano /etc/X11/xorg.conf

Ajouter ces lignes dans le fichier : 

    Section "Screen"
    Identifier "Default Screen"
    SubSection "Display"
    Depth 16
    Modes "800x600" "640x480"
    EndSubSection
    EndSection

Sauvegarde et redémarrer X pour voir le résultat. 

### Déplacements erratiques de la souris

J'ai été confronté à ce problème lié à la configuration de Qemu. La souris se
fige ou certaines portions de l'écrans deviennent inaccessibles. je l'ai
résolu en lançant Qemu ainsi :

    qemu-system-arm -kernel kernel-qemu -cpu arm1176 -m 256 -M versatilepb -no-reboot -serial stdio -usbdevice tablet -display sdl -append "root=/dev/sda2 panic=1 rootfstype=ext4 rw" -hda 2014-06-20-wheezy-raspbian.img

Notez le paramètre *-usbdevice tablet* et *-display sdl*. 

### Conclusion

L'émulation Qemu permet de se faire une bonne idée de la distribution. Bien sûr, ce n'est pas complètement fonctionnel car certains périphériques spécifiques au Raspberry ne sont pas présent (je pense aux entrées / sortie, au port HDMI) mais cela permet déjà beaucoup. 

