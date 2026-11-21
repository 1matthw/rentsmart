"""
RentSmart - Sistema de Orçamento de Locação da R.M Imóveis
Python + Programação Orientada a Objetos
"""
import csv
from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP

# ----------------------------------------------------------------------
# CONSTANTES DE NEGÓCIO (regras comerciais da R.M Imóveis)
# ----------------------------------------------------------------------
TAXA_CONTRATUAL = Decimal("2000.00")
MAX_PARCELAS_TAXA = 5
MESES_PROJECAO = 12
DESCONTO_SEM_CRIANCAS = Decimal("0.05")  # só apartamentos
VAGA_GARAGEM = Decimal("300.00")          # casas e apartamentos
ESTUDIO_PACOTE_2_VAGAS = Decimal("250.00")
ESTUDIO_VAGA_EXTRA = Decimal("60.00")


def money(valor) -> Decimal:
    """Arredonda para 2 casas (centavos)."""
    return Decimal(valor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def brl(valor) -> str:
    """Formata como moeda brasileira: R$ 1.234,56"""
    texto = f"{money(valor):,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


# ----------------------------------------------------------------------
# MODELO DE DOMÍNIO: IMÓVEIS (herança + polimorfismo)
# ----------------------------------------------------------------------
class Imovel(ABC):
    """Classe base abstrata para qualquer imóvel da R.M Imóveis."""

    nome_tipo = "Imóvel"

    def __init__(self, aluguel_base: Decimal):
        self._aluguel_base = Decimal(aluguel_base)

    @property
    def aluguel_base(self) -> Decimal:
        return self._aluguel_base

    @abstractmethod
    def adicionais(self) -> dict:
        """Retorna {descrição: valor} dos adicionais mensais."""

    def aceita_desconto_sem_criancas(self) -> bool:
        return False

    def descricao(self) -> str:
        return self.nome_tipo


class Apartamento(Imovel):
    nome_tipo = "Apartamento"

    def __init__(self, quartos: int, com_garagem: bool):
        super().__init__(Decimal("700.00"))
        self.quartos = quartos
        self.com_garagem = com_garagem

    def adicionais(self) -> dict:
        extras = {}
        if self.quartos == 2:
            extras["Adicional 2 quartos"] = Decimal("200.00")
        if self.com_garagem:
            extras["Vaga de garagem"] = VAGA_GARAGEM
        return extras

    def aceita_desconto_sem_criancas(self) -> bool:
        return True

    def descricao(self) -> str:
        return f"Apartamento de {self.quartos} quarto(s)"


class Casa(Imovel):
    nome_tipo = "Casa"

    def __init__(self, quartos: int, com_garagem: bool):
        super().__init__(Decimal("900.00"))
        self.quartos = quartos
        self.com_garagem = com_garagem

    def adicionais(self) -> dict:
        extras = {}
        if self.quartos == 2:
            extras["Adicional 2 quartos"] = Decimal("250.00")
        if self.com_garagem:
            extras["Vaga de garagem"] = VAGA_GARAGEM
        return extras

    def descricao(self) -> str:
        return f"Casa de {self.quartos} quarto(s)"


class Estudio(Imovel):
    nome_tipo = "Estúdio"

    def __init__(self, vagas: int):
        super().__init__(Decimal("1200.00"))
        self.vagas = vagas

    def adicionais(self) -> dict:
        extras = {}
        if self.vagas >= 1:
            # pacote inicial cobre até 2 vagas; extras a partir da 3ª
            extras["Pacote estacionamento (2 vagas)"] = ESTUDIO_PACOTE_2_VAGAS
            if self.vagas > 2:
                qtd = self.vagas - 2
                extras[f"Vagas adicionais ({qtd}x)"] = ESTUDIO_VAGA_EXTRA * qtd
        return extras

    def descricao(self) -> str:
        return f"Estúdio com {self.vagas} vaga(s)"


# ----------------------------------------------------------------------
# ORÇAMENTO
# ----------------------------------------------------------------------
class Orcamento:
    """Calcula aluguel mensal, desconto, taxa contratual e parcelamento."""

    def __init__(self, imovel: Imovel, tem_criancas: bool, parcelas_taxa: int,
                 cliente: str = "Cliente"):
        self.imovel = imovel
        self.tem_criancas = tem_criancas
        self.parcelas_taxa = parcelas_taxa
        self.cliente = cliente

    # --- cálculos do aluguel ---
    def total_adicionais(self) -> Decimal:
        return sum(self.imovel.adicionais().values(), Decimal("0"))

    def subtotal_aluguel(self) -> Decimal:
        """Aluguel-base + adicionais (antes do desconto)."""
        return self.imovel.aluguel_base + self.total_adicionais()

    def desconto(self) -> Decimal:
        if self.imovel.aceita_desconto_sem_criancas() and not self.tem_criancas:
            return money(self.subtotal_aluguel() * DESCONTO_SEM_CRIANCAS)
        return Decimal("0.00")

    def aluguel_mensal(self) -> Decimal:
        return money(self.subtotal_aluguel() - self.desconto())

    # --- taxa contratual ---
    def valores_parcelas_taxa(self) -> list:
        """Divide a taxa em N parcelas; a última absorve a diferença de centavos."""
        n = self.parcelas_taxa
        base = money(TAXA_CONTRATUAL / n)
        parcelas = [base] * n
        parcelas[-1] = money(TAXA_CONTRATUAL - base * (n - 1))
        return parcelas

    # --- projeção ---
    def projecao_12_meses(self) -> list:
        parcelas = self.valores_parcelas_taxa()
        linhas = []
        for mes in range(1, MESES_PROJECAO + 1):
            taxa = parcelas[mes - 1] if mes <= len(parcelas) else Decimal("0.00")
            aluguel = self.aluguel_mensal()
            linhas.append({
                "mes": mes,
                "aluguel": aluguel,
                "taxa": taxa,
                "total": money(aluguel + taxa),
            })
        return linhas

    # --- exibição ---
    def resumo(self) -> str:
        l = ["", "=" * 56, "           ORÇAMENTO DE LOCAÇÃO - R.M IMÓVEIS", "=" * 56,
             f"Cliente: {self.cliente}", f"Imóvel : {self.imovel.descricao()}", "-" * 56,
             f"{'Aluguel-base':<38}{brl(self.imovel.aluguel_base):>18}"]
        for desc, valor in self.imovel.adicionais().items():
            l.append(f"{'+ ' + desc:<38}{brl(valor):>18}")
        l.append(f"{'Subtotal do aluguel':<38}{brl(self.subtotal_aluguel()):>18}")
        if self.desconto() > 0:
            l.append(f"{'- Desconto 5% (sem crianças)':<38}{brl(self.desconto()):>18}")
        l.append("-" * 56)
        l.append(f"{'ALUGUEL MENSAL FINAL':<38}{brl(self.aluguel_mensal()):>18}")
        l.append("")
        l.append("TAXA CONTRATUAL (cobrada separadamente do aluguel)")
        l.append(f"{'Valor total da taxa':<38}{brl(TAXA_CONTRATUAL):>18}")
        parcelas = self.valores_parcelas_taxa()
        l.append(f"Parcelamento: {self.parcelas_taxa}x")
        for i, p in enumerate(parcelas, 1):
            l.append(f"   Parcela {i}/{self.parcelas_taxa}: {brl(p)}")
        total_ano = sum((r["total"] for r in self.projecao_12_meses()), Decimal("0"))
        l.append("-" * 56)
        l.append(f"{'TOTAL PREVISTO NO 1º ANO':<38}{brl(total_ano):>18}")
        l.append("=" * 56)
        return "\n".join(l)


# ----------------------------------------------------------------------
# EXPORTAÇÃO CSV
# ----------------------------------------------------------------------
class ExportadorCSV:
    def __init__(self, caminho: str = "projecao_12_meses.csv"):
        self.caminho = caminho

    @staticmethod
    def _fmt(valor) -> str:
        return f"{money(valor):.2f}".replace(".", ",")  # padrão pt-BR

    def exportar(self, orcamento: Orcamento) -> str:
        linhas = orcamento.projecao_12_meses()
        with open(self.caminho, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["Mes", "Aluguel Mensal (R$)",
                        "Parcela Taxa Contratual (R$)", "Total do Mes (R$)"])
            for r in linhas:
                w.writerow([r["mes"], self._fmt(r["aluguel"]),
                            self._fmt(r["taxa"]), self._fmt(r["total"])])
            w.writerow(["TOTAL",
                        self._fmt(sum(r["aluguel"] for r in linhas)),
                        self._fmt(sum(r["taxa"] for r in linhas)),
                        self._fmt(sum(r["total"] for r in linhas))])
        return self.caminho


# ----------------------------------------------------------------------
# ENTRADA DE DADOS COM VALIDAÇÃO
# ----------------------------------------------------------------------
def ler_inteiro(msg: str, minimo: int, maximo: int) -> int:
    while True:
        txt = input(msg).strip()
        if txt.isdigit() and minimo <= int(txt) <= maximo:
            return int(txt)
        print(f"  ⚠ Entrada inválida. Digite um número entre {minimo} e {maximo}.")


def ler_sim_nao(msg: str) -> bool:
    while True:
        txt = input(msg + " (s/n): ").strip().lower()
        if txt in ("s", "sim"):
            return True
        if txt in ("n", "nao", "não"):
            return False
        print("  ⚠ Responda com 's' ou 'n'.")


def ler_texto(msg: str) -> str:
    while True:
        txt = input(msg).strip()
        if txt:
            return txt
        print("  ⚠ O campo não pode ficar vazio.")


def montar_imovel() -> Imovel:
    print("\nTipo de imóvel:\n  1 - Apartamento\n  2 - Casa\n  3 - Estúdio")
    tipo = ler_inteiro("Escolha (1-3): ", 1, 3)
    if tipo == 3:
        print("Estacionamento do estúdio: pacote inicial de 2 vagas (R$ 250,00); "
              "vaga adicional R$ 60,00.")
        return Estudio(ler_inteiro("Número de vagas (0 = nenhuma): ", 0, 10))
    quartos = ler_inteiro("Número de quartos (1 ou 2): ", 1, 2)
    garagem = ler_sim_nao("Deseja vaga de garagem (+R$ 300,00/mês)?")
    return Apartamento(quartos, garagem) if tipo == 1 else Casa(quartos, garagem)


def main():
    print("=== RentSmart | R.M Imóveis ===")
    cliente = ler_texto("Nome do cliente: ")
    imovel = montar_imovel()
    tem_criancas = True
    if imovel.aceita_desconto_sem_criancas():
        tem_criancas = ler_sim_nao("O cliente possui crianças?")
    print(f"\nA taxa contratual é de {brl(TAXA_CONTRATUAL)}, em até "
          f"{MAX_PARCELAS_TAXA} parcelas.")
    parcelas = ler_inteiro(f"Número de parcelas (1-{MAX_PARCELAS_TAXA}): ",
                           1, MAX_PARCELAS_TAXA)

    orcamento = Orcamento(imovel, tem_criancas, parcelas, cliente)
    print(orcamento.resumo())
    caminho = ExportadorCSV().exportar(orcamento)
    print(f"\n✔ Projeção de 12 meses salva em: {caminho}")


if __name__ == "__main__":
    main()
