from flask import flash
from node_functions import get_node_level


def add_edge(data, parent_id, child_id, probability, color):
    """
    Fügt eine neue Kante zu den Daten hinzu, wenn die Knoten nicht auf der gleichen Ebene sind.
    Überprüft die Ebenen der Knoten und fügt die Kante hinzu, wenn sie unterschiedlich sind.

    :param data: Die aktuellen Daten
    :param parent_id: ID des Elternknotens
    :param child_id: ID des Kindknotens
    :param probability: Wahrscheinlichkeit der Kante
    :param color: Farbe der Kante (wird verwendet, um AND-Gruppen zu kennzeichnen)
    :return: None
    """
    parent_level = get_node_level(data, parent_id)
    child_level = get_node_level(data, child_id)

    if parent_level == child_level:
        flash('Kanten können nicht zwischen Knoten auf der gleichen Ebene hinzugefügt werden.', 'error')
        return

    new_edge = {"parent": parent_id, "child": child_id, "probability": probability, "color": color}
    data['edges'].append(new_edge)


def edit_edge_probability(data, node_id, new_probability):
    """
    Bearbeitet die Wahrscheinlichkeit einer Kante.
    Überprüft, ob der neue Wahrscheinlichkeitswert eine gültige Zahl ist und aktualisiert die Kante entsprechend.

    :param data: Die aktuellen Daten
    :param node_id: ID des Kindknotens der Kante
    :param new_probability: Neue Wahrscheinlichkeit für die Kante
    :return: None
    """
    try:
        probability_value = float(new_probability.replace(',', '.'))
    except ValueError:
        flash('Die Wahrscheinlichkeit muss einen Zahlenwert sein.', 'error')
        return

    for edge in data['edges']:
        if edge['child'] == node_id:
            edge['probability'] = new_probability
            break


def edit_edge_color(data, node_id, new_color):
    """
    Bearbeitet die Farbe einer Kante.
    Durchsucht die Kanten nach der Kante mit der angegebenen Kindknoten-ID und aktualisiert deren Farbe.

    :param data: Die aktuellen Daten
    :param node_id: ID des Kindknotens der Kante
    :param new_color: Neue Farbe für die Kante
    :return: None
    """
    for edge in data['edges']:
        if edge['child'] == node_id:
            edge['color'] = new_color
            break


#def update_edge_probability(data, node_id, new_probability):
#    if new_probability:
#        edit_edge_probability(data, node_id, new_probability)


def update_edge_color(data, node_id, new_and_or):
    """
    Aktualisiert die Farbe einer Kante basierend auf dem neuen AND/OR-Wert.
    Setzt die Farbe der Kante auf 'schwarz', wenn der neue Wert 'and' oder 'or' ist.

    :param data: Die aktuellen Daten
    :param node_id: ID des Kindknotens der Kante
    :param new_and_or: Neuer AND/OR-Wert
    :return: None
    """
    if new_and_or:
        edit_edge_color(data, node_id, 'black' if new_and_or == 'and' else 'black')
