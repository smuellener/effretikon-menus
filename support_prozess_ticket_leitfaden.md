# Support-Prozess – Ticket-Erstellungs-Leitfaden

**SIUS | Interner & Externer Support-Prozess**

---

## Grundsatz

Ein Ticket wird **manuell** erstellt – es gibt keine automatische Ticketerstellung.

**Zwei parallele Pfade – Chat und Ticket:**

| Pfad | Beschreibung |
|------|--------------|
| **Chat-Pfad** | Anfrage im First Level Chat → Second Level Chat → Important Announcement |
| **🎫 Ticket-Pfad** | Ticket ab First Level erstellen, kann direkt zu Second Level (First Level überspringen); Tickets landen im Second Level Chat |

**Competition Support:** Ausnahme – immer nur Chat, kein Ticket-Pfad.

> **Leitsatz:** Wenn eine hohe Eskalationsstufe erreicht wird, soll möglichst ein Ticket resultieren – entweder zur **technischen Lösung** oder zur **Verbesserung von Kommunikation und Schulung**, damit die Eskalation künftig vermieden wird.

---

## Wann wird ein Ticket erstellt?

| Situation | Ticket erstellen? | Ticket-Typ |
|-----------|:-----------------:|------------|
| **Externe Anfrage (generell)** | ✅ Empfohlen – so früh wie möglich | Anfrage-Ticket → ggf. Bug/Verbesserung |
| Technischer Fehler identifiziert (Bug, Fehlfunktion) | ✅ Ja | Fehler-Ticket |
| Wiederkehrendes Problem, das auf Wissenslücke hindeutet | ✅ Ja | Verbesserungs-Ticket |
| Einmaliges, gelöstes Problem ohne Muster | ❌ Nein | – |
| Wichtige Information wurde kommuniziert, kein Handlungsbedarf | ❌ Nein | – |

---

## Ticket-Typen

### 🐛 Typ 1: Fehler-Ticket

**Zweck:** Einen technischen Fehler beheben.

**Typische Inhalte:**
- Beschreibung des Fehlers / Fehlverhaltens
- Schritte zur Reproduktion
- Betroffene Komponenten / Systeme
- Priorität (kritisch / hoch / mittel / niedrig)
- Zuständige Person / Team (i.d.R. Entwicklung)

**Beispiel:**  
> „Während des Wettkampfs XY hat das System Z bei Aktion A einen Fehler gezeigt. Das Problem trat 3-mal auf. Entwicklung soll Ursache identifizieren und beheben."

---

### 📚 Typ 2: Verbesserungs-Ticket

**Zweck:** Kommunikation, Schulung oder Dokumentation verbessern, damit eine ähnliche Eskalation künftig vermieden wird.

**Typische Inhalte:**
- Beschreibung des zugrundeliegenden Problems
- Warum wurde eskaliert? (Was war unklar / unbekannt?)
- Vorgeschlagene Maßnahme: Schulung / FAQ-Dokument / Kommunikation anpassen
- Zuständige Person / Team

**Beispiel:**  
> „Support hat Frage X mehrfach nicht lösen können. Das Thema scheint unbekannt zu sein. Vorschlag: Schulung für Support-Team oder Erstellung einer Dokumentation / FAQ."

---

## Ticket-Erstellungsprozess – Interner Prozess

```
1. Problem wurde im Important Announcement kommuniziert
        |
        v
2. Teilnehmende Person entscheidet: Ticket notwendig?
        |
       JA
        |
        v
3. Ticket-Typ bestimmen:
   - Fehler?     → Fehler-Ticket
   - Wissenslücke / Kommunikation? → Verbesserungs-Ticket
        |
        v
4. Ticket erstellen mit:
   - Titel (präzise und verständlich)
   - Beschreibung (Was ist passiert? Kontext?)
   - Typ (Fehler / Verbesserung)
   - Priorität
   - Zuständige Person / Team
        |
        v
5. Ticket kommunizieren im entsprechenden Kanal
        |
        v
6. Zuständige Person nimmt Ticket an und bearbeitet es
        |
        v
7. Ticket abschließen mit Kurzdokumentation der Lösung / Maßnahme
```

---

## Ticket-Erstellungsprozess – Externer Prozess

```
1. Externe Anfrage eingehend (Email / Telefon)
        |
        v
2. Ticket erstellen – so früh wie möglich (Empfehlung)
        |
        v
3. Support bearbeitet Anfrage
        |
       Nicht lösbar?
        |
        v
4. Eskalation:
   Bevorzugt: Ticket an Second Level weiterleiten
   Alternativ: Direkt im Second Level Support Chat melden
        |
        v
5. Second Level bearbeitet Ticket
        |
       Weiterhin kritisch?
        |
        v
6. Important Announcement + Externe Benachrichtigung
   (Newsletter / KAM proaktiv)
        |
        v
7. Ticket abschließen mit Lösung / Maßnahme
```

---

## Prioritäten

| Priorität | Beschreibung | Beispiel |
|-----------|--------------|---------|
| **Kritisch** | System ausgefallen, Wettkampf nicht möglich | Server-Ausfall während Event |
| **Hoch** | Wichtige Funktion beeinträchtigt, Workaround nötig | Eingabemasken fehlerhaft |
| **Mittel** | Problem besteht, hat aber Workaround | Kleinere Anzeigeprobleme |
| **Niedrig** | Verbesserungsvorschlag, kein akuter Handlungsbedarf | Dokumentation ergänzen |

---

## Hinweise

- **Externe Anfragen – Tickets bevorzugt**: Für externe Anfragen soll wenn immer möglich ein Ticket erstellt werden. Dies schafft Nachvollziehbarkeit und ermöglicht saubere Eskalation per Ticket-Weiterleitung.
- **Qualität über Quantität**: Nicht jedes Problem braucht ein Ticket. Der Fokus liegt auf Problemen mit Musterpotenzial oder kritischen Fehlern.
- **Kurze Titel, klare Beschreibung**: Ein Ticket sollte von einer fremden Person ohne Kontext verstanden werden können.
- **Nachverfolgung**: Erstellte Tickets sollten in einem regelmäßigen Rhythmus reviewed werden, um sicherzustellen, dass sie nicht liegen bleiben.
