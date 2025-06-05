import streamlit as st
import pandas as pd
from graphviz import Digraph

st.set_page_config(layout="wide")
st.title("🗂️ Visualisateur d'organigramme dynamique")

uploaded_file = st.file_uploader("Importe ton fichier Excel ou CSV", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    df = df.fillna("")

    st.subheader("Aperçu du tableau")
    st.dataframe(df)

    level_names = df.columns.tolist()
    max_depth = len(level_names)

    st.sidebar.header("🎯 Affichage par niveau parent")

    parent_level = st.sidebar.selectbox("Choisir le niveau parent", level_names[:-1])
    parent_idx = level_names.index(parent_level)

    child_idx = parent_idx + 1
    child_level = level_names[child_idx]

    pairs_df = df[[parent_level, child_level]].dropna()
    pairs_df = pairs_df[(pairs_df[parent_level] != "") & (pairs_df[child_level] != "")]

    parents = sorted(pairs_df[parent_level].unique())
    selected_parents = st.sidebar.multiselect(f"Sélectionner les éléments du niveau '{parent_level}'", parents, default=parents)

    filtered_pairs = pairs_df[pairs_df[parent_level].isin(selected_parents)]
    edges = set(filtered_pairs.itertuples(index=False, name=None))

    st.subheader("📊 Organigramme généré")

    dot = Digraph()
    for parent, child in edges:
        dot.edge(parent, child)

    st.graphviz_chart(dot)
