import streamlit as st
import pandas as pd
import numpy as np
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.units import cm
import tempfile

# =========================
# CONFIGURAÇÃO
# =========================
st.set_page_config(
    page_title="Intelligence Banking Pro",
    page_icon="💎",
    layout="wide"
)

st.markdown("""
<style>
.main { background-color: #f8f9fa; }
.card {
    background-color: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    margin-bottom: 15px;
}
h1, h2, h3 { color: #1e3a8a; }
</style>
""", unsafe_allow_html=True)

st.title("💎 Intelligence Banking – Simulador Estratégico")

# =========================
# MODO
# =========================
modo = st.radio("Modo de Visualização", ["👤 Cliente", "🧑‍💼 Consultor"], horizontal=True)

# =========================
# FUNÇÕES
# =========================
def calcular_consorcio(valor, prazo, taxa_adm, fundo, emb_pct, livre, fixo):
    taxa_total = (taxa_adm + fundo) / 100
    valor_plano = valor * (1 + taxa_total)
    parcela = valor_plano / prazo
    lance_emb = valor * (emb_pct / 100)
    credito_liquido = valor - lance_emb
    lance_total = lance_emb + livre + fixo

    return parcela, valor_plano, credito_liquido, lance_total

def financiamento(valor, taxa, prazo):
    parcela = valor * (taxa*(1+taxa)**prazo)/((1+taxa)**prazo-1)
    total = parcela * prazo
    juros = total - valor
    return parcela, total, juros

# =========================
# INPUTS
# =========================
st.header("📊 Dados da Simulação")

c1, c2 = st.columns(2)

with c1:
    credito = st.number_input("Crédito desejado (R$)", 100000.0, 3000000.0, 300000.0)
    prazo_c = st.number_input("Prazo Consórcio (meses)", 60, 240, 180)
    taxa_adm = st.number_input("Taxa Administrativa (%)", 5.0, 30.0, 15.0)
    fundo = st.number_input("Fundo Reserva (%)", 0.0, 5.0, 2.0)
    lance_emb = st.number_input("Lance Embutido (%)", 0.0, 50.0, 30.0)
    lance_livre = st.number_input("Lance Livre (R$)", 0.0, 500000.0, 0.0)
    lance_fixo = st.number_input("Lance Fixo (R$)", 0.0, 500000.0, 0.0)

with c2:
    valor_bem = st.number_input("Valor do Bem (Financiamento)", 100000.0, 5000000.0, 500000.0)
    entrada = st.number_input("Entrada (R$)", 0.0, valor_bem*0.8, valor_bem*0.2)
    prazo_f = st.number_input("Prazo Financiamento (meses)", 60, 420, 240)
    taxa_f = st.number_input("Taxa mensal (%)", 0.5, 3.0, 1.2) / 100

# =========================
# CÁLCULOS
# =========================
parc_c, plano, credito_liq, lance_total = calcular_consorcio(
    credito, prazo_c, taxa_adm, fundo, lance_emb, lance_livre, lance_fixo
)

valor_fin = valor_bem - entrada
parc_f, total_f, juros_f = financiamento(valor_fin, taxa_f, prazo_f)

melhor = "CONSÓRCIO" if parc_c < parc_f else "FINANCIAMENTO"

# =========================
# RESULTADOS
# =========================
st.header("📌 Resultado")

r1, r2 = st.columns(2)

with r1:
    st.markdown(f"""
    <div class="card">
    <h3>Consórcio</h3>
    Parcela: <b>R$ {parc_c:,.2f}</b><br>
    Crédito líquido: <b>R$ {credito_liq:,.2f}</b><br>
    Lance total: <b>R$ {lance_total:,.2f}</b>
    </div>
    """, unsafe_allow_html=True)

with r2:
    st.markdown(f"""
    <div class="card">
    <h3>Financiamento</h3>
    Parcela: <b>R$ {parc_f:,.2f}</b><br>
    Juros totais: <b>R$ {juros_f:,.2f}</b><br>
    Total pago: <b>R$ {total_f:,.2f}</b>
    </div>
    """, unsafe_allow_html=True)

st.success(f"🎯 Estratégia recomendada: **{melhor}**")

# =========================
# PROPOSTA + PDF
# =========================
st.header("📄 Proposta Automática")

cliente = st.text_input("Nome do Cliente")
consultor = st.text_input("Consultor Responsável")

texto = f"""
Cliente: {cliente}
Consultor: {consultor}

Estratégia recomendada: {melhor}

Resumo da Simulação:

CONSÓRCIO
- Parcela: R$ {parc_c:,.2f}
- Crédito líquido: R$ {credito_liq:,.2f}
- Lance total: R$ {lance_total:,.2f}

FINANCIAMENTO
- Parcela: R$ {parc_f:,.2f}
- Total de juros: R$ {juros_f:,.2f}

Conclusão:
A estratégia mais eficiente para este perfil é {melhor},
considerando custo total, impacto no caixa e flexibilidade financeira.
"""

st.text_area("Texto da Proposta", texto, height=250)

def gerar_pdf(texto):
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(temp.name, pagesize=A4,
                            rightMargin=2*cm,leftMargin=2*cm,
                            topMargin=2*cm,bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="Titulo",
        fontSize=18,
        textColor=HexColor("#1e3a8a"),
        spaceAfter=20
    ))

    story = []
    story.append(Paragraph("PROPOSTA INTELLIGENCE BANKING", styles["Titulo"]))
    for linha in texto.split("\n"):
        story.append(Paragraph(linha, styles["Normal"]))
        story.append(Spacer(1, 8))

    doc.build(story)
    return temp.name

if st.button("📄 Gerar PDF Institucional"):
    pdf_path = gerar_pdf(texto)
    with open(pdf_path, "rb") as f:
        st.download_button(
            "⬇️ Baixar Proposta em PDF",
            f,
            file_name="Proposta_Intelligence_Banking.pdf",
            mime="application/pdf"
        )

















