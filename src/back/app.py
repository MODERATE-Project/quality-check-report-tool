from flask import Flask, request, jsonify
from flask_cors import CORS
import xml.etree.ElementTree as ET
import logging
import json
from core.pipeline_manager import PipelineManager
from core.prepare_output import validation_results_to_html
import config


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
    logger.info("*************** upload_xml ***************")

    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400


    questions = pipeline_manager.prepare_questions_to_user(file)
    
    json_string = json.dumps(questions, ensure_ascii=False, indent=4)
    print(json_string)

    with open('questions.json', 'w', encoding='utf-8') as archivo:
        json.dump(questions, archivo, ensure_ascii=False, indent=4)

    return json_string
    
@app.route('/parse', methods=['POST'])
def parse_xml(): # parseo del xml ya con la información de las preguntas que se le hicieron al usuario
    logger.debug("*************** parse_xml ***************")
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    questions_answers = json.loads(request.form['questions_answers'])

    html_content = pipeline_manager.process_request(file, questions_answers)
    
    html_output = validation_results_to_html(html_content)
    with open("validation_results.html", "w", encoding="utf-8") as file:
        file.write(html_output)
    return html_output


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6000)

