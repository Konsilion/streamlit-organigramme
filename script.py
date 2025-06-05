import streamlit as st
import pandas as pd
from graphviz import Digraph
import io

st.set_page_config(layout="wide")
st.title("🗂️ Visualisateur d'organigramme dynamique")

# --- UPLOAD ---
uploaded_file = st.file_uploader("Importe ton fichier Excel ou CSV", type=["csv", "xlsx"])

if uploaded_file:
    # --- READ FILE ---
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    df = df.fillna("")  # Remplace les NaN par des chaînes vides

    st.subheader("Aperçu du tableau")
    st.dataframe(df)

    max_depth = df.shape[1]

    # --- SELECT LEVELS ---
    st.sidebar.header("🛠️ Paramètres d'affichage")
    level_names = df.columns.tolist()
    min_level = st.sidebar.selectbox("Niveau le plus haut (inclus)", level_names, index=0)
    max_level = st.sidebar.selectbox("Niveau le plus bas (inclus)", level_names, index=max_depth - 1)

    min_idx = level_names.index(min_level)
    max_idx = level_names.index(max_level)

    # --- RÉCUPÉRER INTITULÉS UNIQUES ENTRE LES NIVEAUX SÉLECTIONNÉS ---
    selectable_levels = level_names[min_idx:max_idx + 1]
    selection_dict = {}
    for col in selectable_levels:
        uniques = sorted(set(df[col].dropna()) - {""})
        selected = st.sidebar.multiselect(f"Afficher les éléments du niveau '{col}'", uniques, default=uniques)
        selection_dict[col] = set(selected)

    # --- GÉNÉRER EDGES ---
    edges = set()
    valid_paths = []

    for _, row in df.iterrows():
        path = [row[col] for col in level_names if row[col] != ""]
        
        # Vérifier que tous les éléments entre min et max niveaux sont dans la sélection
        path_valid = True
        for i in range(min_idx, min(max_idx + 1, len(path))):
            val = row[level_names[i]]
            if val not in selection_dict[level_names[i]]:
                path_valid = False
                break
        
        if path_valid:
            truncated_path = path[min_idx:max_idx + 1]
            valid_paths.append(truncated_path)

    for path in valid_paths:
        for i in range(len(path) - 1):
            edges.add((path[i], path[i + 1]))

    # --- GRAPHVIZ ---
    st.subheader("📊 Organigramme généré")

    dot = Digraph()
    for parent, child in edges:
        dot.edge(parent, child)

    st.graphviz_chart(dot)
