from flask import Flask, render_template, request, redirect, url_for, flash, send_file, send_from_directory, jsonify

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph

from helper_functions import *
from edge_functions import *
from node_functions import *

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

initial_data = {
    "nodes": [
        {
            "id": "e373b305-49f6-4594-a2d5-aa8c0e5e1851",
            "name": "Node",
            "attributes": {}
        }
    ],
    "edges": []
}


def initialize_data():
    """
    Initialisiert die Daten, indem die JSON-Datei mit den Anfangsdaten erstellt wird, falls sie nicht existiert.
    :return: None
    """
    initialize_data_file('config/attack_tree_data.json', initial_data)


initialize_data()


@app.route('/')
def index():
    """
    Lädt die Daten und rendert die Hauptseite der Anwendung.
    Überprüft die Daten auf Korrektheit und erstellt ein Angriffsbaum-Bild.

    :return: Das gerenderte Template für die Hauptseite.
    """
    try:
        data = load_data()
    except FileNotFoundError:
        initialize_data()
        data = load_data()
    check_and_groups_with_single_node(data.get('nodes', []))
    check_parent_nodes_probability(data.get('nodes', []), data.get('edges', []))
    root_node = None

    # Den Root-Knoten finden (Knoten ohne Eltern)
    for node in data['nodes']:
        if not any(edge['child'] == node['id'] for edge in data['edges']):
            root_node = node
            break

    id_to_name = {node['id']: node['name'] for node in data['nodes']}

    # Füge jedem Knoten basierend auf den Kanten den Namen des Elternknotens hinzu
    for node in data['nodes']:
        parent_edge = next((edge for edge in data['edges'] if edge['child'] == node['id']), None)
        parent_id = parent_edge['parent'] if parent_edge else None
        node['parent_name'] = id_to_name.get(parent_id, 'None') if parent_id else 'None'

    create_attack_tree_image(data['nodes'], data['edges'])

    # Extrahiere eindeutige Gruppen
    groups = list(set(node.get('group') for node in data['nodes'] if node.get('group')))

    return render_template('index.html', nodes=data['nodes'], edges=data['edges'], root_node=root_node,
                           selected_node=None, groups=groups)


@app.route('/add_node', methods=['POST'])
def add_node_route():
    """
    Fügt einen neuen Knoten basierend auf den Formulardaten hinzu.
    Überprüft auf doppelte Attributnamen und vorhandene Knotennamen.

    :return: Weiterleitung zur Hauptseite.
    """
    name = request.form['name']
    parent_id = request.form['parent_id']
    probability = request.form['probability']
    color = "black" if request.form['and_or'] == "and" else "black"
    group = request.form.get('group', None)

    # Initialisiere das Attribut-Wörterbuch
    attributes = {}

    # Rufe die Attributnamen und -werte ab
    attribute_names = request.form.getlist('attribute_name[]')
    attribute_values = request.form.getlist('attribute_value[]')
    display_in_tree_flags = request.form.getlist('display_in_tree[]')

    # Überprüfe, ob Attributnamen doppelt vorkommen
    if len(attribute_names) != len(set(attribute_names)):
        flash("Attributnamen dürfen nicht doppelt vorkommen.", "error")
        return redirect(url_for('index'))

    # Füge Attribute nur hinzu, wenn beide Listen nicht leer sind
    attributes = create_attributes_dict(attribute_names, attribute_values, display_in_tree_flags)

    data = load_data()

    if node_name_exists(data, name):
        flash("Der Knoten Name existiert bereits.", "error")
        return redirect(url_for('index'))

    add_node(data, name, parent_id, probability, color, group, attributes)
    save_data(data)
    flash("Knoten erfolgreich hinzugefügt.", "success")
    return redirect(url_for('index'))


