import streamlit as st
import pandas as pd
from graphviz import Digraph

st.set_page_config(layout="wide")
st.title("🗂️ Navigation hiérarchique dans un organigramme")

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

    # --- SESSION STATE ---
    if "current_level" not in st.session_state:
        st.session_state.current_level = 0
    if "history" not in st.session_state:
        st.session_state.history = []
    if "current_value" not in st.session_state:
        st.session_state.current_value = None

    level = st.session_state.current_level
    current_col = level_names[level]

    if st.session_state.current_value:
        st.markdown(f"### Niveau **{current_col}** → _{st.session_state.current_value}_")

    # Affichage des enfants du niveau courant
    if level < max_depth - 1:
        child_col = level_names[level + 1]
        if st.session_state.current_value:
            children_df = df[df[current_col] == st.session_state.current_value][[current_col, child_col]]
        else:
            children_df = df[[current_col, child_col]]

        children_df = children_df.dropna()
        children_df = children_df[(children_df[current_col] != "") & (children_df[child_col] != "")]
        children = sorted(children_df[child_col].unique())

        if children:
            selected_child = st.selectbox(f"Sélectionne un enfant du niveau '{child_col}'", [""] + children)

            col1, col2 = st.columns(2)
            with col1:
                if selected_child and st.button("🔽 Descendre à l'enfant"):
                    st.session_state.history.append((level, st.session_state.current_value))
                    st.session_state.current_level += 1
                    st.session_state.current_value = selected_child
                    st.experimental_rerun()

            with col2:
                if st.session_state.history and st.button("🔼 Remonter"):
                    prev_level, prev_value = st.session_state.history.pop()
                    st.session_state.current_level = prev_level
                    st.session_state.current_value = prev_value
                    st.experimental_rerun()
        else:
            st.info("Aucun enfant à afficher à ce niveau.")
            if st.session_state.history and st.button("🔼 Remonter"):
                prev_level, prev_value = st.session_state.history.pop()
                st.session_state.current_level = prev_level
                st.session_state.current_value = prev_value
                st.experimental_rerun()
    else:
        st.info("Dernier niveau atteint.")
        if st.session_state.history and st.button("🔼 Remonter"):
            prev_level, prev_value = st.session_state.history.pop()
            st.session_state.current_level = prev_level
            st.session_state.current_value = prev_value
            st.experimental_rerun()

    # --- Affichage Graphviz du chemin parcouru ---
    st.subheader("📊 Organigramme partiel")
    dot = Digraph()

    path = [val for _, val in st.session_state.history]
    if st.session_state.current_value:
        path.append(st.session_state.current_value)

    for i in range(len(path) - 1):
        dot.edge(path[i], path[i + 1])

    st.graphviz_chart(dot)
