

# sim-C

<p align="center">
  <img src="../logo.png" height="200">
</p>

[![GitHub](https://img.shields.io/github/license/cimplec/sim-c)](https://github.com/cimplec/sim-c/blob/master/LICENSE)  ![GitHub stars](https://img.shields.io/github/stars/cimplec/sim-c?style=plastic)  ![GitHub contributors](https://img.shields.io/github/contributors/cimplec/sim-c)  ![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)  ![GitHub last commit](https://img.shields.io/github/last-commit/cimplec/sim-c)

##   Cos'è simC?

<p align="justify">Spesso le persone hanno problemi a programmare in C (specialmente i principianti) a causa della sua sintassi di basso livello e dell'indisponibilità di librerie di terze parti stabili. Presentiamo sim-C un front-end di alto livello per C che crea una sintassi tipizzata dinamicamente per C. L'utente può scrivere codice in questa sintassi di alto livello e quindi compilarlo in codice C ottimizzato. sim-C non elabora il codice e lo traduce semplicemente in C, quindi non c'è possibilità che il codice funzioni lentamente. Quindi, con sim-C gli utenti possono scrivere codice più velocemente utilizzando la sintassi di alto livello e allo stesso tempo essere in grado di sfruttare la potenza e la velocità di un programma C. Facciamo raffreddare di nuovo C.</p>

## Tubatura

<p align="center">
  <img src="../simc-pipeline.png">
</p>

##   Inizia a contribuire
<p align="justify">sim-C che ha una base di codice molto intuitiva, sarai pronto a contribuire in pochissimo tempo!
Durante l'aggiunta di qualsiasi funzionalità a sim-C è necessario apportare modifiche solo ai seguenti file:</p>

<p align="justify">1. <strong>lexical_analyzer.py</strong>
L'analisi lessicale è la prima fase di un compilatore. Prende il codice sorgente modificato dai preprocessori del linguaggio scritti sotto forma di frasi. L'analizzatore lessicale suddivide queste sintassi in una serie di token, rimuovendo eventuali spazi o commenti nel codice sorgente. A seconda del tipo di funzionalità aggiungilo alla rispettiva funzione: is_keyword, numeric_val, string_val, keyword_identifier e / o lexical_analyze.</p>

<p align="justify">2. <strong>op_code.py</strong>
È responsabile della creazione di codici operativi. Se necessario, è necessario modificare solo la funzione opcode2dig che restituisce la rappresentazione intera del tipo di codice operativo.</p>

<p align="justify">3. <strong>simc_parser.py</strong>
Parser è un componente interprete che viene utilizzato per suddividere i dati in elementi più piccoli provenienti dalla fase di analisi lessicale.Un parser prende l'input sotto forma di sequenza di token e produce output. Qui potrebbe essere necessario creare una funzione separata che definisce la grammatica e controlla la sintassi. La funzione dovrebbe restituire l'OpCode. Inoltre, se necessario, devi aggiungere la funzionalità alla funzione di analisi che analizza i token, chiama la particolare funzione e restituisce gli opcode.</p>

<p align="justify">4. <strong>compiler.py</strong>
Infine è necessario definire il tipo di codice operativo nel compilatore e scrivere la sintassi C prevista per la funzionalità.</p>

<p align="justify">Puoi scrivere un test in test.simc e verificare se sta producendo risultati nel file test.c.</p>


## Iniziare

Per iniziare con simC segui la documentazione ufficiale:-
https://cimplec.github.io/docs/

Le seguenti risorse sono un buon posto per conoscere meglio simC: -

1) Scrivi codice in C? Semplifica la tua vita con sim-C <a href="https://dev.to/cimplec/writing-code-in-c-simplify-your-life-with-sim-c-2dkj">Dev.to</a>, <a href="https://medium.com/oss-build/writing-code-in-c-simplify-your-life-with-sim-c-9dd98f882bf8">Medium</a>.
2) Iniziare con sim-C <a href="https://dev.to/cimplec/getting-started-with-sim-c-4iek">Dev.to</a>, <a href="https://medium.com/oss-build/getting-started-with-sim-c-1397ee539877">Medium</a>.

Oltre a questi post del blog, puoi anche consultare i <a href="https://cimplec.github.io/docs"> documenti ufficiali </a>.

Prima di procedere oltre, leggi le regole in [CONTRIBUTING.md](../CONTRIBUTING.md)

## Licenza

sim-C è concesso in licenza con GNU General Public License (GPL) v3.0. [LICENSE](../LICENSE)

##   Il gruppo

- [Siddhartha Dhar Choudhury](https://github.com/frankhart2018)
- [Dhairya Jain](https://github.com/dhairyaj)
- [Mathias Fernandes Duarte Coelho](https://github.com/Math-O5)
