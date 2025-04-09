from fastapi import HTTPException
from goose3 import Goose
import requests
import os
import threading
import re
from youtube_transcript_api import YouTubeTranscriptApi 


def get_text_of_web(url):
    g = Goose()
    article = g.extract(url=url)
    response ={ 
          "title": f"""{article.title.replace('"', "'")}""",
          "text": f"""{article.cleaned_text.replace('"', "'")}"""
          }
    return response

def call_api_post(url,data):
    print(f"call_ser({url})")

    response = requests.post(url, json=data)
    # print(response)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail="Error calling API")

def call_api_get(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=f"Error calling API: {response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def call_ser_texttomp3_thread(resume_text, name_file):
  def run_function():
    call_ser_texttomp3(resume_text, name_file)
  hilo = threading.Thread(target=run_function)
  hilo.start()
    
def call_ser_texttomp3(text,name_file):
    url = "http://ser_larynxes:5002/api/tts"
    params = {'text': text,
              "voice":"es-es/carlfm-glow_tts",
              "vocoder":"hifi_gan/vctk_medium",
              "denoiserStrength":"0.01",
              "noiseScale": "0.4",
              "lengthScale": "1.1"
              }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        path_name_file=f"/resources/mp3/{name_file}"
        with open(path_name_file, 'wb') as archivo:
            archivo.write(response.content)
            print(f"Archivo guardado como {path_name_file}")
        return response.content
    else:
        raise HTTPException(status_code=response.status_code, detail="Error calling API textomp3")
    
def get_subtitles(url, umbral_pausa=1.5):
    video_id = obtener_id_video(url)
    try:
        transcript = detectar_idioma_disponible(video_id)
        
        if not transcript or not transcript.snippets:
            return ""
        
        snippets = transcript.snippets
        response = []
        
        for i, snippet in enumerate(snippets):
            texto = re.sub(r"\[.*?\]", "", snippet.text).strip()
            
            if not texto.endswith((".", "!", "?")):
                texto += "."
            
            if i < len(snippets) - 1:
                # Calcular tiempo usando propiedades del objeto
                tiempo_fin_actual = snippet.start + snippet.duration
                tiempo_inicio_siguiente = snippets[i + 1].start  # Corrección clave
                
                if tiempo_inicio_siguiente - tiempo_fin_actual > umbral_pausa:
                    texto += "\n\n"
                else:
                    texto += " "
            
            response.append(texto)
        
        return ' '.join(response).replace("  ", " ").strip()
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return "" 

def obtener_id_video(url):
    # Patrón para extraer el ID del video
    patron = r"(?:v=|\/)([0-9A-Za-z_-]{11})"
    coincidencia = re.search(patron, url)
    if coincidencia:
        return coincidencia.group(1)  # Retorna el ID del video
    else:
        return None
    
def detectar_idioma_disponible(video_id):

    try:
        # Obtener la lista de idiomas disponibles
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Seleccionar automáticamente el primer idioma disponible
        for transcript_option in transcripts:
            if transcript_option.is_generated or transcript_option.is_translatable:
                print(f"Subtítulos encontrados en idioma: {transcript_option.language}")
                return transcript_option.fetch()  # Retorna los subtítulos en el idioma detectado
        
        print("No se encontraron subtítulos disponibles.")
        return None
    except Exception as e:
        print(f"Error al detectar idioma: {e}")
        return None
                        

if __name__ == '__main__':
    url = 'https://www.eleconomista.es/mercados-cotizaciones/noticias/12900627/07/24/el-cientifico-malagueno-que-trabaja-con-nvidia-habla-del-secreto-de-la-compania-parece-que-tienen-una-bola-de-cristal.html?utm_source=pocket-newtab-es-es'
    response = get_text(url)
    print(response)

