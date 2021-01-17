
# sim-C

<p align="center">
  <img src="../logo.png" height="200">
</p>

[![GitHub](https://img.shields.io/github/license/cimplec/sim-c)](https://github.com/cimplec/sim-c/blob/master/LICENSE)  ![GitHub stars](https://img.shields.io/github/stars/cimplec/sim-c?style=plastic)  ![GitHub contributors](https://img.shields.io/github/contributors/cimplec/sim-c)  ![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)  ![GitHub last commit](https://img.shields.io/github/last-commit/cimplec/sim-c)

## O que é sim-C?

<p align="justify">Muitas vezes as pessoas têm problemas para programar em C (especialmente iniciantes) devido à sua sintaxe de baixo nível e indisponibilidade de bibliotecas externas. Nós apresentamos sim-C, um *front end* de alto nível para C que cria uma sintaxe *dynamically typed* para C. O utlizador pode escrever código nesta sintaxe de alto nível e depois compliar para código C otimizado. sim-C não processa o código e o simplesmente traduz para C portanto, não é possível que o código seja lento. Por isso, com sim-C os utilizadores podem escrever código rapidamente usando a sintaxe de alto nível e ao mesmo tempo ser capazes de aproveitar a potência e velocidade de um programa de C. Deixa-nos fazer C fixe outra vez.</p>

## Pipeline

<p align="center">
  <img src="../simc-pipeline.png">
</p>

## Começa a Contribuir

<p align="justify">sim-C tem uma base de código muito intuitiva, estarás pronto a contribuir num instante!
Enquanto adicionas funcionalidades ao sim-C precisas de fazer alterações apenas nos seguintes ficheiros:</p>

<p align="justify">1. <strong>lexical_analyzer.py</strong>
Análise lexical é a primeira fase do compilador. Pega no código fonte modificado dos processadores de linguagem que estão escritos na forma de frases. O analisador lexical separa estas sintaxes em séries de *tokens*, removendo espaços ou comentários no código fonte. Dependendo do tipo de funcionalidade adiciona-a à respetiva função: is_keyword, numeric_val, string_val, keyword_identifier e/ou lexical_analyze.</p>

<p align="justify">2. <strong>op_code.py</strong>
É responsável por criar *opcodes*. Se necessário, precisas de alterar apenas a função opcode2dig, que retorna a representação inteira do topo de *opcode*</p>

<p align="justify">3. <strong>simc_parser.py</strong>
O analisador é uma componente do interpretador que é usado para separar informação em elementos mais pequenos vindos da fase da análise lexical. Um analisador recebe *input* na forma de uma sequência de *tokens* e produz um resultado. Aqui pode ser preciso criar uma função separada que defina a gramática e que verifique a sintaxe. A função deve retornar o *opcode*. Além disto, se necessário, deves anexar a funcionalidade à função parse que analisa os *tokens*, chama a função pretendida e returna os *opcodes*.</p>

<p align="justify">4. <strong>compiler.py</strong>
Finalmente, tens de definir o tipo de *opcode* no compilador e escrever a sintaxe experada em C para a funcionalidade.</p>

<p align="justify">Você pode escrever testes em test.simc e verificar se está a produzir resultados no ficheiro test.c </p>


## Começar

Para começar com simC segue a documentação oficial:- https://cimplec.github.io/docs/

Os seguintes recursos são um bom sítio para conhecer melhor simC:-

1) Escreves código em C? Simplifica a tua vida com sim-C <a href="https://dev.to/cimplec/writing-code-in-c-simplify-your-life-with-sim-c-2dkj">Dev.to</a>, <a href="https://medium.com/oss-build/writing-code-in-c-simplify-your-life-with-sim-c-9dd98f882bf8">Medium</a>.
2) Começar com sim-C <a href="https://dev.to/cimplec/getting-started-with-sim-c-4iek">Dev.to</a>, <a href="https://medium.com/oss-build/getting-started-with-sim-c-1397ee539877">Medium</a>.

Além destas publicações em blogs, podes verificar os <a href="https://cimplec.github.io/docs">documentos oficiais</a>.

Antes de continuares, por favor lê as regras em [CONTRIBUTING.md](../CONTRIBUTING.md)

## Licença

sim-C tem uma lincença GNU General Public License (GPL) v3.0. [LICENSE](../LICENSE)

## A Equipa

- [Siddhartha Dhar Choudhury](https://github.com/frankhart2018)
- [Dhairya Jain](https://github.com/dhairyaj)
- [Mathias Fernandes Duarte Coelho](https://github.com/Math-O5)
