# Support-Prozess – Eskalationsübersicht

**SIUS | Interner & Externer Support-Prozess**  
Je höher die Stufe, desto höher die Eskalation.

---

## Interner Prozess

```mermaid
flowchart BT

    classDef l0 fill:#7B2D8B,color:#fff,stroke:#5a1f6e,font-size:14px
    classDef l1 fill:#1565C0,color:#fff,stroke:#0d47a1,font-size:14px
    classDef l2 fill:#E65100,color:#fff,stroke:#bf360c,font-size:14px
    classDef l3 fill:#B71C1C,color:#fff,stroke:#7f0000,font-size:14px
    classDef ticket fill:#2E7D32,color:#fff,stroke:#1b5e20,font-size:13px
    classDef ticketpath fill:#388E3C,color:#fff,stroke:#1b5e20,font-size:13px

    RESTICKET["🎫 TICKET RESULT\nFehler-Ticket  |  Verbesserungs-Ticket"]:::ticket

    IA["🔴 IMPORTANT ANNOUNCEMENT  ·  Stufe 3\n─────────────────────────────────────\nTEC  ·  SUP  ·  WET  ·  ENT  ·  PL  ·  KAM  ·  GL\n─────────────────────────────────────\nAlle Schlüsselpersonen · Kritische Meldungen"]:::l3

    L2["🟠 SECOND LEVEL SUPPORT CHAT  ·  Stufe 2\n─────────────────────────────────────\nSUP  ·  TEC  ·  WET  ·  ENT  ·  (PL)  ·  (KAM)\n─────────────────────────────────────\nChat + Tickets werden hier besprochen"]:::l2

    T1["🎫 TICKET-PFAD  ·  ab Stufe 1\n─────────────────────────────────────\nTicket erstellen (parallel zum Chat)\nKann First Level Chat überspringen\nund direkt zu Second Level"]:::ticketpath

    L1["🔵 FIRST LEVEL SUPPORT CHAT  ·  Stufe 1\n─────────────────────────────────────\nTEC  ·  SUP  ·  WET\n─────────────────────────────────────\nErstanlaufstelle · parallel Ticket möglich"]:::l1

    CS["🏆 COMPETITION SUPPORT  ·  Stufe 0\n─────────────────────────────────────\nTEC  ·  SUP  ·  WET  ·  ENT\n─────────────────────────────────────\nWettkampf läuft ODER hohe Dringlichkeit\nNur Chat – kein Ticket-Pfad"]:::l0

    L1 -->|"Nicht gelöst"| L2
    T1 -->|"Direkt zu\nSecond Level"| L2
    L2 -->|"Nicht gelöst\noder grosses Problem"| IA
    CS -->|"Kritisches Problem\nbleibt ungelöst"| IA
    IA -->|"Ticket notwendig\n(manuell)"| RESTICKET
```

---

## Externer Prozess

```mermaid
flowchart BT

    classDef ext1 fill:#00695C,color:#fff,stroke:#004D40,font-size:14px
    classDef l2 fill:#E65100,color:#fff,stroke:#bf360c,font-size:14px
    classDef l3 fill:#B71C1C,color:#fff,stroke:#7f0000,font-size:14px
    classDef notif fill:#1A237E,color:#fff,stroke:#0D1B7A,font-size:13px
    classDef ticket fill:#2E7D32,color:#fff,stroke:#1b5e20,font-size:13px
    classDef ticketpath fill:#388E3C,color:#fff,stroke:#1b5e20,font-size:13px

    TICKET["🎫 TICKET RESULT\nFehler-Ticket  |  Verbesserungs-Ticket"]:::ticket

    NOTIF["📢 EXTERNE BENACHRICHTIGUNG\n─────────────────────────────────────\n📰 Public Newsletter (Holschuld, alle Kunden)\n🤝 KAM proaktiv (Polytronic · Meyton · Holybrother u.a.)"]:::notif

    IA["🔴 IMPORTANT ANNOUNCEMENT  ·  Ext. Stufe 3\n─────────────────────────────────────\nTEC  ·  SUP  ·  WET  ·  ENT  ·  PL  ·  KAM  ·  GL\n─────────────────────────────────────\nGleicher Kanal wie interner Prozess"]:::l3

    L2["🟠 SECOND LEVEL SUPPORT CHAT  ·  Ext. Stufe 2\n─────────────────────────────────────\nSUP  ·  TEC  ·  WET  ·  ENT  ·  (PL)  ·  (KAM)\n─────────────────────────────────────\nGleicher Kanal wie interner Prozess\nChat + Tickets werden hier besprochen"]:::l2

    ET1["🎫 TICKET-PFAD  ·  ab Ext. Stufe 1\n─────────────────────────────────────\nTicket erstellen (empfohlen)\nKann Ext. First Level überspringen\nund direkt zu Second Level"]:::ticketpath

    EFL["✉ EXT. FIRST LEVEL  ·  Ext. Stufe 1\n─────────────────────────────────────\nEmail: support@sius.com (bevorzugt)\nTelefon zu Bürozeiten\n─────────────────────────────────────\nParallel Ticket erstellen – empfohlen"]:::ext1

    EFL -->|"Nicht lösbar"| L2
    ET1 -->|"Direkt zu\nSecond Level"| L2
    L2 -->|"Grosses Problem"| IA
    IA -->|"Ticket notwendig\n(manuell)"| TICKET
    IA -->|"Externe Mitteilung"| NOTIF
```

