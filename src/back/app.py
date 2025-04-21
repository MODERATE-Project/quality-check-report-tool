from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import xml.etree.ElementTree as ET
import logging
import json
from core.pipeline_manager import PipelineManager
from core.prepare_output import validation_results_to_html, generate_pdf_report
import config
import io


app = Flask(__name__)
CORS(app)

logging.basicConfig(level=config.LOG_LEVEL,  # Set the logging level
                    # Log format
                    format='[%(asctime)s] [%(levelname)s]: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',  # Date format
                    # Log output handler (console)
                    handlers=[logging.StreamHandler()])

logger = logging.getLogger(__name__)

pipeline_manager = PipelineManager()

def create_html_section(element, section_title, is_full_width=False):
    class_name = "full-width" if is_full_width else "column"
    section_html = f'<div class="section {class_name}"><h2>{section_title}</h2>'
    for child in element:
        section_html += f'<div class="item"><strong>{child.tag}:</strong> {child.text}</div>'
    section_html += '</div>'
    return section_html

@app.route('/upload', methods=['POST'])
def upload_xml(): #para obtener las posibles preguntas para el usuario
    try:
        logger.debug("*************** upload_xml ***************")
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
    except Exception as e:
        logger.error(f"Error al procesar el archivo: {str(e)}", exc_info=True)
        return jsonify({"error": "Error al procesar el archivo"}), 500

    questions = pipeline_manager.prepare_questions_to_user(file)
    logger.debug("questions: %s", questions)
    json_string = json.dumps(questions, ensure_ascii=False, indent=4)
    print(json_string)

    with open('questions.json', 'w', encoding='utf-8') as archivo:
        json.dump(questions, archivo, ensure_ascii=False, indent=4)

    return questions

@app.route('/evaluate', methods=['POST'])
def evaluate_xml():
    """
    Endpoint que:
      1) Recibe un archivo y respuestas de preguntas previas (opcional).
      2) Llama a la lógica de pipeline_manager (o similar).
      3) Devuelve:
         - El HTML de validación (si aplica).
         - Las preguntas que resulten de la nueva evaluación (si quedan pendientes).
    """
    try:
        logger.debug("*************** evaluate_xml ***************")

        # 1) Verificar que venga un archivo en la petición
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        # 2) Cargar las respuestas a preguntas anteriores (si existen)
        #    - Podrías venir en 'request.form['form_data']'
        #    - O bien en 'request.json' (dependiendo de cómo lo envíe el front)
        # En este ejemplo, asumimos que se envía en form-data junto con el archivo:
        questions_answers_str = request.form.get('form_data', '{}')
        logger.debug("***************************   questions_answers  ***********************************************************")
        
        try:
            questions_answers = json.loads(questions_answers_str)
        except json.JSONDecodeError:
            questions_answers = {}
        logger.debug("*****************************************************************************************************************")
        logger.debug(f"questions_answers = {questions_answers}")

        # 3) Procesar la lógica: parsear y validar, y obtener
        #    nuevas preguntas (si las reglas así lo requieren).
        resultado_validacion = pipeline_manager.process_request(file, questions_answers)
        # La forma exacta de pipeline_manager.process_request(...) depende de tu implementación.
        # Se asume que retorna algo como un dict con:
        #  {
        #    "html_content": "...",
        #    "new_questions": {...}  # dict con las preguntas nuevas, si las hay
        #    "errors": [...]
        #  }

        # 4) Generar el HTML final (opcional, si tu pipeline ya no lo hace)
        #    Supongamos que en 'resultado_validacion' viene la parte "html_content" con tu HTML
        #    Si no, podemos generarlo con la función que ya usas:
        logger.debug("Generando HTML de validación")
        logger.debug(f"resultado_validacion: {resultado_validacion}")
        html_output = validation_results_to_html(resultado_validacion)#.get("html_content", ""))
        
        # 5) Guardar el HTML en un fichero local (opcional, como en tu ejemplo)
        with open("validation_results.html", "w", encoding="utf-8") as f:
            f.write(html_output)

        # 6) Responder con JSON que contenga:
        #    - El HTML (si lo quieres incrustar)
        #    - Las nuevas preguntas (si surgen)
        #    - Cualquier otra info que necesites en el front
        response_body = {
            "html_output": html_output,
            "new_questions": resultado_validacion.get("new_questions", {}),
            "errors": resultado_validacion.get("errors", []),
            # ...
        }
        response = jsonify(response_body)
        response.headers['Content-Type'] = 'application/json'
        return response

    except Exception as e:
        logger.error(f"Error al procesar el archivo: {str(e)}", exc_info=True)
        return jsonify({"error": "Error al procesar el archivo"}), 500
    


@app.route('/report', methods=['POST'])
def generate_report():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Generar el PDF
        pdf_content = generate_pdf_report(data, "ruta_del_pdf.pdf")
        
        # Crear un buffer en memoria para el PDF
        pdf_buffer = io.BytesIO(pdf_content)
        
        # Enviar el PDF como respuesta
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='informe.pdf'
        )
        
    except Exception as e:
        logger.error(f"Error al generar el informe: {str(e)}")
        return jsonify({"error": "Error al generar el informe"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

