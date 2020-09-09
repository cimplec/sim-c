
# sim-C

<p align = "center">
  <img src = "../logo.png" height = "200">
</p>

[! [GitHub] (https://img.shields.io/github/license/cimplec/sim-c)] (https://github.com/cimplec/sim-c/blob/master/LICENSE)! [ Звезды GitHub] (https://img.shields.io/github/stars/cimplec/sim-c?style=plastic)! [Участники GitHub] (https://img.shields.io/github/contributors/cimplec/ sim-c)! [PRs приветствуются] (https://img.shields.io/badge/PRs-welcome-brightgreen.svg)! [последняя фиксация GitHub] (https://img.shields.io/github/last -commit / cimplec / sim-c)

## Что такое sim-C?

<p align = "justify"> Часто люди (особенно новички) испытывают проблемы с программированием на C из-за его синтаксиса низкого уровня и недоступности стабильных сторонних библиотек. Мы представляем sim-C как высокоуровневый интерфейс для C, который создает динамически типизированный синтаксис для C. Пользователь может писать код в этом синтаксисе высокого уровня, а затем компилировать его в оптимизированный код C. sim-C не обрабатывает код, а просто переводит его на C, поэтому нет возможности, что код будет работать медленно. Таким образом, с помощью sim-C пользователи могут писать код быстрее, используя синтаксис высокого уровня, и в то же время иметь возможность использовать мощность и скорость программы C. Давайте снова заставим C остыть. </p>

## Трубопровод

<p align = "center">
  <img src = "../simc-pipeline.png">
</p>

## Начать участие

<p align = "justify"> sim-C с интуитивно понятной кодовой базой, вы будете готовы внести свой вклад в кратчайшие сроки!
При добавлении каких-либо функций в sim-C вам необходимо внести изменения только в следующие файлы: </p>

<p align = "justify"> 1. <strong> lexical_analyzer.py </strong>
Лексический анализ - это первая фаза компилятора. Он берет модифицированный исходный код из языковых препроцессоров, которые записываются в форме предложений. Лексический анализатор разбивает эти синтаксисы на серию токенов, удаляя любые пробелы или комментарии в исходном коде. В зависимости от типа функциональности добавьте его к соответствующей функции: is_keyword, numeric_val, string_val, keyword_identifier и / или lexical_analyze. </p>

<p align = "justify"> 2. <strong> op_code.py </strong>
Он отвечает за создание кодов операций. При необходимости вам нужно изменить только функцию opcode2dig, которая возвращает целочисленное представление типа кода операции. </p>

<p align = "justify"> 3. <strong> simc_parser.py </strong>
Синтаксический анализатор - это компонент интерпретатора, который используется для разбиения данных на более мелкие элементы, поступающие на этапе лексического анализа. Парсер принимает входные данные в виде последовательности токенов и производит выходные данные. Здесь вам может потребоваться создать отдельную функцию, которая определяет грамматику и проверяет синтаксис. Функция должна вернуть OpCode. Кроме того, при необходимости вы должны добавить функциональность к функции синтаксического анализа, которая анализирует токены, вызывает конкретную функцию и возвращает коды операций. </p>

<p align = "justify"> 4. <strong> compiler.py </strong>
Наконец, вам нужно определить тип кода операции в компиляторе и написать ожидаемый синтаксис C для функциональности. </p>

<p align = "justify"> Вы можете написать тест в test.simc и проверить, дает ли он результаты в файле test.c. </p>


## Начать

Чтобы начать работу с simC, следуйте официальной документации: - https://cimplec.github.io/docs/

Следующие ресурсы - хорошее место, чтобы узнать больше о simC: -

1) Написание кода на C? Упростите свою жизнь с помощью sim-C <a href="https://dev.to/cimplec/writing-code-in-c-simplify-your-life-with-sim-c-2dkj"> Dev.to </ a>, <a href="https://medium.com/oss-build/writing-code-in-c-simplify-your-life-with-sim-c-9dd98f882bf8"> Средний </a>.
2) Начало работы с sim-C <a href="https://dev.to/cimplec/getting-started-with-sim-c-4iek"> Dev.to </a>, <a href = "https : //medium.com/oss-build/getting-started-with-sim-c-1397ee539877 "> Средний </a>.

Помимо этих сообщений в блоге, вы также можете ознакомиться с <a href="https://cimplec.github.io/docs"> официальными документами </a>.

Прежде чем двигаться дальше, ознакомьтесь с правилами на [CONTRIBUTING.md] (./ CONTRIBUTING.md)

## Лицензия

sim-C находится под лицензией GNU General Public License (GPL) v3.0. [ЛИЦЕНЗИЯ] (./ ЛИЦЕНЗИЯ)

## Команда

- [Siddhartha Dhar Choudhury](https://github.com/frankhart2018)
- [Aayush Agarwal](https://github.com/Aayush-99)
- [Pranshul Dobriyal](https://github.com/PranshulDobriyal)
- [Dhairya Jain](https://github.com/dhairyaj)
