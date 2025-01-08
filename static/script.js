function showSection(sectionId) {
    /**
     * Zeigt den angegebenen Abschnitt an und speichert die Auswahl im lokalen Speicher.
     * Entfernt die Klasse 'active' von allen anderen Abschnitten außer 'attack-tree-section'.
     * Fügt die Klasse 'active' zum angegebenen Abschnitt hinzu.

     * @param {string} sectionId - Die ID des anzuzeigenden Abschnitts.
     */
    // Alle Abschnitte mit der Klasse 'section' auswählen
    const sections = document.querySelectorAll('.section');
    // Für jeden Abschnitt prüfen
    sections.forEach(section => {
        // Wenn der Abschnitt nicht der 'attack-tree-section' ist
        if (section.id !== 'attack-tree-section') {
            // Entferne die Klasse 'active' vom Abschnitt
            section.classList.remove('active');
        }
    });
    // Füge die Klasse 'active' zum angegebenen Abschnitt hinzu
    document.getElementById(sectionId).classList.add('active');
    // Speichere die Auswahl im lokalen Speicher
    localStorage.setItem('selectedSection', sectionId);
}

function confirmUpload() {
    /**
     * Zeigt eine Bestätigungsnachricht an und gibt das Ergebnis zurück.
     * Warnt den Benutzer, dass das aktuelle Projekt überschrieben wird.

     * @return {boolean} - True, wenn der Benutzer fortfahren möchte, sonst False.
     */
    // Zeigt eine Bestätigungsnachricht an und gibt das Ergebnis zurück
    return confirm("Achtung: Das aktuelle Projekt wird überschrieben! Möchten Sie fortfahren?");
}


document.addEventListener('DOMContentLoaded', () => {
    /**
     * Führt Aktionen aus, wenn das Dokument vollständig geladen ist.
     * Zeigt den ausgewählten Abschnitt an und fügt Klick-Event-Listener zu allen Elementen mit der Klasse 'collapsible' hinzu.
     * Speichert die Auswahl des Abschnitts im lokalen Speicher.

     */
    // Hole den ausgewählten Abschnitt aus dem lokalen Speicher
    const selectedSection = localStorage.getItem('selectedSection');
    // Wenn ein Abschnitt ausgewählt wurde, zeige diesen Abschnitt an
    if (selectedSection) {
        showSection(selectedSection);
    } else {
        // Andernfalls zeige den Standardabschnitt an
        showSection('root-node-section');
    }

    // Alle Elemente mit der Klasse 'collapsible' auswählen
    const coll = document.getElementsByClassName("collapsible");
    // Für jedes dieser Elemente einen Klick-Event-Listener hinzufügen
    for (let i = 0; i < coll.length; i++) {
        coll[i].addEventListener("click", function () {
            // Toggle die Klasse 'active' für das geklickte Element
            this.classList.toggle("active");
            // Wähle das nächste Geschwisterelement
            const content = this.nextElementSibling;
            // Wenn das Geschwisterelement angezeigt wird, verstecke es
            if (content.style.display === "block") {
                content.style.display = "none";
            } else {
                // Andernfalls zeige es an
                content.style.display = "block";
            }
        });
    }
});


function loadNodeAttributes(nodeId) {
    /**
     * Lädt die Attribute eines Knotens vom Server und fügt sie dem Bearbeitungsformular hinzu.
     * Löscht vorhandene Attribute im Formular und fügt die neuen Attribute hinzu.
     *
     * @param {string} nodeId - Die ID des Knotens, dessen Attribute geladen werden sollen.
     */
    // Hole die Attribute des Knotens vom Server
    fetch(`/get_node_attributes/${nodeId}`)
        .then(response => response.json())
        .then(data => {
            // Wähle den Container für die Attribute
            const container = document.getElementById('attributes-container');
            // Lösche vorhandene Attribute
            container.innerHTML = '';
            // Wenn Attribute vorhanden sind, füge sie dem Container hinzu
            if (data.attributes) {
                for (const [name, attribute] of Object.entries(data.attributes)) {
                    const div = document.createElement('div');
                    div.className = 'attribute-pair';
                    div.innerHTML = `
                        <input type="text" name="edit_attribute_name[]" value="${name}" placeholder="Attribut Name">
                        <input type="text" name="edit_attribute_value[]" value="${attribute.value}" placeholder="Attribut Wert">
                        <select name="display_in_tree[]">
                            <option value="true" ${attribute.display_in_tree === 'true' ? 'selected' : ''}>Anzeigen</option>
                            <option value="false" ${attribute.display_in_tree === 'false' ? 'selected' : ''}>Verbergen</option>
                        </select>
                    `;
                    container.appendChild(div);
                }
            } else {
                // Wenn ein Fehler auftritt, zeige ihn in der Konsole an
                console.error('Error loading attributes:', data.error);
            }
        });
}

