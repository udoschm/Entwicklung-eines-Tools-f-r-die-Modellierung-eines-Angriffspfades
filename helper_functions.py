import json
import os

from flask import flash
from graphviz import Digraph


def load_data(file_path='config/attack_tree_data.json'):
    """
    Lädt die Daten aus der JSON-Datei.

    :param file_path: Pfad zur JSON-Datei
    :return: Die geladenen Daten
    """
    with open(file_path, 'r') as file:
        return json.load(file)


def save_data(data, file_path='config/attack_tree_data.json'):
    """
    Speichert die Daten in die JSON-Datei.
    :param data: Die zu speichernden Daten
    :param file_path: Pfad zur JSON-Datei
    :return: None
    """
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


def initialize_data_file(file_path, initial_data):
    """
    Initialisiert die JSON-Datei mit den Anfangsdaten, falls sie nicht existiert.
    :param file_path: Pfad zur JSON-Datei
    :param initial_data: Anfangsdaten, die in die Datei geschrieben werden sollen
    :return: None
    """
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            json.dump(initial_data, file, indent=4)


def create_attack_tree_image(nodes, edges, file_path='static/attack_tree', format='svg'):
    """
    Erstellt ein Attack-Tree-Bild basierend auf den Knoten und Kanten.
    Fügt Knoten und Kanten zum Diagramm hinzu und gruppiert Knoten in AND-Gruppen.
    Rendert das Bild und speichert es im angegebenen Dateipfad.

    :param nodes: Liste der Knoten
    :param edges: Liste der Kanten
    :param file_path: Pfad, unter dem das Bild gespeichert wird
    :param format: Format des Bildes (Standard: 'svg')
    :return: None
    """
    dot = Digraph()
    #dot.attr(rankdir='TB', nodesep='0.2', ranksep='0.2')  # Minimale Abstände setzen

    group_to_nodes = create_and_groups(nodes)  # Funktion, die AND-Gruppen erstellt.

    # Knoten hinzufügen
    for node in nodes:
        label = f"<b>{node['name']}</b>"
        attributes = node.get('attributes', {})
        for key, value in attributes.items():
            if value.get('display_in_tree', 'false').lower() == 'true':
                label += f"<br/>{key}: {value['value']}"
        dot.node(node['id'], f"<{label}>", shape='box')

    cluster_index = 0
    group_to_cluster = {}

    # Subgraphen (AND-Gruppen) hinzufügen
    for group, children in group_to_nodes.items():
        if group:  # Nur Gruppen mit Knoten berücksichtigen
            total_probability = sum(
                float(edge['probability'].replace(',', '.')) for edge in edges if edge['child'] in children)
            total_probability = f"{total_probability:.2f}"  # Format auf 2 Dezimalstellen

            with dot.subgraph(name=f'cluster_{cluster_index}') as c:
                c.attr(
                    style='dashed',
                    label=f"AND Group: {group} (Total Prob.: {total_probability})",
                    labelloc="t",
                    labeljust="l",
                    fontsize="12",
                )

                # Dummy-Node für die mittige Platzierung
                if any(edge['parent'] in children for edge in edges):
                    dummy_node_id = f"dummy_{cluster_index}"
                    c.node(dummy_node_id, shape='point', width='0.01', height='0.01')

                    for child in children:
                        c.edge(child, dummy_node_id, minlen='1')

                    group_to_cluster[group] = dummy_node_id

                # Alle Kinderknoten hinzufügen
                for child in children:
                    c.node(child)

                # Unsichtbare Kanten zwischen Kindern und Dummy-Node


            cluster_index += 1

    # Kanten hinzufügen
    for edge in edges:
        label = edge['probability'] if edge['probability'] else 'N/A'
        color = edge.get('color', 'black')
        parent = edge['parent']
        child = edge['child']

        # Falls der Parent Teil einer Gruppe ist, Dummy-Node verwenden
        parent_group = next((group for group, children in group_to_nodes.items() if parent in children), None)
        if parent_group:
            parent = group_to_cluster[parent_group]

        dot.edge(parent, child, label=label, color=color)

    # Legende hinzufügen
# legend = '''<
#     <TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0">
#     <TR><TD ALIGN="LEFT"><B>Legende:</B></TD></TR>
#     <TR><TD ALIGN="LEFT"><FONT COLOR="blue">AND-Verknüpfung</FONT></TD></TR>
#     <TR><TD ALIGN="LEFT"><FONT COLOR="black">OR-Verknüpfung</FONT></TD></TR>
#     </TABLE>
# >'''
# dot.attr(label=legend, labelloc="b", labeljust="l")

    # Bild rendern
    dot.render(file_path, format=format, cleanup=True)


def create_and_groups(nodes):
    """
    Erstellt ein Mapping von Gruppen zu ihren Knoten.
    Durchsucht die Knoten nach Gruppen und ordnet die Knoten den entsprechenden Gruppen zu.

    :param nodes: Liste der Knoten
    :return: Dictionary, das Gruppen zu Knoten mappt
    """
    group_to_nodes = {}
    for node in nodes:
        group = node.get('group')
        if group is not None:
            if group not in group_to_nodes:
                group_to_nodes[group] = []
            group_to_nodes[group].append(node['id'])
    return group_to_nodes

def check_and_groups_with_single_node(nodes):
    """
    Überprüft, ob es AND-Gruppen mit nur einem Knoten gibt.
    Durchsucht die Knoten nach AND-Gruppen und überprüft deren Größe.
    Zeigt eine Info-Nachricht an, wenn eine AND-Gruppe nur einen Knoten enthält.

    :param nodes: Liste der Knoten
    :return: None
    """
    group_to_nodes = create_and_groups(nodes)

    for group, children in group_to_nodes.items():
        if len(children) == 1:
            flash(f"Die AND Verknüpfung '{group}' besitzt nur einen Node!", 'info')


def check_parent_nodes_probability(nodes, edges):
    """
    Überprüft, ob ein Elternknoten Kinder mit einer Gesamtwahrscheinlichkeit ungleich 1 hat.
    Durchsucht die Kanten und berechnet die Gesamtwahrscheinlichkeit der Kinder für jeden Elternknoten.
    Zeigt eine Info-Nachricht an, wenn die Gesamtwahrscheinlichkeit ungleich 1 ist.

    :param nodes: Liste der Knoten
    :param edges: Liste der Kanten
    :return: None
    """
    id_to_name = {node['id']: node['name'] for node in nodes}
    parent_to_children_prob = {}

    for edge in edges:
        parent = edge['parent']
        probability = float(edge['probability'].replace(',', '.'))
        if parent not in parent_to_children_prob:
            parent_to_children_prob[parent] = 0
        parent_to_children_prob[parent] += probability

    for parent, total_probability in parent_to_children_prob.items():
        total_probability = round(total_probability, 2)
        if total_probability != 1:
            parent_name = id_to_name.get(parent, 'Unbekannt')
            flash(f"Der Knoten '{parent_name}' hat Kinder mir einer Gesamtwahrscheinlichkeit von {total_probability} !", 'info')

def find_new_parent_id(data, child_id):
    """
    Findet die neue Eltern-ID für einen gegebenen Kindknoten.

    :param data: Die aktuellen Daten
    :param child_id: ID des Kindknotens
    :return: Neue Eltern-ID oder None
    """
    new_parent_id = next((edge['parent'] for edge in data['edges'] if edge['child'] == child_id), None)
    if new_parent_id:
        for node in data['nodes']:
            if node['id'] == child_id:
                node['parent'] = new_parent_id
                break
    return new_parent_id