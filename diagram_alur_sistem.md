# Diagram Alur Implementasi Sistem

> **Cara pakai**: Copy kode Mermaid ke [mermaid.live](https://mermaid.live) → Export sebagai PNG/SVG → Masukkan ke dokumen Word.
>
> **Versi:** Disesuaikan dengan PRD terkini. Modul lama (`BuildingDataReceiver`, `BuildingClickHandler`, `ReceiveBuildingsData`, callback Unity→React) sudah **deprecated** dan digantikan alur baru: Unity menarik data sendiri via `GET /api/unity/data`, dan komunikasi bersifat **satu arah** React→Unity (`SendMessage("NavigationReceiver","NavigateTo", unity_object_name)`).

---

## 1. Diagram Arsitektur Sistem (Keseluruhan)

```mermaid
%%{init: {'theme':'neutral'}}%%
graph TB
    subgraph USERS["Pengguna"]
        ADMIN["Administrator"]
        PUBLIC["Mahasiswa / Pengunjung"]
    end

    subgraph FRONTEND["Frontend (React + TypeScript / Vite)"]
        ADMIN_DASH["Admin Dashboard<br/>/admin"]
        PUBLIC_DASH["Public Dashboard<br/>/"]
        SEARCH["Panel Pencarian<br/>SearchOverlay"]
        UNITY_EMBED["Unity WebGL Viewer<br/>CampusMapViewer"]
        LOGIN["Login Page<br/>/login"]
    end

    subgraph BACKEND["Backend"]
        SUPABASE_SDK["Supabase SDK<br/>(Client-Side)"]
        VERCEL_FN["Vercel Serverless<br/>Functions /api/*"]
        EXPRESS["Express.js Server<br/>:3001 (proxy + rate limiter)"]
    end

    subgraph DATABASE["Database & Layanan"]
        POSTGRES["PostgreSQL<br/>(Supabase Cloud)"]
        AUTH["Supabase Auth<br/>(JWT)"]
        STORAGE["Supabase Storage<br/>(Foto Gedung/Fasilitas)"]
        UMAMI["Umami Analytics<br/>(Docker :3000)"]
    end

    subgraph UNITY_ENGINE["Unity WebGL Engine"]
        BUILDING_DB["BuildingDatabase<br/>(fetch data + cache)"]
        NAV_RECEIVER["NavigationReceiver<br/>(terima NavigateTo)"]
        NAV_GUIDE["NavigationGuide<br/>(render rute)"]
        SYNC_CHECKER["DatabaseSyncChecker<br/>(Editor Tool)"]
    end

    %% Interaksi pengguna
    ADMIN -->|Login| LOGIN
    ADMIN -->|CRUD Data| ADMIN_DASH
    PUBLIC -->|Akses Info| PUBLIC_DASH
    PUBLIC -->|Cari Lokasi| SEARCH
    PUBLIC -->|Navigasi 3D| UNITY_EMBED

    %% Frontend ke backend
    LOGIN -->|signInWithPassword| AUTH
    ADMIN_DASH -->|CRUD + Audit Log| SUPABASE_SDK
    PUBLIC_DASH -->|Fetch Data| SUPABASE_SDK
    PUBLIC_DASH -->|Statistik Analitik| EXPRESS
    ADMIN_DASH -->|Upload Foto| STORAGE

    %% Supabase SDK ke DB
    SUPABASE_SDK -->|Query + RLS| POSTGRES
    SUPABASE_SDK -->|Session| AUTH

    %% Express proxy
    EXPRESS -->|Proxy API| UMAMI

    %% Jembatan React -> Unity (SATU ARAH)
    SEARCH -->|SendMessage NavigateTo<br/>unity_object_name| NAV_RECEIVER

    %% Unity menarik data sendiri (runtime)
    BUILDING_DB -->|HTTP GET /api/unity/data| VERCEL_FN
    SYNC_CHECKER -->|HTTP GET /api/unity/names<br/>Editor only| VERCEL_FN
    VERCEL_FN -->|Query| POSTGRES

    %% Alur internal Unity
    BUILDING_DB -->|rebuild cache| NAV_RECEIVER
    NAV_RECEIVER -->|StartNavigation| NAV_GUIDE
```

---

## 2. Sequence Diagram — Alur CRUD Admin (Create Fasilitas)

```mermaid
%%{init: {'theme':'neutral'}}%%
sequenceDiagram
    actor Admin
    participant UI as Admin Dashboard<br/>(React)
    participant SVC as supabaseDataService
    participant SB as Supabase SDK
    participant DB as PostgreSQL<br/>(+ RLS)
    participant AUDIT as audit_logs
    participant STORE as Supabase Storage

    Admin->>UI: Klik "Tambah Fasilitas"
    UI->>UI: Buka FacilityModal

    Admin->>UI: Isi form + Upload foto
    UI->>STORE: uploadFacilityPhoto(file)
    STORE-->>UI: Return publicUrl

    Admin->>UI: Submit form
    UI->>SVC: createFacility(data)
    SVC->>SVC: clearCache()
    SVC->>SB: supabase.from("fasilitas").insert(data)
    SB->>DB: INSERT INTO fasilitas ... (JWT token attached)
    DB->>DB: RLS check: auth.role() = 'authenticated'
    DB-->>SB: Return inserted row
    SB-->>SVC: { data, error: null }

    SVC->>SB: Trigger DB menulis audit_logs
    Note over SVC,AUDIT: Audit log otomatis via<br/>database trigger
    SB->>AUDIT: INSERT INTO audit_logs ...

    SVC-->>UI: Return FacilityData
    UI->>UI: showToast("Berhasil", "success")
    UI->>SVC: loadData() -> fetch ulang
    SVC->>SB: Fetch ulang semua data
    SB-->>UI: Data terbaru
    UI->>UI: Re-render tabel
```

---

## 3. Sequence Diagram — Alur Data & Navigasi Unity WebGL

```mermaid
%%{init: {'theme':'neutral'}}%%
sequenceDiagram
    actor User as Pengguna
    participant React as React Frontend
    participant API as Vercel Serverless<br/>/api/unity/data
    participant DB as PostgreSQL<br/>(Supabase)
    participant BDB as BuildingDatabase<br/>(Unity)
    participant NR as NavigationReceiver
    participant NG as NavigationGuide
    participant Scene as Scene 3D

    Note over BDB,DB: === FASE 1: Unity Menarik Data (saat game start) ===

    BDB->>API: HTTP GET /api/unity/data
    API->>DB: SELECT gedung & fasilitas (+ unity_object_name)
    DB-->>API: Result set
    API-->>BDB: JSON { gedung: [...], fasilitas: [...] }
    BDB->>BDB: Cache unityObjectNames & realNames
    BDB->>BDB: isLoaded = true
    BDB->>NR: Rebuild cache Transform lookup

    Note over User,Scene: === FASE 2: Navigasi Terpandu (satu arah React -> Unity) ===

    User->>React: Cari & pilih lokasi (SearchOverlay)
    React->>NR: SendMessage("NavigationReceiver",<br/>"NavigateTo", unity_object_name)
    NR->>NR: Lookup Transform via cache (case-insensitive)
    alt Ditemukan di cache
        NR->>BDB: GetRealName(unity_object_name)
        BDB-->>NR: nama tampilan
    else Tidak ada di cache
        NR->>Scene: FindInactiveByName (fallback)
        Scene-->>NR: Transform target
    end
    NR->>NG: StartNavigation(target, namaTampilan)
    NG->>NG: NavMesh.CalculatePath()
    NG->>Scene: Render garis rute (PathLine) + label jarak
    NG-->>User: Tampilkan rute & jarak tersisa
    Note over NG,User: Stop otomatis saat jarak < stopDistance
```

---

## 4. Diagram Deployment — Pengembangan vs Produksi

```mermaid
%%{init: {'theme':'neutral'}}%%
graph LR
    subgraph DEV["Lingkungan PENGEMBANGAN / PRODUKSI SAAT INI"]
        direction TB
        B1["Browser"] --> V1["Vercel CDN"]
        V1 --> R1["React SPA + Unity WebGL<br/>(dist/, unity-builds/)"]
        R1 --> SC1["Supabase Cloud<br/>PostgreSQL + Auth + Storage"]
        R1 --> VF1["Vercel Serverless<br/>Functions /api/*"]
        VF1 --> SC1
        R1 --> E1["Express :3001<br/>(proxy analitik)"]
        E1 --> UM1["Umami<br/>Docker :3000"]
    end

    subgraph PROD["RENCANA MASA DEPAN (Server Kampus)"]
        direction TB
        B2["Browser"] --> N2["Nginx<br/>(Reverse Proxy + SSL)"]
        N2 --> S2["Static Files<br/>dist/ + unity-builds/"]
        N2 --> E2["Express.js :3001<br/>(API + Proxy Analitik)"]
        E2 --> SH2["Supabase Self-Hosted<br/>PostgreSQL + Auth + Storage"]
        E2 --> UM2["Umami<br/>Docker :3000"]
        N2 --> UM2
    end
```

> Catatan: saat ini sistem berjalan di **Supabase Cloud** agar online 24/7. **Supabase self-hosted** adalah rencana masa depan saat server kampus tersedia. `docker-compose.yml` di repo web khusus untuk **Umami Analytics**, bukan Supabase.

---

## 5. Diagram Alur Sistem End-to-End (Flowchart)

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TD
    A["Admin Login"] --> B{"Autentikasi<br/>Supabase Auth"}
    B -->|Gagal| C["Tampilkan Error"]
    B -->|Berhasil| D["JWT Token Diterima"]
    D --> E["Akses Admin Dashboard"]
    E --> F{"Pilih Operasi"}

    F -->|Create| G["Buka Modal Form"]
    F -->|Update| H["Buka Modal Form<br/>(data prefill)"]
    F -->|Delete| I["Tampilkan Konfirmasi"]

    G --> J["Submit Data"]
    H --> J
    I --> K["Konfirmasi Hapus"]

    J --> L["Supabase SDK<br/>INSERT / UPDATE"]
    K --> M["Supabase SDK<br/>DELETE"]

    L --> N{"RLS Check"}
    M --> N

    N -->|Authorized| O["Data Tersimpan<br/>di PostgreSQL"]
    N -->|Unauthorized| P["Error 403"]

    O --> Q["Audit Log Dicatat<br/>(database trigger)"]
    O --> R["Cache Invalidated"]
    R --> S["Refresh Dashboard"]

    O --> T["Data Tersedia via API"]

    T --> U["Public Dashboard<br/>(React)"]
    T --> V["Unity WebGL<br/>BuildingDatabase via HTTP"]
    T --> W["Unity Editor<br/>DatabaseSyncChecker"]

    U --> X["Mahasiswa / Pengunjung<br/>melihat informasi kampus"]
    V --> Y["Pengguna navigasi denah 3D<br/>via pencarian (NavigateTo)"]
    W --> Z["Developer cek sinkronisasi<br/>unity_object_name vs scene"]
```

---

## Cara Export untuk Dokumen Word

1. Buka **[mermaid.live](https://mermaid.live)**
2. Copy-paste kode Mermaid (tanpa backtick ` ```mermaid `)
3. Diagram akan ter-render otomatis di panel kanan
4. Klik **Actions → Export PNG** (resolusi tinggi) atau **SVG**
5. Masukkan ke dokumen Word sebagai gambar

> Tema `neutral` sudah disetel via `%%{init: {'theme':'neutral'}}%%` di awal tiap diagram agar warna konsisten dan netral. Versi PlantUML (`.puml`) dari diagram-diagram BAB II tersedia di `document/diagrams/`.
