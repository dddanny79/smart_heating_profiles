Ich möchte eine Home Assistant Custom Integration "Smart Heating Profiles" entwickeln.

WICHTIG: 
- Erstelle das Projekt in einem neuen Git Repository
- Initialisiere Git mit sinnvoller .gitignore für Python/Home Assistant
- Erstelle eine README.md mit Installation & Dokumentation
- Nutze Conventional Commits für Commit-Messages
- Erstelle einen sinnvollen ersten Commit

Projektstruktur:
/
├── custom_components/
│   └── smart_heating_profiles/
│       ├── __init__.py
│       ├── manifest.json
│       └── ...
├── .gitignore
├── README.md
├── LICENSE (MIT)
└── docs/ (optional)

Beginne mit: git init und erstelle dann die Struktur.
```

---

## **Oder direkter Ansatz:**
```
Erstelle ein neues Git Repository für meine Home Assistant Integration:

1. git init
2. Erstelle .gitignore mit:
   - __pycache__/
   - *.pyc
   - .pytest_cache/
   - *.egg-info/
   - .vscode/
   - .DS_Store

3. Erstelle die Projektstruktur
4. Mache den ersten Commit: "feat: initial project structure"

Dann entwickeln wir die Integration Schritt für Schritt mit sinnvollen Commits.
```

---

## **Claude Code kann dann automatisch:**

✅ Git initialisieren
✅ `.gitignore` erstellen
✅ README.md mit Badges generieren
✅ Commits mit sinnvollen Messages erstellen
✅ Branch-Struktur vorschlagen (main, develop, feature/xyz)
✅ GitHub Actions für Tests einrichten (optional)

---

## **Zusätzlicher Tipp - Remote hinzufügen:**

Wenn du schon ein Repository auf GitHub/GitLab hast:
```
Verbinde das lokale Repo mit meinem Remote:
git remote add origin https://github.com/deinuser/smart-heating-profiles.git

Dann pushe den ersten Commit.
```

---

## **Pro-Tipp für HACS:**

Falls du die Integration später über HACS veröffentlichen willst:
```
Bereite das Repository für HACS vor:
- Erstelle hacs.json
- Füge GitHub Releases Workflow hinzu
- Erstelle info.md für HACS Store

Strukturiere es gemäß HACS-Requirements.