---

## Legende

| Farbe | Stufe | Kanal / Pfad |
|-------|-------|-------|
| 🟣 Lila | Stufe 0 | Competition Support – nur Chat |
| 🔵 Blau | Stufe 1 | First Level Support Chat (intern) |
| 🟢 Dunkelgrün | Ext. Stufe 1 | Ext. First Level – Email / Telefon (extern) |
| 🟩 Grün (heller) | ab Stufe 1 | **Ticket-Pfad** – parallel zum Chat, kann First Level überspringen |
| 🟠 Orange | Stufe 2 | Second Level Support Chat (intern & extern – Chat + Tickets) |
| 🔴 Rot | Stufe 3 | Important Announcement (intern & extern geteilt) |
| 🔷 Dunkelblau | – | Externe Benachrichtigung (Newsletter / KAM) |
| 🟢 Dunkelgrün | – | Ticket-Ergebnis (Massnahme nach Important Announcement) |

---

## Schnellübersicht: Chat-Pfad & Ticket-Pfad im Vergleich

```
▲  höchste Eskalation
│
│  ┌──────────────────────────────────────────────────────────────────┐
│  │  🔴  IMPORTANT ANNOUNCEMENT  (Stufe 3 – intern & extern)        │
│  │  TEC · SUP · WET · ENT · PL · KAM · GL                          │
│  │  ──────────────────────────────────────────────────────────────  │
│  │  Intern: Kanal-Meldung    │  Extern: Newsletter + KAM proaktiv  │
│  └──────────────────────────────────────────────────────────────────┘
│            ▲                              ▲
│            │ nicht gelöst /               │ nicht gelöst /
│            │ grosses Problem              │ grosses Problem
│  ┌──────────────────────────────────────────────────────────────────┐
│  │  🟠  SECOND LEVEL SUPPORT CHAT  (Stufe 2 – intern & extern)     │
│  │  SUP · TEC · WET · ENT · (PL) · (KAM)                           │
│  │  Chat + Tickets werden hier besprochen                           │
│  └──────────────────────────────────────────────────────────────────┘
│       ▲               ▲                    ▲              ▲
│       │ Chat nicht    │ 🎫 Ticket direkt   │ Chat nicht   │ 🎫 Ticket direkt
│       │ gelöst        │ zu 2nd Level       │ gelöst       │ zu 2nd Level
│  ┌────────────┐  ┌───────────────────┐  ┌──────────────────────────────┐
│  │ 🔵 1ST     │  │ 🎫 TICKET-PFAD   │  │  ✉  EXT. FIRST LEVEL         │
│  │ LEVEL CHAT │  │ ab First Level    │  │  Email: support@sius.com     │
│  │ TEC·SUP·WET│  │ parallel zum Chat │  │  Telefon zu Bürozeiten       │
│  └────────────┘  │ kann FL überspri. │  │  🎫 Ticket parallel möglich  │
│       ▲          └───────────────────┘  └──────────────────────────────┘
│       │                  ▲                           ▲
│  ┌────────────┐          │                           │
│  │ 🏆 COMP.  │     Interne Anfrage           Externe Anfrage
│  │ SUPPORT   │     (Chat oder Ticket)         (Chat oder Ticket)
│  │TEC·SUP·   │
│  │WET·ENT    │
│  │ Nur Chat! │
│  └────────────┘
│
▼  niedrigste Eskalation
```