function addEditAttribute(name = '', value = '') {
    /**
     * Fügt ein Attributpaar (Name und Wert) zum Bearbeitungsformular hinzu.
     * Erstellt Eingabefelder für den Attributnamen und -wert sowie eine Löschen-Schaltfläche.
     * Fügt das Attributpaar dem Container für die zu bearbeitenden Attribute hinzu.
     *
     * @param {string} name - Der Name des Attributs (optional).
     * @param {string} value - Der Wert des Attributs (optional).
     */
    // Wähle den Container für die zu bearbeitenden Attribute
    const container = document.getElementById('edit-attributes-container');
    // Erstelle ein neues Attributpaar-Div
    const attributeDiv = document.createElement('div');
    attributeDiv.classList.add('attribute-pair');

    // Erstelle das Eingabefeld für den Attributnamen
    const nameInput = document.createElement('input');
    nameInput.type = 'text';
    nameInput.name = 'edit_attribute_name[]';
    nameInput.placeholder = 'Attribut Name';
    nameInput.value = name;

    // Erstelle das Eingabefeld für den Attributwert
    const valueInput = document.createElement('input');
    valueInput.type = 'text';
    valueInput.name = 'edit_attribute_value[]';
    valueInput.placeholder = 'Attribut Wert';
    valueInput.value = value;

    // Erstelle die Löschen-Schaltfläche
    const deleteButton = document.createElement('button');
    deleteButton.type = 'button';
    deleteButton.textContent = 'Löschen';
    // Füge einen Klick-Event-Listener hinzu, um das Attributpaar zu entfernen
    deleteButton.onclick = () => container.removeChild(attributeDiv);

    // Füge die Eingabefelder und die Schaltfläche dem Attributpaar-Div hinzu
    attributeDiv.appendChild(nameInput);
    attributeDiv.appendChild(valueInput);
    attributeDiv.appendChild(deleteButton);
    // Füge das Attributpaar-Div dem Container hinzu
    container.appendChild(attributeDiv);
}

function validateEditForm() {
    /**
     * Validiert das Bearbeitungsformular, um sicherzustellen, dass eine Gruppe angegeben wird, wenn "AND" ausgewählt ist.
     * Zeigt eine Warnung an, wenn "AND" ausgewählt ist und das Gruppen-Eingabefeld leer ist.
     * Gibt false zurück, wenn die Validierung fehlschlägt, sonst true.
     */
    // Wähle das "AND"-Radio-Button und das Gruppen-Eingabefeld
    const andRadio = document.getElementById('and');
    const groupInput = document.querySelector('input[name="new_group"]');

    // Wenn "AND" ausgewählt ist und das Gruppen-Eingabefeld leer ist, zeige eine Warnung an
    if (andRadio.checked && !groupInput.value.trim()) {
        alert('Bitte geben Sie eine Gruppe an, wenn "AND" ausgewählt ist.');
        return false;
    }
    return true;
}

function toggleGroupInput() {
    /**
     * Schaltet das Gruppen-Eingabefeld basierend auf der Auswahl von "AND" oder "OR" um.
     * Aktiviert oder deaktiviert das Eingabefeld für Gruppen, je nachdem, ob "AND" oder "OR" ausgewählt ist.
     * Fügt Event-Listener hinzu, um das Verhalten bei Änderungen der Auswahl zu steuern.
     */
    // Wähle die "AND"- und "OR"-Radio-Buttons und das Gruppen-Eingabefeld für das Hinzufügen
    const andRadioAdd = document.getElementById('and_add');
    const groupInputAdd = document.querySelector('input[name="group"]');
    const orRadioAdd = document.getElementById('or_add');

    // Wähle die "AND"- und "OR"-Radio-Buttons und das Gruppen-Eingabefeld für das Bearbeiten
    const andRadioEdit = document.getElementById('and');
    const groupInputEdit = document.querySelector('input[name="new_group"]');
    const orRadioEdit = document.getElementById('or');

    // Wenn die Elemente für das Hinzufügen vorhanden sind, schalte das Gruppen-Eingabefeld um
    if (andRadioAdd && groupInputAdd && orRadioAdd) {
        groupInputAdd.disabled = !andRadioAdd.checked;
        andRadioAdd.addEventListener('change', function () {
            groupInputAdd.disabled = !this.checked;
        });
        orRadioAdd.addEventListener('change', function () {
            groupInputAdd.disabled = this.checked;
        });
    }

    // Wenn die Elemente für das Bearbeiten vorhanden sind, schalte das Gruppen-Eingabefeld um
    if (andRadioEdit && groupInputEdit && orRadioEdit) {
        groupInputEdit.disabled = !andRadioEdit.checked;
        andRadioEdit.addEventListener('change', function () {
            groupInputEdit.disabled = !this.checked;
        });
        orRadioEdit.addEventListener('change', function () {
            groupInputEdit.disabled = this.checked;
        });
    }
}