@app.route('/add_edge', methods=['POST'])
def add_edge_route():
    """
    Fügt eine neue Kante basierend auf den Formulardaten hinzu.
    Überprüft, ob die Kante bereits existiert oder ob Parent und Child gleich sind.

    :return: Weiterleitung zur Hauptseite.
    """
    parent_id = request.form['parent']
    child_id = request.form['child']
    probability = request.form['probability']
    color = 'black'  # if request.form['and_or'] == 'and' else 'black'

    data = load_data()

    # Überprüfe, ob Parent und Child Node gleich sind
    if parent_id == child_id:
        flash("Eltern- und Kind Knoten dürfen nicht gleich sein.", "error")
        return redirect(url_for('index'))

    # Überprüfe, ob eine Kante zwischen Parent und Child bereits existiert
    for edge in data['edges']:
        if edge['parent'] == parent_id and edge['child'] == child_id:
            flash("Eine Kante zwischen diesen beiden Knoten existiert bereits.", "error")
            return redirect(url_for('index'))

    # Füge die neue Kante hinzu, falls sie noch nicht existiert
    add_edge(data, parent_id, child_id, probability, color)
    save_data(data)

    flash("Kante erfolgreich hinzugefügt.", "success")
    return redirect(url_for('index'))


@app.route('/get_node_attributes/<node_id>')
def get_node_attributes(node_id):
    """
    Gibt die Attribute eines Knotens basierend auf der Knoten-ID zurück.

    :param node_id: Die ID des Knotens
    :return: JSON-Antwort mit den Attributen des Knotens oder einer Fehlermeldung
    """
    data = load_data()
    for node in data['nodes']:
        if node['id'] == node_id:
            return jsonify({'attributes': node.get('attributes', {})})
    return jsonify({'error': 'Node not found'}), 404


@app.route('/delete_edge', methods=['POST'])
def delete_edge_route():
    """
    Löscht eine Kante basierend auf den Formulardaten.
    Überprüft, ob es eine weitere Kante zum Kindknoten gibt und ob der Kindknoten noch mit einem Elternknoten verbunden ist.

    :return: Weiterleitung zur Hauptseite.
    """
    parent_id = request.form['parent']
    child_id = request.form['child']
    data = load_data()

    # Überprüfe, ob es eine weitere Kante zum Kindknoten gibt
    child_edges = [edge for edge in data['edges'] if edge['child'] == child_id]
    if len(child_edges) <= 1:
        flash("Die Kante kann nicht gelöscht werden, da keine zweite Kante zum Kindknoten existiert.", "error")
        return redirect(url_for('index'))

    # Entferne die Kante
    data['edges'] = [edge for edge in data['edges'] if not (edge['parent'] == parent_id and edge['child'] == child_id)]

    # Überprüfe, ob der Kindknoten noch mit einem Elternknoten verbunden ist
    remaining_edges = [edge for edge in data['edges'] if edge['child'] == child_id]
    if not remaining_edges:
        # Finde einen neuen Elternknoten für den Kindknoten
        new_parent_id = find_new_parent_id(data, child_id)
        if new_parent_id:
            for node in data['nodes']:
                if node['id'] == child_id:
                    node['parent'] = new_parent_id
                    break

    save_data(data)
    flash("Kante erfolgreich gelöscht.", "success")
    return redirect(url_for('index'))


