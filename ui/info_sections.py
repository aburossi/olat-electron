import streamlit as st

def display_cost_info():
    with st.expander("ℹ️ Kosteninformationen"):
        st.markdown('''
        <div class="custom-info">
            <ul>
                <li>Die Nutzungskosten hängen von der <strong>Länge der Eingabe</strong> ab (zwischen $0,01 und $0,1).</li>
                <li>Jeder ausgewählte Fragetyp kostet ungefähr $0,01.</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)

def display_question_type_info():
    with st.expander("✅ Fragetypen"):
        st.markdown('''
        <div class="custom-success">
            <strong>Multiple-Choice-Fragen:</strong>
            <ul>
                <li>Alle Multiple-Choice-Fragen haben maximal <strong>3 Punkte</strong>.</li>
                <li><strong>multiple_choice1</strong>: 1 von 4 richtigen Antworten = 3 Punkte</li>
                <li><strong>multiple_choice2</strong>: 2 von 4 richtigen Antworten = 3 Punkte</li>
                <li><strong>multiple_choice3</strong>: 3 von 4 richtigen Antworten = 3 Punkte</li>
            </ul>
            <p>Man kann die Punktzahl der Fragen im Editor später mit Ctrl+H suchen und ersetzen. Achtung: Punktzahl für korrekte Antworten UND maximale Punktzahl anpassen!</p>
        </div>
        ''', unsafe_allow_html=True)
        st.markdown('''
        <div class="custom-success">
            <strong>Inline/FIB-Fragen:</strong>
            <ul>
                <li>Die <strong>Inline</strong>- und <strong>FiB</strong>-Fragen sind inhaltlich identisch.</li>
                <li>FiB = Das fehlende Wort eingeben.</li>
                <li>Inline = Das fehlende Wort auswählen.</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
        st.markdown('''
        <div class="custom-success">
            <strong>Andere Fragetypen:</strong>
            <ul>
                <li><strong>Einzelauswahl</strong>: 4 Antworten, 1 Punkt pro Frage.</li>
                <li><strong>KPRIM</strong>: 4 Antworten, 5 Punkte (4/4 korrekt), 2,5 Punkte (3/4 korrekt), 0 Punkte (50 % oder weniger korrekt).</li>
                <li><strong>Wahr/Falsch</strong>: 3 Antworten, 3 Punkte pro Frage.</li>
                <li><strong>Drag & Drop</strong>: Variable Punkte.</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)

def display_warnings():
    with st.expander("⚠️ Warnungen"):
        st.markdown('''
        <div class="custom-warning">
            <ul>
                <li><strong>Überprüfen Sie immer, ob die Gesamtpunktzahl = Summe der Punkte der richtigen Antworten ist.</strong></li>
                <li><strong>Überprüfen Sie immer den Inhalt der Antworten.</strong></li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)

def display_contact_info():
    with st.expander("📧 Kontaktinformationen"):
        st.markdown('''
        <div class="custom-info">
            <p>Wenn du Fragen oder Verbesserungsideen hast, kannst du mich gerne kontaktieren:</p>
            <ul>
                <li><strong>Pietro Rossi</strong></li>
                <li><strong>E-Mail:</strong> pietro.rossi[at]bbw.ch</li>
            </ul>
            <p>Ich freue mich über dein Feedback!</p>
        </div>
        ''', unsafe_allow_html=True)

def display_all_info_sections():
    """Displays all informational expander sections."""
    display_cost_info()
    display_question_type_info()
    display_warnings()
    display_contact_info()

def apply_custom_css():
    st.markdown(
        """
        <style>
        .custom-info {
            background-color: #e7f3fe;
            padding: 10px;
            border-radius: 5px;
            border-left: 6px solid #2196F3;
        }
        .custom-success {
            background-color: #d4edda;
            padding: 10px;
            border-radius: 5px;
            border-left: 6px solid #28a745;
        }
        .custom-warning {
            background-color: #fff3cd;
            padding: 10px;
            border-radius: 5px;
            border-left: 6px solid #ffc107;
        }
        </style>
        """, unsafe_allow_html=True
    )