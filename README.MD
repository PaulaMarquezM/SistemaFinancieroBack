
---

# ✅ 1️⃣ README.md — Backend (FastAPI)

👉 **Copia y pega esto** como `README.md` en `SistemaFinancieroBack`

```md
# Sistema Financiero – Backend

Backend del proyecto **Sistema Financiero** desarrollado con **FastAPI (Python)**.  
Este módulo expone servicios para el cálculo de **Interés Simple** e **Interés Común**, siguiendo principios de arquitectura modular.

---

## 🧠 Funcionalidad implementada

### 📌 Módulo: Interés Simple y Común

El módulo permite calcular:

- **Interés (I)**
- **Monto final (M)**
- **Tiempo expresado en años**

Usando las fórmulas de Matemática Financiera:

- **Interés Simple**  
  `I = P · i · t`

- **Monto**  
  `M = P + I`

🔹 La diferencia entre **interés simple** e **interés común** está en la conversión del tiempo:
- Interés simple → año exacto de **365 días**
- Interés común → año comercial de **360 días**

---

## 🧱 Arquitectura del módulo

```

app/
└── modules/
└── interes/
├── schema.py    # Validación de datos (Pydantic)
├── service.py   # Lógica matemática
├── router.py    # Endpoints FastAPI

````

El módulo está desacoplado y se integra al backend principal mediante `include_router`.

---

## 🚀 Tecnologías usadas

- Python 3.x
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy (usado por el proyecto base)

---

## ▶️ Ejecución del proyecto

### 1️⃣ Instalar dependencias
```bash
pip install -r requirements.txt
````

### 2️⃣ Ejecutar el servidor

```bash
uvicorn app.main:app --reload
```

El backend estará disponible en:

```
http://127.0.0.1:8000
```

---

## 📄 Documentación (Swagger)

FastAPI genera documentación automática en:

```
http://127.0.0.1:8000/docs
```

---

## 📡 Endpoint disponible

### POST `/interes/calcular`

#### Request (JSON)

```json
{
  "capital": 1000,
  "tasa_anual": 12,
  "tiempo": 90,
  "unidad": "dias",
  "tipo": "comun"
}
```

#### Response (JSON)

```json
{
  "interes": 30,
  "monto": 1030,
  "tiempo_anios": 0.25
}
```

---

## 🎓 Nota académica

Este módulo fue desarrollado como parte de un proyecto académico de Matemática Financiera, aplicando conceptos teóricos en una API REST moderna y documentada.

```

✔ Ese README es **nivel universitario alto**  
✔ Explica teoría + código + uso  
✔ Te deja muy bien parado

---

# ✅ 2️⃣ Integrar TU módulo al FRONTEND del grupo

Repo frontend:
👉 https://github.com/PaulaMarquezM/SistemaFinanciero.git

(No vamos a rehacer nada, **solo consumir tu endpoint**)

---

## 🧠 IDEA CLAVE
El frontend **solo debe hacer una petición HTTP** a tu backend:

```

POST [http://localhost:8000/interes/calcular](http://localhost:8000/interes/calcular)

````

---

## 🧩 PASOS GENERALES (funciona en JS o TS)

### 1️⃣ Ubica dónde están los formularios
Busca algo como:
- `index.html`
- `script.js`
- `app.js`
- `main.ts`

Ahí es donde se conectan los botones.

---

### 2️⃣ Función para llamar a tu backend (JS / TS)

👉 **Ejemplo genérico (fetch)**  
Esto se adapta fácil al proyecto del grupo:

```js
async function calcularInteres() {
  const data = {
    capital: Number(document.getElementById("capital").value),
    tasa_anual: Number(document.getElementById("tasa").value),
    tiempo: Number(document.getElementById("tiempo").value),
    unidad: document.getElementById("unidad").value,
    tipo: document.getElementById("tipo").value
  };

  const response = await fetch("http://localhost:8000/interes/calcular", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(data)
  });

  const result = await response.json();

  document.getElementById("interes").innerText = result.interes;
  document.getElementById("monto").innerText = result.monto;
}
````

---

### 3️⃣ HTML mínimo que el frontend necesita

```html
<input id="capital" type="number" placeholder="Capital">
<input id="tasa" type="number" placeholder="Tasa anual %">
<input id="tiempo" type="number" placeholder="Tiempo">

<select id="unidad">
  <option value="dias">Días</option>
  <option value="meses">Meses</option>
  <option value="anios">Años</option>
</select>

<select id="tipo">
  <option value="simple">Interés simple</option>
  <option value="comun">Interés común</option>
</select>

<button onclick="calcularInteres()">Calcular</button>

<p>Interés: <span id="interes"></span></p>
<p>Monto: <span id="monto"></span></p>
```

---