@app.route('/edit_node', methods=['POST'])
def edit_node_route():
    """
    Bearbeitet einen Knoten basierend auf den Formulardaten.
    Überprüft auf doppelte Attributnamen und aktualisiert die Knotenattribute.

    :return: Weiterleitung zur Hauptseite.
    """
    data = load_data()
    node_id = request.form['node_id']
    new_and_or = request.form.get('new_and_or')

    update_node_name(data, node_id, request.form.get('new_name'))
    #update_edge_probability(data, node_id, request.form.get('new_probability'))
    update_edge_color(data, node_id, new_and_or)
    update_node_parent(data, node_id, request.form.get('new_parent'))

    if new_and_or == 'or':
        # Entferne die Gruppe, wenn 'OR' ausgewählt ist
        for node in data['nodes']:
            if node['id'] == node_id:
                node.pop('group', None)
                break
    else:
        update_node_group(data, node_id, request.form.get('new_group'))

    # Rufe Attributnamen, -werte und display_in_tree Flags ab
    attribute_names = request.form.getlist('edit_attribute_name[]')
    attribute_values = request.form.getlist('edit_attribute_value[]')
    display_in_tree_flags = request.form.getlist('display_in_tree[]')

    # Überprüfe, ob Attributnamen doppelt vorkommen
    if len(attribute_names) != len(set(attribute_names)):
        flash("Attributnamen dürfen nicht doppelt vorkommen.", "error")
        return redirect(url_for('index'))

    # Aktualisiere Knotenattribute mit dem neuen Format
    attributes = create_attributes_dict(attribute_names, attribute_values, display_in_tree_flags)

    update_node_attributes(data, node_id, attributes)

    save_data(data)
    flash("Der Knoten wurde erfolgreich bearbeitet.", "success")
    return redirect(url_for('index'))


@app.route('/edit_name/<node_id>', methods=['POST'])
def edit_name_route(node_id):
    """
    Bearbeitet den Namen eines Knotens basierend auf den Formulardaten.
    Lädt die Daten, aktualisiert den Knotennamen und speichert die Änderungen.

    :param node_id: Die ID des Knotens
    :return: Weiterleitung zur Hauptseite
    """
    new_name = request.form['new_name']
    data = load_data()
    edit_node_name(data, node_id, new_name)
    save_data(data)
    return redirect(url_for('index'))


@app.route('/edit_probability/<node_id>', methods=['POST'])
def edit_probability_route(node_id):
    """
    Bearbeitet die Wahrscheinlichkeit einer Kante basierend auf den Formulardaten.
    Lädt die Daten, aktualisiert die Kantenwahrscheinlichkeit und speichert die Änderungen.

    :param node_id: Die ID des Knotens
    :return: Weiterleitung zur Hauptseite
    """
    new_probability = request.form['new_probability']
    data = load_data()
    edit_edge_probability(data, node_id, new_probability)
    save_data(data)
    return redirect(url_for('index'))


@app.route('/edit_and_or/<node_id>', methods=['POST'])
def edit_and_or_route(node_id):
    """
    Bearbeitet die Farbe einer Kante basierend auf den Formulardaten.
    Lädt die Daten, aktualisiert die Kantenfarbe und speichert die Änderungen.

    :param node_id: Die ID des Knotens
    :return: Weiterleitung zur Hauptseite
    """
    new_and_or = request.form['and_or']
    data = load_data()
    edit_edge_color(data, node_id, 'black' if new_and_or == 'and' else 'black')
    save_data(data)
    return redirect(url_for('index'))


@app.route('/edit_parentnode/<node_id>', methods=['POST'])
def edit_parentnode_route(node_id):
    """
    Bearbeitet den Elternknoten eines Knotens basierend auf den Formulardaten.
    Lädt die Daten, aktualisiert den Elternknoten des angegebenen Knotens und speichert die Änderungen.

    :param node_id: Die ID des Knotens
    :return: Weiterleitung zur Hauptseite
    """
    new_parent_id = request.form['parent']
    data = load_data()
    for node in data['nodes']:
        if node['id'] == node_id:
            node['parent'] = new_parent_id
            break
    for edge in data['edges']:
        if edge['child'] == node_id:
            edge['parent'] = new_parent_id
            break
    save_data(data)
    return redirect(url_for('index'))


