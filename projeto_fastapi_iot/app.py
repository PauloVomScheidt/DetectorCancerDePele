from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import cv2
import numpy as np
import tempfile
import os
from uuid import uuid4

app = FastAPI(title="API de Análise de Imagens IoT", version="1.0")

IMAGES_DIR = "imagens"
os.makedirs(IMAGES_DIR, exist_ok=True)

app.mount("/imagens", StaticFiles(directory=IMAGES_DIR), name="imagens")

def detectar_manchas(imagem, min_area_ratio=0.0005):
    """
    Detecta manchas escuras na imagem.
    - min_area_ratio: fração mínima da área da imagem para considerar um contorno como 'mancha'.
    Retorna dicionário com métricas e a imagem anotada (BGR).
    """
    # garantia de copy
    img = imagem.copy()
    h, w = img.shape[:2]
    image_area = h * w

    # 1) pré-processamento
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # 2) segmentação: regiões escuras -> THRESH_BINARY_INV + Otsu
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # 3) operações morfológicas para limpar ruído
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    clean = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    clean = cv2.morphologyEx(clean, cv2.MORPH_CLOSE, kernel, iterations=1)

    # 4) encontrar contornos
    contours, _ = cv2.findContours(clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 5) filtrar contornos por área mínima relativa
    min_area = image_area * min_area_ratio
    spots = []
    total_spots_area = 0.0

    annotated = img.copy()
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue
        x, y, cw, ch = cv2.boundingRect(cnt)
        total_spots_area += area
        spots.append({
            "area": round(float(area), 2),
            "bbox": [int(x), int(y), int(cw), int(ch)]
        })
        cv2.rectangle(annotated, (x, y), (x + cw, y + ch), (0, 0, 255), 2)
        cv2.putText(annotated, f"{len(spots)}", (x, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    percentual = (total_spots_area / image_area) * 100.0

    if percentual > 15:
        mensagem = "Manchas extensas detectadas"
    elif percentual > 5:
        mensagem = "Possíveis manchas detectadas"
    else:
        mensagem = "Imagem limpa"

    resultado = {
        "percentual_manchas": round(percentual, 2),
        "num_manchas": len(spots),
        "spots": spots,
        "mensagem": mensagem,
        "annotated_image_obj": annotated
    }
    return resultado


@app.get("/")
def raiz():
    return {"mensagem": "API IoT de análise de imagem está online 🚀"}


@app.post("/analisar")
async def analisar_imagem(foto: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(foto.filename)[1]) as temp:
            temp.write(await foto.read())
            temp.flush()
            path = temp.name

        imagem = cv2.imread(path)
        try:
            os.remove(path)
        except Exception:
            pass

        if imagem is None:
            return JSONResponse(status_code=400, content={"erro": "Imagem inválida ou formato não suportado."})

        resultado = detectar_manchas(imagem)
        annotated = resultado.pop("annotated_image_obj")

        fname = f"annot_{uuid4().hex}.jpg"
        out_path = os.path.join(IMAGES_DIR, fname)
        cv2.imwrite(out_path, annotated)

        resposta = {
            "arquivo": foto.filename,
            "percentual_manchas": resultado["percentual_manchas"],
            "num_manchas": resultado["num_manchas"],
            "mensagem": resultado["mensagem"],
            "annotated_image": fname,
            "annotated_url": f"/imagens/{fname}"
        }
        return resposta

    except Exception as e:
        return JSONResponse(status_code=500, content={"erro": str(e)})
