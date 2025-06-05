import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Charger le fichier CSV
def load_data(file):
    return pd.read_csv(file)

# Dessiner l'organigramme
def draw_org_chart(df, parent_id=None):
    G = nx.DiGraph()

    if parent_id is None:
        # Trouver le niveau 0
        root_nodes = df[df['parent_id'].isna()]
    else:
        root_nodes = df[df['id'] == parent_id]

    for _, row in root_nodes.iterrows():
        G.add_node(row['id'])
        children = df[df['parent_id'] == row['id']]
        for _, child in children.iterrows():
            G.add_node(child['id'])
            G.add_edge(row['id'], child['id'])

    pos = nx.spring_layout(G)
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_size=3000, node_color='skyblue', font_size=10, font_weight='bold', arrowsize=20)
    st.pyplot(plt)

# Interface Streamlit
def main():
    st.title("Organigramme Interactif")

    uploaded_file = st.file_uploader("Choisissez un fichier CSV", type="csv")
    if uploaded_file is not None:
        data = load_data(uploaded_file)

        if 'id' not in data.columns or 'parent_id' not in data.columns:
            st.error("Le fichier CSV doit contenir les colonnes 'id' et 'parent_id'.")
            return

        parent_id = st.selectbox("Sélectionnez un nœud", options=[None] + list(data['id'].unique()))

        if st.button("Remonter d'un niveau"):
            if parent_id is not None:
                parent_row = data[data['id'] == parent_id].iloc[0]
                parent_id = parent_row['parent_id'] if pd.notna(parent_row['parent_id']) else None

        draw_org_chart(data, parent_id)

if __name__ == "__main__":
    main()
