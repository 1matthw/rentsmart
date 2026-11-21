# RentSmart — Sistema de Orçamento de Locação (R.M Imóveis)

Aplicação em Python (Programação Orientada a Objetos) que calcula o orçamento de locação de apartamentos,
casas e estúdios, apresenta um resumo detalhado e gera um arquivo CSV com a projeção dos 12 primeiros meses.

## Requisitos
- Python 3.8 ou superior
- Nenhuma biblioteca externa (usa apenas a biblioteca padrão: `csv`, `decimal`, `abc`)

## Como executar
```bash
python rentsmart.py
```
(em alguns sistemas: `python3 rentsmart.py`)

O programa pergunta, nesta ordem: nome do cliente, tipo de imóvel, quartos/vagas, garagem,
se há crianças (apenas apartamentos) e o número de parcelas da taxa contratual (1 a 5).
As entradas são validadas; valores inválidos são solicitados novamente.

## Saída
- Resumo do orçamento no terminal (aluguel-base, adicionais, desconto, aluguel final,
  taxa contratual e parcelamento **apresentados separadamente**).
- Arquivo `projecao_12_meses.csv` (separador `;`, valores no padrão brasileiro) com:
  mês, aluguel mensal, parcela da taxa contratual e total do mês, mais uma linha de TOTAL.

## Regras de negócio implementadas
| Item | Regra |
|---|---|
| Apartamento 1 quarto | R$ 700,00 |
| Casa 1 quarto | R$ 900,00 |
| Estúdio | R$ 1.200,00 |
| Apartamento 2 quartos | + R$ 200,00 |
| Casa 2 quartos | + R$ 250,00 |
| Garagem (casa/apartamento) | + R$ 300,00 / mês |
| Estúdio — estacionamento | pacote de 2 vagas R$ 250,00; vaga adicional R$ 60,00 |
| Desconto sem crianças | 5% sobre o aluguel **após** os adicionais (somente apartamentos) |
| Taxa contratual | R$ 2.000,00 em até 5 parcelas (cobrada à parte do aluguel) |

## Premissas adotadas
1. Estúdio com 1 ou 2 vagas paga o pacote de R$ 250,00; a partir da 3ª vaga soma R$ 60,00 por vaga.
2. O desconto de 5% incide sobre aluguel-base + todos os adicionais mensais (quartos e garagem).
3. As parcelas da taxa contratual são cobradas nos primeiros meses; a última parcela absorve a diferença de centavos.
4. Cálculos feitos com `Decimal` para evitar erros de arredondamento com dinheiro.

## Estrutura do código
- `Imovel` (classe abstrata) → `Apartamento`, `Casa`, `Estudio` (herança e polimorfismo)
- `Orcamento` — cálculos de aluguel, desconto, taxa, parcelas e projeção
- `ExportadorCSV` — geração do arquivo CSV
- Funções de entrada/validação e `main()`
