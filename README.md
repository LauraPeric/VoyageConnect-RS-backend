# VoyageConnect – Raspodijeljeni Sustav

**Fakultet:** Fakultet informatike u Puli  
**Kolegij:** Raspodijeljeni sustavi  
**Nositelj kolegija:** doc. dr. sc. Nikola Tanković  
**Asistent:** Luka Blašković, mag. inf.  
**Studentica:** Laura Perić


## 🧠 Opis projekta

**VoyageConnect** je aplikacija raspodijeljenog sustava čiji je cilj povezivanje korisnika putem kreiranih destinacija i objava, te omogućavanje međusobne interakcije kroz komentare i rasprave na forumu. Sustav je izgrađen kao skup mikroservisa koji komuniciraju preko HTTP protokola koristeći NGINX kao reverse proxy.

Projekt koristi autentifikaciju putem JSON Web Tokena (JWT), a svaki mikroservis zadužen je za svoju zasebnu domenu unutar sustava.

## 🚀 Pregled projekta
Distribuirani pozadinski sustav (backend) temeljen na mikroservisima, izgrađen pomoću tehnologija FastAPI, Docker i MongoDB.
Podržava autentifikaciju korisnika, objave, komentare i sustav foruma.


## 🛠 Korištene tehnologije i servisi

- **Backend:** FastAPI, Pydantic  
  Aplikacija je razvijena korištenjem FastAPI frameworka za izradu visokoučinkovitih REST API-jeva.
  Pydantic se koristi za deklarativnu validaciju podataka i definiranje ulazno-izlaznih modela.

- **Baza podataka:** MongoDB (korištenjem Motor klijenta)  
  Sustav koristi MongoDB kao primarnu NoSQL bazu podataka. Asinkroni pristup putem Motor klijenta omogućava visoku skalabilnost i neblokirajuće operacije nad bazom.

- **Autentifikacija:** JWT (JSON Web Tokeni)  
  Autentifikacija korisnika implementirana je korištenjem JWT tokena, čime se omogućuje sigurna i skalabilna autorizacija bez potrebe za server-side sesijama.
  Korištene su biblioteke `python-jose[cryptography]` za rad s tokenima i `passlib[bcrypt]` za sigurnu pohranu lozinki.

- **Pokretanje aplikacije:** Docker i Docker Compose  
  Svi mikroservisi dockerizirani su zbog lakšeg testiranja, skaliranja i deployanja.
  Cjelokupno razvojno okruženje pokreće se pomoću `docker-compose. (Pokretanje svih servisa odjednom)

- **Proxy i usmjeravanje zahtjeva:** NGINX  
  NGINX se koristi kao reverzni proxy poslužitelj koji prosljeđuje HTTP zahtjeve prema odgovarajućim mikroservisima na temelju definiranih ruta.
  Također omogućuje centralizirano upravljanje pristupom, HTTPS terminaciju i poboljšava performanse keširanjem odgovora.

- **Dodatne biblioteke:**  
  - `uvicorn[standard]` – ASGI server za pokretanje FastAPI aplikacija  
  - `python-multipart` – podrška za obradu formi i datoteka  
  - `email-validator` – validacija email adresa



## 🎯 Glavne funkcionalnosti

- ✅ Registracija i prijava korisnika (JWT autentifikacija)
- 🗺 Kreiranje i pregled destinacija
- 📝 Objavljivanje postova vezanih uz destinacije
- 💬 Komentiranje postova i odgovaranje na komentare
- 🧵 Forum s temama i pripadajućim komentarima



## 🧩 Pregled mikroservisa

| Mikroservis           | Opis funkcionalnosti                                                                 |
|------------------------|--------------------------------------------------------------------------------------|
| `auth-service`         | Upravljanje registracijom, prijavom i verifikacijom JWT tokena                      |
| `destination-service`  | Omogućava korisnicima kreiranje i pregled destinacija                              |
| `post-service`         | Omogućava dodavanje i pregled postova unutar pojedine destinacije                  |
| `comment-service`      | Upravljanje komentarima i ugniježđenim odgovorima na postove                        |
| `forum-service`        | Omogućava kreiranje forum tema i sudjelovanje u raspravama                         |

---

## 📁 Za pokretanje svih mikroservisa koristi sljedeće naredbe u terminalu:

    cd voyageconnect_project
    docker-compose down
    docker-compose up


## 📁 Build i pokretanje pojedinačnih servisa

1. Auth Service - Izgradite i pokrenite Auth mikroservis:

    ```bash
    cd auth-service
    docker build -t auth-service:1.0 .
    docker run -p 8001:8000 --name auth-service auth-service:1.0
    ```

2. Destination Service -Izgradite i pokrenite Destination mikroservis:

    ```bash
    cd destination-service
    docker build -t destination-service:1.0 .
    docker run -p 8002:8000 --name destination-service destination-service:1.0
    ```

3. Post Service - Izgradite i pokrenite Post mikroservis:

    ```bash
    cd post-service
    docker build -t post-service:1.0 .
    docker run -p 8003:8000 --name post-service post-service:1.0
    ```

4. Comment Service - Izgradite i pokrenite Comment mikroservis:

    ```bash
    cd comment-service
    docker build -t comment-service:1.0 .
    docker run -p 8004:8000 --name comment-service comment-service:1.0
    ```

5. Forum Service - Izgradite i pokrenite Forum mikroservis:

    ```bash
    cd forum-service
    docker build -t forum-service:1.0 .
    docker run -p 8005:8000 --name forum-service forum-service:1.0
    ```