document.addEventListener('DOMContentLoaded', function () {
    /**
     * Ruft die Funktion `toggleGroupInput` auf, um das Gruppen-Eingabefeld basierend auf der Auswahl umzuschalten.
     */
    // Rufe die Funktion auf, um das Gruppen-Eingabefeld umzuschalten
    toggleGroupInput();
});

function addAttributeField() {
    /**
     * Fügt ein neues Attributpaar (Name und Wert) zum Bearbeitungsformular hinzu.
     * Erstellt Eingabefelder für den Attributnamen und -wert sowie ein Dropdown-Menü zur Anzeigeoption.
     * Fügt das Attributpaar dem Container für die Attribute hinzu.
     */
    // Wähle den Container für die Attribute
    const container = document.getElementById('attributes-container');
    // Erstelle ein neues Attributpaar-Div
    const attributePair = document.createElement('div');
    attributePair.className = 'attribute-pair';
    // Füge die Eingabefelder und das Dropdown-Menü für das Attributpaar hinzu
    attributePair.innerHTML = `
        <input type="text" name="edit_attribute_name[]" placeholder="Attribut Name">
        <input type="text" name="edit_attribute_value[]" placeholder="Attribut Wert">
        <select name="display_in_tree[]">
            <option value="false">Verbergen</option>
            <option value="true">Anzeigen</option>
        </select>
    `;
    // Füge das Attributpaar-Div dem Container hinzu
    container.appendChild(attributePair);
}

// Fügt ein Attributfeld zum Hinzufügen von Attributen hinzu
function addAttribute() {
    /**
     * Fügt ein neues Attributpaar (Name und Wert) zum Formular hinzu.
     * Erstellt Eingabefelder für den Attributnamen und -wert sowie ein Dropdown-Menü zur Anzeigeoption.
     * Fügt das Attributpaar dem Container für die hinzuzufügenden Attribute hinzu.
     */
    // Wähle den Container für die hinzuzufügenden Attribute
    const container = document.getElementById('add-attributes-container');
    // Erstelle ein neues Attributpaar-Div
    const attributePair = document.createElement('div');
    attributePair.className = 'attribute-pair';
    // Füge die Eingabefelder und das Dropdown-Menü für das Attributpaar hinzu
    attributePair.innerHTML = `
        <input type="text" name="attribute_name[]" placeholder="Attribut Name">
        <input type="text" name="attribute_value[]" placeholder="Attribut Wert">
        <select name="display_in_tree[]">
            <option value="false">Verbergen</option>
            <option value="true">Anzeigen</option>
        </select>
    `;
    // Füge das Attributpaar-Div dem Container hinzu
    container.appendChild(attributePair);
}

document.addEventListener('DOMContentLoaded', function() {
    /**
     * Fügt eine Fortschrittsleiste zu Nachrichten hinzu, wenn das Dokument vollständig geladen ist.
     * Überspringt Info-Nachrichten und setzt die Farbe der Fortschrittsleiste basierend auf der Kategorie.
     * Reduziert die Breite der Fortschrittsleiste schrittweise und blendet die Nachricht aus, wenn die Breite 0 erreicht.
     */
    // Wähle das Nachrichten-Element
    const messages = document.getElementById('messages');
    // Wenn Nachrichten vorhanden sind, füge für jede Nachricht eine Fortschrittsleiste hinzu
    if (messages) {
        const messageItems = messages.getElementsByTagName('li');
        for (let i = 0; i < messageItems.length; i++) {
            const category = messageItems[i].getAttribute('data-category');

            // Überspringe die Fortschrittsleiste für Info-Nachrichten
            if (category === 'info') {
                continue;
            }

            const progressBar = document.createElement('div');
            progressBar.id = 'progress-bar';
            messageItems[i].appendChild(progressBar);

            // Setze die Farbe basierend auf der Kategorie
            switch (category) {
                case 'error':
                    progressBar.style.backgroundColor = 'red';
                    break;
                case 'success':
                    progressBar.style.backgroundColor = 'green';
                    break;
                default:
                    progressBar.style.backgroundColor = 'gray';
            }

            // Starte die Fortschrittsleiste für Fehler- und Erfolgsmeldungen
            let width = 100;
            const interval = setInterval(function() {
                width -= 2;
                progressBar.style.width = width + '%';
                if (width <= 0) {
                    clearInterval(interval);
                    messageItems[i].style.display = 'none';
                }
            }, 100);
        }
    }
});

