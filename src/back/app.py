from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import xml.etree.ElementTree as ET
import logging
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
    section_html = f'<div class="section {
        class_name}"><h2>{section_title}</h2>'
    for child in element:
        section_html += f'<div class="item"><strong>{
            child.tag}:</strong> {child.text}</div>'
    section_html += '</div>'
    return section_html


@app.route('/upload', methods=['POST'])
def parse_xml():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400


        json_response = pipeline_manager.process_request(file)

        return jsonify(json_response)

        # html_output = validation_results_to_html(json_response)
        # with open("validation_results.html", "w", encoding="utf-8") as file:
        #     file.write(html_output)
        # return html_output
        # return json_response
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

