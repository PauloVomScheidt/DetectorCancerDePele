#  API IoT de Análise de Imagens — FastAPI + OpenCV

Este projeto é uma **API para análise automática de imagens IoT**, desenvolvida em **Python (FastAPI)**.
A API permite o **upload de uma imagem** e realiza o **processamento com OpenCV** para detectar **manchas ou imperfeições visuais**.
Como resultado, a API retorna um **relatório em JSON** com o percentual de manchas detectadas, além de gerar uma **imagem anotada** destacando as áreas detectadas.


##  Instalação e Execução

### 1️ Clonar o repositório

```bash
git clone https://github.com/SEU_USUARIO/projeto_fastapi_iot.git
cd projeto_fastapi_iot
```

---

### 2️ Criar e ativar ambiente virtual

**Windows (CMD):**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3️ Instalar dependências

```bash
pip install fastapi uvicorn opencv-python pillow numpy
```

---

### 4️ Executar o servidor

```bash
uvicorn app:app --reload
```

O servidor ficará disponível em:
‘	 [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

##  Testando a API

###  Verificar se está online

Abra no navegador:

```
http://127.0.0.1:8000/
```

Deve retornar:

```json
{"mensagem": "API IoT de análise de imagem está online "}
```

---

###  Enviar uma imagem para análise

Abra o Swagger UI (interface interativa):

```
http://127.0.0.1:8000/docs
```

1. Clique em **POST /analisar**
2. Clique em **Try it out**
3. Faça o upload de uma imagem (`.jpg`, `.png`, etc.)
4. Clique em **Execute**

Exemplo de resposta:

```json
{
  "arquivo": "imagem.jpg",
  "percentual_manchas": 6.72,
  "num_manchas": 3,
  "spots": [
    {"area": 1324.5, "bbox": [120, 80, 50, 60]},
    {"area": 980.0, "bbox": [300, 200, 40, 50]}
  ],
  "mensagem": "Possíveis manchas detectadas",
  "annotated_image": "annot_abc123.jpg",
  "annotated_url": "/imagens/annot_abc123.jpg"
}
```

---

### 🔹 Visualizar a imagem anotada

Copie o valor retornado em `annotated_url` e abra no navegador:

```
http://127.0.0.1:8000/imagens/annot_abc123.jpg
```

---

##  Explicação técnica resumida

1. A imagem é recebida via upload (`POST /analisar`);
2. É convertida para escala de cinza e suavizada (GaussianBlur);
3. Um limiar adaptativo detecta áreas mais escuras (possíveis manchas);
4. Contornos são encontrados e desenhados sobre a imagem original;
5. A API calcula o percentual de área manchada e gera o resultado em JSON;
6. Uma cópia da imagem anotada é salva em `imagens/`.

---
