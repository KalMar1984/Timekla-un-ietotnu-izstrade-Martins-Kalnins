# 📄 PRD — “Trīs Labas Lietas”

## 1. Produkta pārskats

**Nosaukums:** Trīs Labas Lietas  
**Tips:** Personīgās labsajūtas / dienasgrāmatas lietotne  
**Platforma:** Web aplikācija (PWA, offline-first)

### Mērķis
Veicināt lietotāja pozitīvo domāšanu, pašrefleksiju un psihoemocionālo veselību.

---

## 2. Problēma

- Fokuss uz negatīvo
- Trūkst pašrefleksijas
- Netiek analizēti emocionālie paradumi

---

## 3. Mērķauditorija

- Individuāli lietotāji
- Ģimenes
- Nākotnē: publiska lietošana

---

## 4. Core funkcionalitāte

Lietotājs katru dienu ievada:
- 3 labas lietas
- 1–3 negatīvas lietas
- 1–3 pateicības
- emocijas
- piezīmes
- dienasgrāmatas ierakstu

---

## 5. Lietotāja konti (CRUD)

- Create
- Read
- Update
- Delete

Multi-user vienā ierīcē.

---

## 6. Dienas ieraksti

### Lauki:
- date
- positive_things
- negative_things
- gratitude
- emotions
- notes
- diary_entry

---

## 7. Emociju sistēma

### Noklusētās emocijas:
- priecīgs
- noskumis
- laimīgs
- nelaimīgs
- bēdīgs
- spēka pilns
- noguris
- noraizējies
- dusmīgs
- bailīgs
- satraukts
- atpūties
- jautrs

### Funkcionalitāte:
- pievienot jaunas emocijas
- grupēt kategorijās

---

## 8. Atskati un analītika

- nedēļas pārskats
- mēneša pārskats

### Ietver:
- emociju biežumu
- pozitīvo/negatīvo attiecību
- tendences

---

## 9. Rekomendāciju sistēma

Rule-based loģika:

- Ja bieži “noguris” → ieteikums atpūtai
- Ja bieži “noraizējies” → ieteikums relaksācijai
- Ja maz pozitīvo ierakstu → ieteikums fokusēties uz pozitīvo

---

## 10. Offline-first arhitektūra

### Frontend:
- Vue 3
- PWA
- IndexedDB (Dexie.js)

### Backend:
- Flask (Python)
- REST API

### Database:
- Lokāli: IndexedDB
- Serverī: PostgreSQL

---

## 11. Datu modelis

### users
- id
- username
- password_hash

### daily_entries
- id
- user_id
- date
- sync_status   

---

## 12. Sinhronizācija

- manuāla vai automātiska
- last-write-wins (MVP)

---

## 13. Drošība

- password hashing (bcrypt)
- datu izolācija

---

## 14. MVP

- multi-user
- offline režīms
- CRUD ierakstiem
- emociju tracking
- analītika
- rekomendācijas

---

## 15. Nākotnes attīstība

- foto, audio, video
- mobilā aplikācija
- AI rekomendācijas

---

## 16. Riska faktori

- sync konflikti
- datu zudums
- offline sarežģītība

---

## 17. Tehnoloģiju stacks

- Frontend: Vue 3
- Backend: Flask (Python)
- DB: IndexedDB + PostgreSQL

---

## 18. Atvērtie jautājumi

- sync nepieciešamība MVP?
- backup stratēģija?
- AI ieviešana nākotnē?