@app.route('/delete_node', methods=['POST'])
def delete_node_route():
    """
    Löscht einen Knoten basierend auf den Formulardaten.
    Überprüft, ob der Knoten der Root-Knoten ist und weist die Kinderknoten einem neuen Elternknoten zu.

    :return: Weiterleitung zur Hauptseite.
    """
    node_id = request.form['node_id']
    data = load_data()

    # Überprüfe, ob der zu löschende Knoten der Root-Knoten ist
    root_node = next((node for node in data['nodes'] if
                      node['id'] == node_id and not any(edge['child'] == node_id for edge in data['edges'])), None)
    if root_node:
        flash('Der Root Knoten kann nicht gelöscht werden.', 'error')
        return redirect(url_for('index'))

    # Weist die Kinderknoten einem neuen Elternknoten zu
    parent_id = find_new_parent_id(data, node_id)
    for edge in data['edges']:
        if edge['parent'] == node_id:
            edge['parent'] = parent_id

    delete_node(data, node_id)
    save_data(data)
    flash("Der Knoten wurde erfolgreich gelöscht und Kanten wurden aktualisiert.", "success")
    return redirect(url_for('index'))


@app.route('/export_dot', methods=['POST'])
def export_dot():
    """
    Exportiert das Angriffsbaum-Bild in das angegebene Format.
    Lädt die Daten, erstellt das Bild und sendet die Datei als Download.

    :return: Datei-Download der exportierten Angriffsbaum-Bilddatei.
    """
    data = load_data()
    export_format = request.form.get('export_format', 'pdf').lower()
    path = f'export/attack_tree'

    create_attack_tree_image(data['nodes'], data['edges'], file_path=path, format=export_format)

    return send_file(f"export/attack_tree.{export_format}", as_attachment=True,
                     download_name=f'attack_tree.{export_format}',
                     mimetype=f'application/{export_format}')


@app.route('/export_nodes', methods=['GET'])
def export_nodes():
    """
    Exportiert die Knoten und deren Attribute in eine CSV-Datei.

    :return: Datei-Download der exportierten CSV-Datei.
    """
    data = load_data()
    nodes = data['nodes']

    # Erstelle den CSV-Inhalt
    csv_content = "Name,Attribute\n"
    for node in nodes:
        attributes = "; ".join(
            [f"{key}: {value['value']} (Sichtbar im Angriffspfad: {value['display_in_tree']})" for key, value in
             node['attributes'].items()])
        csv_content += f"{node['name']},{attributes}\n"

    # Speichere die CSV-Datei
    csv_path = 'export/nodes_overview.csv'
    with open(csv_path, 'w', encoding='utf-8') as file:
        file.write(csv_content)

    return send_file(csv_path, as_attachment=True, download_name='nodes_overview.csv', mimetype='text/csv')


