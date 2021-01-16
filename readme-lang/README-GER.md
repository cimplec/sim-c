# sim-C

<p align="center">
  <img src="../logo.png" height="200">
</p>

[![GitHub](https://img.shields.io/github/license/cimplec/sim-c)](https://github.com/cimplec/sim-c/blob/master/LICENSE)  ![GitHub stars](https://img.shields.io/github/stars/cimplec/sim-c?style=plastic)  ![GitHub contributors](https://img.shields.io/github/contributors/cimplec/sim-c)  ![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)  ![GitHub last commit](https://img.shields.io/github/last-commit/cimplec/sim-c)

## Was ist sim-C?

<p align="justify">Häufig haben Menschen (insbesondere Anfänger) Probleme beim Programmieren in C aufgrund der Syntax auf niedriger Ebene und der Nichtverfügbarkeit von stabilen Bibliotheken von Drittanbietern. Wir stellen sim-C ein High-Level-Frontend für C vor, das eine dynamisch typisierte Syntax für C erzeugt. Der Benutzer kann Code in dieser High-Level-Syntax schreiben und ihn dann zu optimiertem C-Code kompilieren. sim-C verarbeitet den Code nicht und übersetzt ihn einfach in C, so dass es keine Möglichkeit gibt, dass der Code langsam läuft. Mit sim-C können Benutzer also unter Verwendung der High-Level-Syntax schneller Code schreiben und gleichzeitig die Leistung und Geschwindigkeit eines C-Programms nutzen. Lassen Sie uns C wieder kühl machen.</p>

## Die Pipeline

<p align="center">
  <img src="../simc-pipeline.png">
</p>

## Mit dem Beitragen beginnen

<p align="justify">sim-C, das über eine sehr intuitive Codebasis verfügt, werden Sie im Handumdrehen bereit sein, einen Beitrag zu leisten!
Beim Hinzufügen jeglicher Funktionalität zu sim-C müssen Sie nur in den folgenden Dateien Änderungen vornehmen:</p>

<p align="justify">1. <strong>lexical_analyzer.py</strong>
Die lexikalische Analyse ist die erste Phase eines Compilers. Sie übernimmt den modifizierten Quellcode von Sprachpräprozessoren, die in Form von Sätzen geschrieben werden. Der lexikalische Analysator zerlegt diese Syntaxen in eine Reihe von Token, indem er alle Leerzeichen oder Kommentare im Quellcode entfernt. Je nach Art der Funktionalität fügen Sie diese der jeweiligen Funktion hinzu: is_Schlüsselwort, numeric_val, string_val, keyword_identifier und/oder lexical_analyze.</p>

<p align="justify">2. <strong>op_code.py</strong>
Sie ist für die Erstellung von Opcodes zuständig. Gegebenenfalls müssen Sie nur die Funktion opcode2dig ändern, die die ganzzahlige Darstellung des Opcode-Typs zurückgibt.</p>

<p align="justify">3. <strong>simc_parser.py</strong>
Der Parser ist eine Interpreterkomponente, die verwendet wird, um die Daten in kleinere Elemente zu zerlegen, die aus der lexikalischen Analysephase stammen. Ein Parser nimmt Eingaben in Form einer Folge von Token entgegen und erzeugt Ausgaben. Hier kann es erforderlich sein, eine separate Funktion zu erstellen, die die Grammatik definiert und auf die Syntax prüft. Die Funktion sollte den OpCode zurückgeben. Gegebenenfalls müssen Sie auch die Funktionalität an die Parser-Funktion anhängen, die die Token parst, die jeweilige Funktion aufruft und den OpCode zurückgibt.</p>

<p align="justify">4. <strong>compiler.py</strong>
Schließlich müssen Sie den Opcode-Typ im Compiler definieren und die erwartete C-Syntax für die Funktionalität schreiben.</p>

<p align="justify">Sie können einen Test in test.simc schreiben und in der Datei test.c überprüfen, ob er Ergebnisse liefert.</p>


## Beginnen Sie

Um mit simC zu beginnen, folgen Sie der offiziellen Dokumentation:- https://cimplec.github.io/docs/

Die folgenden Ressourcen sind ein guter Ort, um mehr über simC zu erfahren:-

1) Schreiben von Code in C? Vereinfachen Sie Ihr Leben mit sim-C <a href="https://dev.to/cimplec/writing-code-in-c-simplify-your-life-with-sim-c-2dkj">Dev.to</a>, <a href="https://medium.com/oss-build/writing-code-in-c-simplify-your-life-with-sim-c-9dd98f882bf8">Medium</a>.
2) Erste Schritte mit sim-C <a href="https://dev.to/cimplec/getting-started-with-sim-c-4iek">Dev.to</a>, <a href="https://medium.com/oss-build/getting-started-with-sim-c-1397ee539877">Medium</a>.

Abgesehen von diesen Blog-Einträgen können Sie auch die <a href="https://cimplec.github.io/docs">offizielle Dokumente</a>.

Bevor Sie weitergehen, gehen Sie bitte die Regeln in [CONTRIBUTING.md](../CONTRIBUTING.md)

## Lizenz

sim-C ist unter der GNU General Public License (GPL) v3.0 lizenziert. [LIZENZ](../LICENSE)

## Das Team

- [Siddhartha Dhar Choudhury](https://github.com/frankhart2018)
- [Dhairya Jain](https://github.com/dhairyaj)
- [Mathias Fernandes Duarte Coelho](https://github.com/Math-O5)
