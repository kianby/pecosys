Title: Pecosys, les commentaires avec Pelican
Date: 2014-08-07 19:00
Tags: GNU/Linux, Hébergement, Web
Planet: true

Pecosys est le projet évoqué dans mon dernier billet pour gérer des
commentaires avec un blog statique créé avec
[Pelican](http://docs.getpelican.com/en/3.4.0). J'ai publié [l'ensemble des
sources sur mon GitHub](https://github.com/kianby/pecosys) sous licence GPL.
Avant d'expliquer à quoi ça sert, une présentation des types de moteurs de
blog s'impose.

#### Petite intro sur les blog statiques

Les moteurs de blog classiques comme Wordpress ou Dotclear stockent leurs
données (articles, commentaires) dans une base de données et ils utilisent une
logique côté serveur pour produire les pages HTML. Au fil des ans, ces moteurs
ont rajouté beaucoup de fonctionnalités (par l'utilisation de plugins) et on
les appelle désormais des CMS (Content Management System) car ils peuvent
servir à bâtir tout type de site Web, en facilitant le travail de publication
et de collaboration aux rédacteurs qui n'ont plus besoin d'être des gens
techniques.

PluXml est un moteur un peu à part, plus léger que les CMS cités ci-dessus,
qui n'utilise pas de base de données mais stocke les données dans des fichiers
XML. C'est un pas dans la direction des blogs statiques dans la mesure où cela
permet de mettre son blog dans un gestionnaire de sources (comme GIT) et
conserver une traçabilité des changements. Cela facilite aussi la migration du
blog.

Pelican et Jekyll sont des vrais blogs statiques. Ils n'utilisent pas de
langage serveur comme PHP ou Ruby, il ne stockent pas leurs données dans une
base de données. Les articles sont écrits dans un langage Markup comme
[Markdown](http://daringfireball.net/projects/markdown) et la construction du
site (le build) est réalisé hors ligne. Il génère les pages à base de HTML,
CSS et éventuellement un zeste de JavaScript. Ces pages sont transférées vers
le serveur HTTP hébergeant le site... et hop le site est à jour.

Alors pourquoi s'embêter à gérer un site statique alors qu'un Wordpress
s'installe en 5 minutes ? 

Cela dépend de tout un chacun mais j'y suis venu pour les raisons suivantes :

-    Les articles sont écrits dans un format simpliste (pour ma part c'est Markdown), la présentation est clairement séparée du contenu. C'est lors du build qu'on génère le code HTML en fonction de *templates* et de CSS personnalisés par nos soins. Le code HTML généré par Pelican est propre et léger. Le jour où j'ai migré de WordPress à PluXml, j'ai été horrifié par le code HTML de WordPress.  
-    Le contenu du blog est un ensemble de fichier au format texte, idéal à gérer avec un gestionnaire de sources afin de garder trace des modifications. Un gestionnaire de sources devient aussi un moyen d'automatiser la mise à jour du site. On écrit et on teste sur sa machine de dev, on publie sous GIT et il suffit que le serveur rafraîchisse sa version du site quand une modification a été effectuée.

#### La problématique des commentaires

Pas de logique serveur, juste un ensemble de pages HTML avec un peu
d'interactivité grâce à JavaScript. Comment gérer les commentaires avec un
site statique ? La solution proposée par Pelican c'est l'utilisation des
services de la société Disqus. Un peu de JavaScript embarqué au bon endroit et
vos pages sont agrémentées d'un formulaire pour poster des commentaires qui
envoie les données chez Disqus et l'affichage de la page dans le navigateur
client par l'usage de JavaScript, envoie des requêtes à Disqus pour rapatrier
les commentaires approuvées et les ajouter à la page HTML qui vient de votre
serveur.

Est-ce que vous sentez venir l'objection ? 

D'abord on met en place une belle mécanique,très pure, où l'on contrôle le
contenu, l'affichage, puis on confie la partie sensible (les données
utilisateur) à une société commerciale, qui ne demande rien en retour et qui
propose sûrement un service aux petits oignons pour approuver les
commentaires... mais qui garde les données. Comment une société comme Disqus
monétise ses services ? Je ne sais pas, peu importe. Que se passe-t-il si la
société dépose le bilan ? Là j'ai la réponse. L'ensemble des commentaires est
perdu : une bonne partie de la richesse d'un blog, ce qui fait son histoire.
Dommage non ?

#### L'approche Pecosys

Pecosys est un serveur de commentaires écrit en Python que vous hébergez sur le même serveur que votre blog. Il reçoit les commentaires à approuver depuis le blog par le biais d'un formulaire sur le blog. Pour cela, les *templates* de Pelican ont été adaptés afin de rajouter ce formulaire en bas de chaque article. 

Le lien entre le blog statique et le serveur Pecosys est réalisé par grâce au serveur Web. Dans le cas de NginX, il est trivial d'associer une URL à un programme Python. Dans le cas d'Apache, c'est faisable facilement en utilisant le module Proxy. Bref, le serveur Pecosys est d'abord un serveur HTTP sur lequel on poste les commentaires entrés par un formulaire classique de création de commentaires.  

Quand un commentaire est reçu, le serveur va faire deux trucs : sauvegarder le commentaire et le soumettre à l'administrateur du blog. 

La sauvegarde se fait grâce à GIT. Ah j'avais pas encore parlé de GIT :-) On suppose qu'on est dans une architecture centralisée où le blog est modifié depuis une machine de développeur et poussé (au sens GIT: PUSH) vers un *bare repository*. Dans mon cas, cette référence centrale des sources est sous BitBucket car ils acceptent la création de dépôts privés gratuitement et que je ne veux pas publier les adresses emails de tous ceux qui ont laissé un commentaire sur le blog. Souvenez-vous les commentaires font désormais partie des sources du blog, on verra comment plus loin. 

Donc, pour résumer :

-     j'écris mes articles sur ma machine de dev perso, je publie dans GIT et je pousse mes modifications au GIT centralisé de BitBucket (au sens GIT: ORIGIN).
-     mon serveur vérifie périodiquement si le dépôt BitBucket a été modifié et si c'est le cas, il rapatrie les sources du blog et reconstruit le site grâce à sa mécanique Pelican installée localement. 
-     Pecosys a sa propre version du blog (au sens GIT: CLONE) maintenue à jour de BitBucket. 

Donc quand Pecosys reçoit un nouveau commentaire, il met à jour sa version du
blog (la branche MASTER) et il crée une nouvelle branche XYZ pour ce
commentaire. il sauve ce commentaire dans les sources du blog (au format
Markdown) et il committe la branche XYZ.

Ensuite, le serveur va le communiquer à l'administrateur du blog par email.
Cela suppose qu'un email dédié est utilisé par Pecosys (pourquoi pas
blog@mydomain.com) et qu'il connaît l'email de l'administrateur du blog (vous
!). Cet email contient le commentaire et demande une réponse.

L'administrateur du blog (toujours vous) doit répondre à cet email. Une
réponse sans commentaire revient à approuver le commentaire et va lancer sa
publication. Une réponse avec un commentaire "NO" (désolé pour l'originalité)
signifie qu'on refuse le commentaire.

En fonction de cette réponse, le serveur Pecosys qui vérifie sa boite de
réception régulièrement, va traiter le commentaire :

-    un refus du commentaire revient à supprimer la branche GIT XYZ
-    une approbation du commentaire ramène les modifications de la branche XYZ sur la branche MASTER (au sens GIT: MERGE) et pousse les modifications sur le GIT distant (dans mon cas BitBucket)

Dans les deux cas, un email de confirmation de l'action réalisée est envoyé à
l'administrateur du blog.

A ce stade, la branche de référence BitBucket est à jour donc le serveur va
ramener ses modifications, reconstruire le site et par là même
publier le commentaire.

Si vous avez bien suivi et je sais que c'est un peu touffu et compliqué, vous
vous demandez comment les commentaires (ces fichiers en Markdown) sont générés
en HTML. Et bien, pas le biais d'un plugin Pelican nommé **CaCause**, en
hommage au projet de base initié il y a un an avec [Bruno
Adele](http://www.jesuislibre.org) et [Nahir
Mohamed](https://github.com/nadley) dont Pecosys est une reprise des idées
principales mais avec une réalisation différente par son dialogue basé sur
l'email et son utilisation *forcenée* de GIT.

Je teste Pecosys depuis deux semaines sur ce site et je suis prêt à donner un
coup de main à quiconque veut se lancer. Sur GitHub, j'ai publié les sources
du serveur mais aussi une version allégée de ce site (sans les commentaires)
qui contient donc mes *templates* avec le formulaire et les sources du plugin. 

En attendant je retourne à mon farniente estival :-)

<img src="images/2014/lemon.jpg"/>

 


