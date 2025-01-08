import uuid

from flask import flash

from helper_functions import save_data


def add_node(data, name, parent_id, probability, color, group=None, attributes=None):
    """
    Fügt einen neuen Knoten und die entsprechende Kante zu den Daten hinzu.
    Überprüft die Wahrscheinlichkeit und fügt den neuen Knoten und die Kante zu den Daten hinzu.

    :param data: Die aktuellen Daten
    :param name: Name des neuen Knotens
    :param parent_id: ID des Elternknotens
    :param probability: Wahrscheinlichkeit der Kante
    :param color: Farbe der Kante (wird verwendet, um AND-Gruppen zu kennzeichnen)
    :param group: Gruppe des Knotens (für AND-Verknüpfungen)
    :param attributes: Attribute des Knotens
    :return: None
    """
    try:
        probability_value = float(probability.replace(',', '.'))  # Wahrscheinlichkeit in eine Zahl umwandeln
    except ValueError:
        flash('Die Wahrscheinlichkeit muss einen Zahlenwert sein.', 'error')
        return

    total_probability = sum(
        float(edge['probability'].replace(',', '.')) for edge in data['edges']
        if edge['parent'] == parent_id
    )

    if total_probability + probability_value > 1:
        flash('Die Gesamtwahrscheinlichkeit der Kindknoten darf 1 nicht überschreiten.', 'error')
        return

    new_node = {
        "id": str(uuid.uuid4()),  # Generiert eine eindeutige ID für den neuen Knoten
        "name": name,
        "color": color,
        "group": group,
        "attributes": attributes or {}
    }
    data['nodes'].append(new_node)
    new_edge = {"parent": parent_id, "child": new_node['id'], "probability": probability, "color": color}
    data['edges'].append(new_edge)


def edit_node_name(data, node_id, new_name):
    """
    Bearbeitet den Namen eines Knotens.

    :param data: Die aktuellen Daten
    :param node_id: ID des zu bearbeitenden Knotens
    :param new_name: Neuer Name für den Knoten
    :return: None
    """
    for node in data['nodes']:
        if node['id'] == node_id:
            node['name'] = new_name
            break


def delete_node(data, node_id):
    """
    Löscht einen Knoten und die entsprechenden Kanten aus den Daten.
    Entfernt den Knoten mit der angegebenen ID und alle Kanten, die mit diesem Knoten verbunden sind.

    :param data: Die aktuellen Daten
    :param node_id: ID des zu löschenden Knotens
    :return: None
    """
    data['nodes'] = [node for node in data['nodes'] if node['id'] != node_id]
    data['edges'] = [edge for edge in data['edges'] if edge['parent'] != node_id and edge['child'] != node_id]


def get_node_level(data, node_id):
    """
    Bestimmt die Ebene eines Knotens in einem Baum.
    Durchläuft die Kanten, um die Anzahl der Ebenen vom gegebenen Knoten bis zur Wurzel zu zählen.

    :param data: Die aktuellen Daten
    :param node_id: ID des Knotens
    :return: Ebene des Knotens
    """
    level = 0
    current_node_id = node_id
    while True:
        parent_edge = next((edge for edge in data['edges'] if edge['child'] == current_node_id), None)
        if not parent_edge:
            break
        level += 1
        current_node_id = parent_edge['parent']
    return level





def update_node_name(data, node_id, new_name):
    """
    Aktualisiert den Namen eines Knotens.
    Überprüft, ob der neue Name bereits existiert und ändert den Namen des Knotens.

    :param data: Die aktuellen Daten
    :param node_id: ID des zu bearbeitenden Knotens
    :param new_name: Neuer Name für den Knoten
    :return: None
    """
    if new_name:
        if node_name_exists(data, new_name):
            return flash('Ein Knoten mit diesem Namen existiert bereits.', 'error')
        edit_node_name(data, node_id, new_name)


def update_node_parent(data, node_id, new_parent_id):
    """
    Aktualisiert die Eltern-ID eines Knotens.
    Überprüft, ob die neue Eltern-ID gültig ist und ändert die Eltern-ID des Knotens.

    :param data: Die aktuellen Daten
    :param node_id: ID des zu bearbeitenden Knotens
    :param new_parent_id: Neue Eltern-ID für den Knoten
    :return: None
    """
    if new_parent_id and new_parent_id != "Keine Änderung":
        for edge in data['edges']:
            if edge['child'] == node_id:
                edge['parent'] = new_parent_id
                break


def update_node_group(data, node_id, new_group):
    """
    Aktualisiert die Gruppenzugehörigkeit eines Knotens.

    :param data: Die aktuellen Daten
    :param node_id: ID des zu bearbeitenden Knotens
    :param new_group: Neue Gruppe für den Knoten
    :return: None
    """
    if new_group:
        for node in data['nodes']:
            if node['id'] == node_id:
                node['group'] = new_group
                break


def update_node_attributes(data, node_id, attributes):
    """
    Aktualisiert die Attribute eines Knotens.
    Durchsucht die Knoten nach der gegebenen ID und ändert die Attribute des Knotens.

    :param data: Die aktuellen Daten
    :param node_id: ID des zu bearbeitenden Knotens
    :param attributes: Neue Attribute für den Knoten
    :return: None
    """
    for node in data['nodes']:
        if node['id'] == node_id:
            node['attributes'] = attributes
            break

def node_name_exists(data, name):
    """
    Überprüft, ob ein Knotenname bereits in den Daten existiert.

    :param data: Die Daten, die Knoten enthalten
    :param name: Der zu überprüfende Knotenname
    :return: True, wenn der Knotenname existiert, sonst False
    """
    return any(node['name'] == name for node in data['nodes'])

def create_attributes_dict(attribute_names, attribute_values, display_in_tree_flags):
    """
    Erstellt ein Dictionary von Attributen aus den bereitgestellten Listen.
    Überprüft die Listen und fügt die Attribute dem Dictionary hinzu.

    :param attribute_names: Liste der Attributnamen
    :param attribute_values: Liste der Attributwerte
    :param display_in_tree_flags: Liste der Flags, ob das Attribut im Baum angezeigt werden soll
    :return: Dictionary der Attribute
    """
    attributes = {}
    if attribute_names and attribute_values != [""]:
        for attribute_name, attribute_value, display_in_tree in zip(attribute_names, attribute_values, display_in_tree_flags):
            if attribute_name != "" and attribute_value != "":
                attributes[attribute_name.strip()] = {
                    "value": attribute_value.strip(),
                    "display_in_tree": display_in_tree.lower()
                }
    return attributes