@app.route('/export_nodes_pdf', methods=['GET'])
def export_nodes_pdf():
    """
    Exportiert die Knoten und deren Attribute in eine PDF-Datei.
    Sendet die PDF-Datei als Download an den Benutzer.

    :return: Datei-Download der exportierten PDF-Datei.
    """
    data = load_data()
    nodes = data['nodes']

    pdf_path = 'export/nodes_overview.pdf'
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title = Paragraph("Knoten Übersicht", styles['Title'])
    elements.append(title)

    table_data = [["Name", "Attribute"]]
    for node in nodes:
        attributes = "<br/>".join([f"{key}: {value['value']}" for key, value in node['attributes'].items()])
        attributes_paragraph = Paragraph(attributes, styles['Normal'])
        table_data.append([Paragraph(node['name'], styles['Normal']), attributes_paragraph])

    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('ALIGN', (0, 1), (0, -1), 'RIGHT'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Füge abwechselnde Zeilenfarben hinzu
    for i in range(1, len(table_data)):
        if i % 2 == 1:
            table.setStyle(TableStyle([('BACKGROUND', (0, i), (-1, i), colors.lightgrey)]))

    elements.append(table)
    doc.build(elements)

    return send_file(pdf_path, as_attachment=True, download_name='nodes_overview.pdf', mimetype='application/pdf')


@app.route('/download_json')
def download_json():
    """
    Lädt die JSON-Datei mit den Angriffsdaten herunter.

    :return: Datei-Download der JSON-Datei.
    """
    output_file = 'config/attack_tree_data.json'
    flash("Die JSON Datei wird heruntergeladen.", "success")
    return send_file(output_file, as_attachment=True, download_name='attack_tree_data.json',
                     mimetype='application/json')


@app.route('/upload_json', methods=['POST'])
def upload_json():
    """
    Lädt eine JSON-Datei hoch und speichert sie.
    Überprüft, ob die Datei gültig ist und erstellt ein Bild basierend auf den Daten.

    :return: Weiterleitung zur Hauptseite.
    """
    if 'file' not in request.files:
        flash('Keine Datei hochgeladen!', 'error')
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        flash('Keine ausgewählte Datei!', 'error')
        return redirect(url_for('index'))

    if file and file.filename.endswith('.json'):
        file_path = os.path.join('config', 'attack_tree_data.json')
        file.save(file_path)

        # Überprüft, ob die JSON-Datei ein Bild generieren kann
        try:
            data = load_data(file_path)
            create_attack_tree_image(data['nodes'], data['edges'])
            flash('JSON-Datei erfolgreich hochgeladen!', 'success')
        except Exception as e:
            flash("Bitte eine gültige JSON-Datei hochladen!", 'error')
            os.remove(file_path)
    else:
        flash('Bitte eine gültige JSON-Datei hochladen!', 'error')

    return redirect(url_for('index'))


@app.route('/view_nodes')
def view_nodes():
    """
    Lädt die Knoten-Daten und rendert die Ansicht der Knoten.
    Lädt die Daten aus der JSON-Datei und extrahiert die Knoten.
    Rendert das Template 'view_nodes.html' mit den Knoten-Daten.

    :return: Das gerenderte Template für die Knoten-Ansicht.
    """
    data = load_data()
    nodes = data['nodes']
    return render_template('view_nodes.html', nodes=nodes)


@app.route('/edit_edge', methods=['POST'])
def edit_edge():
    """
    Bearbeitet die Wahrscheinlichkeit einer Kante basierend auf den Formulardaten.
    Überprüft, ob der neue Wahrscheinlichkeitswert gültig ist und aktualisiert die Kante entsprechend.

    :return: Weiterleitung zur Hauptseite.
    """
    parent_id = request.form['parent']
    child_id = request.form['child']
    new_probability = request.form['probability']
    data = load_data()

    # Überprüft, ob der neue Wahrscheinlichkeitswert eine gültige Zahl ist
    try:
        new_probability_value = float(new_probability.replace(',', '.'))
    except ValueError:
        flash('Die Wahrscheinlichkeit muss einen Zahlenwert sein.', 'error')
        return redirect(url_for('index'))

    # Findet die zu bearbeitende Kante
    edge = next((edge for edge in data['edges'] if edge['parent'] == parent_id and edge['child'] == child_id), None)
    if edge:
        # Überprüft, ob der neue Wahrscheinlichkeitswert gültig ist
        total_probability = sum(
            float(e['probability'].replace(',', '.')) for e in data['edges']
            if e['parent'] == parent_id and e['child'] != child_id
        )
        if total_probability + new_probability_value > 1:
            flash('Die Gesamtwahrscheinlichkeit der Kindknoten darf 1 nicht überschreiten.', 'error')
        else:
            edge['probability'] = new_probability
            save_data(data)
            flash("Die Kante wurde erfolgreich bearbeitet.", "success")
    else:
        flash("Die Kante wurde nicht gefunden.", "error")

    return redirect(url_for('index'))


@app.route('/new_project', methods=['POST'])
def new_project():
    """
    Erstellt ein neues Projekt mit den Anfangsdaten.

    :return: Weiterleitung zur Hauptseite.
    """
    save_data(initial_data)
    flash('Neues Projekt erfolgreich angelegt!', 'success')
    return redirect(url_for('index'))

@app.route('/view_help')
def view_help():
    """
    Öffnet die Benutzerdokumentation in einem neuen Tab

    :return: Das PDF File im Browser
    """
    pdf_path = 'static/Benutzerdokumentation.pdf'
    return send_file(pdf_path, as_attachment=False)


if __name__ == '__main__':
    app.run(debug=False)