function confirmNewProject() {
    /**
     * Zeigt eine Bestätigungsnachricht an und gibt das Ergebnis zurück.
     * Warnt den Benutzer, dass das aktuelle Projekt überschrieben wird.
     * Gibt true zurück, wenn der Benutzer fortfahren möchte, sonst false.
     */
    // Zeigt eine Bestätigungsnachricht an und gibt das Ergebnis zurück
    return confirm("Das aktuelle Projekt wird überschrieben. Möchten Sie fortfahren?");
}


document.addEventListener('DOMContentLoaded', function() {
    /**
     * Initialisiert den Kippschalter für Info-Nachrichten und stellt den gespeicherten Zustand wieder her.
     * Fügt einen Event-Listener hinzu, um den Zustand des Kippschalters zu speichern und die Anzeige von Info-Nachrichten umzuschalten.
     */
    // Wähle den Kippschalter für Info-Nachrichten
    const toggleSwitch = document.getElementById('toggle-info-messages');

    // Lade den gespeicherten Zustand aus dem lokalen Speicher
    const savedState = localStorage.getItem('toggleInfoMessages');
    if (savedState !== null) {
        toggleSwitch.checked = JSON.parse(savedState);
        toggleInfoMessages(toggleSwitch.checked);
    }

    // Füge einen Event-Listener hinzu, um den Zustand des Kippschalters zu speichern
    toggleSwitch.addEventListener('change', function() {
        const isChecked = toggleSwitch.checked;
        localStorage.setItem('toggleInfoMessages', JSON.stringify(isChecked));
        toggleInfoMessages(isChecked);
    });

    // Funktion zum Umschalten der Anzeige von Info-Nachrichten
    function toggleInfoMessages(isChecked) {
        const infoMessages = document.querySelectorAll('#messages .info');
        infoMessages.forEach(function(message) {
            message.style.display = isChecked ? 'list-item' : 'none';
        });
    }

    // Wende den gespeicherten Zustand an, wenn der Seiteninhalt aktualisiert wird
    const observer = new MutationObserver(function() {
        const savedState = localStorage.getItem('toggleInfoMessages');
        if (savedState !== null) {
            toggleSwitch.checked = JSON.parse(savedState);
            toggleInfoMessages(toggleSwitch.checked);
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });
});

document.addEventListener('DOMContentLoaded', () => {
    /**
     * Passt die Höhe des Abschnitts basierend auf der Bildhöhe an.
     * Beobachtet Änderungen der Bildquelle und passt die Höhe entsprechend an.
     * Justiert die Containergröße basierend auf den Dimensionen des Bildes und der Überschrift.
     */
    // Wähle das Bild und den Abschnitt
    const img = document.getElementById('attack-tree-img');
    const section = document.getElementById('attack-tree-section');

    // Funktion zur Anpassung der Abschnittshöhe basierend auf der Bildhöhe
    function adjustSectionHeight() {
        section.style.height = img.clientHeight + 'px';
    }

    // Passe die Höhe an, wenn das Bild geladen wird
    img.onload = adjustSectionHeight;

    // Passe die Höhe an, wenn sich die Bildquelle ändert
    const observer = new MutationObserver(adjustSectionHeight);
    observer.observe(img, { attributes: true, attributeFilter: ['src'] });

    window.addEventListener('load', function() {
        var attackTreeSection = document.getElementById('attack-tree-section');
        var img = attackTreeSection.querySelector('img');
        var heading = attackTreeSection.querySelector('h2');

        // Passe die Containergröße basierend auf den Dimensionen des Bildes und der Überschrift an
        attackTreeSection.style.height = (img.offsetHeight + heading.offsetHeight + 40) + 'px';
    });
});

