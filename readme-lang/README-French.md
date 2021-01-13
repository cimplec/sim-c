
# sim-C

<p align="center">
  <img src="../logo.png" height="200">
</p>

[![GitHub](https://img.shields.io/github/license/cimplec/sim-c)](https://github.com/cimplec/sim-c/blob/master/LICENSE)  ![GitHub stars](https://img.shields.io/github/stars/cimplec/sim-c?style=plastic)  ![GitHub contributors](https://img.shields.io/github/contributors/cimplec/sim-c)  ![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)  ![GitHub last commit](https://img.shields.io/github/last-commit/cimplec/sim-c)

## Qu'est-ce que sim-C?

<p align="justify">Souvent, les gens ont du mal à programmer en C (en particulier les débutants) en raison de sa syntaxe de bas niveau et de l'indisponibilité de bibliothèques tierces stables. Nous présentons sim-C un frontal de haut niveau pour C qui crée une syntaxe typée dynamiquement pour C. L'utilisateur peut écrire du code dans cette syntaxe de haut niveau, puis le compiler en code C optimisé. sim-C ne traite pas le code et le traduit simplement en C, il n'y a donc aucune possibilité que le code s'exécute lentement. Ainsi, avec sim-C, les utilisateurs peuvent écrire du code plus rapidement en utilisant la syntaxe de haut niveau et en même temps être en mesure d'exploiter la puissance et la vitesse d'un programme C. Faisons à nouveau C cool.</p>

## Pipeline

<p align="center">
  <img src="../simc-pipeline.png">
</p>

## Commencer à contribuer

<p align="justify">sim-C qui a une base de code très intuitive, vous serez prêt à contribuer en un rien de temps! Lors de l'ajout de fonctionnalités à sim-C, vous devez uniquement apporter des modifications aux fichiers suivants:</p>

<p align="justify">1. <strong>lexical_analyzer.py</strong>
L'analyse lexicale est la première phase d'un compilateur. Il prend le code source modifié des préprocesseurs de langage qui sont écrits sous forme de phrases. L'analyseur lexical décompose ces syntaxes en une série de jetons, en supprimant tout espace ou commentaire dans le code source. Selon le type de fonctionnalité, ajoutez-le à la fonction respective: is_keyword, numeric_val, string_val, keyword_identifier et / ou lexical_analyze.</p>

<p align="justify">2. <strong>op_code.py</strong>
Il est responsable de la création des opcodes. Si besoin est, vous devez modifier uniquement la fonction opcode2dig qui renvoie la représentation entière du type opcode.</p>

<p align="justify">3. <strong>simc_parser.py</strong>
Parser est un composant interpréteur utilisé pour diviser les données en éléments plus petits provenant de la phase d'analyse lexicale. Un analyseur prend l'entrée sous la forme d'une séquence de jetons et produit une sortie. Ici, vous devrez peut-être créer une fonction distincte qui définit la grammaire et vérifie la syntaxe. La fonction doit renvoyer l'OpCode. De plus, si nécessaire, vous devez ajouter la fonctionnalité à la fonction d'analyse qui analyse les jetons, appelle la fonction particulière et renvoie les opcodes.</p>

<p align="justify">4. <strong>compiler.py</strong>
Enfin, vous devez définir le type d'opcode dans le compilateur et écrire la syntaxe C attendue pour la fonctionnalité.</p>

<p align="justify">Vous pouvez écrire un test dans test.simc et vérifier s'il produit des résultats dans le fichier test.c.</p>


## Commencer

Pour démarrer avec simC suivez la documentation officielle: - https://cimplec.github.io/docs/

Les ressources suivantes sont un bon endroit pour en savoir plus sur simC: -

1) Écrire du code en C? Simplifiez-vous la vie avec sim-C <a href="https://dev.to/cimplec/writing-code-in-c-simplify-your-life-with-sim-c-2dkj">Dev.to</a>, <a href="https://medium.com/oss-build/writing-code-in-c-simplify-your-life-with-sim-c-9dd98f882bf8">Medium</a>.
2) Premiers pas avec sim-C <a href="https://dev.to/cimplec/getting-started-with-sim-c-4iek">Dev.to</a>, <a href="https://medium.com/oss-build/getting-started-with-sim-c-1397ee539877">Medium</a>.

En dehors de ces articles de blog, vous pouvez également consulter le <a href="https://cimplec.github.io/docs">documents officiels</a>.

Avant d'aller plus loin, veuillez parcourir les règles dans [CONTRIBUTING.md](../CONTRIBUTING.md)

## Licence

sim-C est sous licence GNU General Public License (GPL) v3.0. [LICENCE](../LICENSE)

## L'équipe

- [Siddhartha Dhar Choudhury](https://github.com/frankhart2018)
- [Dhairya Jain](https://github.com/dhairyaj)
- [Mathias Fernandes Duarte Coelho](https://github.com/Math-O5)
