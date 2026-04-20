# Support-Prozess – Flussdiagramm

**SIUS | Interner & Externer Support-Prozess**  
Gültig für: Alle internen Mitarbeiter (@sius.com) sowie externe Kunden und Vertriebspartner

---

## Interner Prozess

Zwei parallele Pfade: **Chat-Pfad** (blau/orange) und **Ticket-Pfad** (grün). Beide konvergieren im Second Level Support Chat.

```mermaid
flowchart TD
    A([📩 Interne Supportanfrage\n@sius.com Mitarbeiter]) --> B{Wettkampf\nläuft aktuell\nODER hohe\nDringlichkeit?}

    B -- JA --> C[🏆 Competition Support CHAT\nTEC · SUP · WET · ENT\nNur Chat – kein Ticket-Pfad]
    B -- NEIN --> SPLIT{Pfad wählen}

    SPLIT -- Chat-Pfad --> D[🔵 First Level Support CHAT\nTEC · SUP · WET]
    SPLIT -- "Ticket-Pfad\n(parallel möglich)" --> T1[🎫 Ticket erstellen\nFirst Level]

    C --> E{Problem\ngelöst?}
    E -- JA --> Z1([✅ Abgeschlossen])
    E -- NEIN --> F{Großes Problem?}
    F -- JA --> I
    F -- NEIN --> G

    D --> H{Problem\ngelöst?}
    H -- JA --> Z2([✅ Abgeschlossen])
    H -- NEIN --> G

    T1 -- "Direkt zu\nSecond Level\nmöglich" --> G
    T1 -- "Erst First Level\nbearbeiten" --> D

    G[🟠 Second Level Support CHAT\nSUP · TEC · WET · ENT · ± PL · ± KAM\nChat + Tickets werden hier besprochen]

    G --> J{Problem gelöst\nODER großes Problem?}
    J -- Gelöst --> Z3([✅ Abgeschlossen])
    J -- Großes Problem --> I

    I[🔴 Important Announcement\nTEC · SUP · WET · ENT · PL · KAM · GL]

    I --> K{Ticket\nerstellen?}
    K -- NEIN --> Z4([✅ Info kommuniziert\nKAM informiert Key Accounts proaktiv])
    K -- JA --> L{Ticket-Typ?}

    L -- Fehler --> M[🐛 Bug-/Fehler-Ticket]
    L -- Wissen/Schulung --> N[📚 Verbesserungs-Ticket]

    M --> Z5([✅ Ticket in Bearbeitung])
    N --> Z5
```

---

## Externer Prozess

Zwei parallele Pfade: **Chat/Email-Pfad** und **Ticket-Pfad**. Beide konvergieren im Second Level Support Chat.

```mermaid
flowchart TD
    EXT([🌐 Externe Supportanfrage\nKunde / Vertriebspartner])

    EXT --> EMAIL["✉ Email an support@sius.com\nbevorzugter Kontaktweg"]
    EXT --> TEL["📞 Support-Telefon\nzu Bürozeiten"]

    EMAIL --> SPLIT2{Pfad wählen}
    TEL --> SPLIT2

    SPLIT2 -- "Chat-Pfad\n(ohne Ticket)" --> SA
    SPLIT2 -- "Ticket-Pfad\n(empfohlen)" --> CT[🎫 Ticket erstellen\nExt. First Level]

    CT -- "Direkt zu\nSecond Level\nmöglich" --> SL
    CT -- "First Level\nbearbeitet" --> SA

    SA{Support kann\nantworten?}
    SA -- JA --> EZ1([✅ Abgeschlossen])
    SA -- NEIN --> SL

    SL[🟠 Second Level Support CHAT\nSUP · TEC · WET · ENT · ± PL · ± KAM\nChat + Tickets werden hier besprochen]

    SL --> SLR{Problem gelöst\nODER großes Problem?}
    SLR -- Gelöst --> EZ2([✅ Abgeschlossen])
    SLR -- Großes Problem --> IA

    IA[🔴 Important Announcement\nTEC · SUP · WET · ENT · PL · KAM · GL]

    IA --> NOT[📢 Externe Benachrichtigung]
    NOT --> NL["📰 Public Newsletter\nfür alle Kunden – Holschuld"]
    NOT --> KAM["🤝 KAM proaktiv\nPolytronic · Meyton · Holybrother u.a."]

    IA --> IK{Ticket\nerstellen?}
    IK -- JA --> IT["🐛 Bug-Ticket / 📚 Verbesserungs-Ticket"]
    IK -- NEIN --> EZ3([✅ Info verteilt])
    IT --> EZ4([✅ Ticket in Bearbeitung])
```

---

## Legende

| Symbol | Bedeutung |
|--------|-----------|
| 🏆 | Competition Support – sofortige Eskalation bei Wettkampf |
| 🔵 | First Level Support – Erstanlaufstelle intern |
| ✉ / 📞 | Ext. First Level – Email (bevorzugt) oder Telefon zu Bürozeiten |
| 🟠 | Second Level Support – geteilt zwischen intern & extern |
| 🔴 | Important Announcement – höchste interne Eskalationsstufe |
| 📰 | Public Newsletter – externe Benachrichtigung (Holschuld) |
| 🤝 | KAM proaktiv – Benachrichtigung für Key Accounts |
| ✅ | Prozess abgeschlossen |
| 🐛 | Fehler-Ticket |
| 📚 | Verbesserungs-/Schulungsticket |
| 🎫 | Ticket-Pfad – parallel zum Chat, ab First Level möglich, direkt zu Second Level eskalierbar |

---

## Rollen-Kürzel

| Kürzel | Rolle |
|--------|-------|
| TEC | Techniker |
| SUP | Support |
| WET | Wettkampf |
| ENT | Entwickler |
| PL | Projektleiter |
| KAM | Key Account Manager |
| GL | Geschäftsleitung |
