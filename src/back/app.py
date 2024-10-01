from flask import Flask, request, jsonify
from flask_cors import CORS
import xml.etree.ElementTree as ET
import logging


app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG,  # Set the logging level
                    # Log format
                    format='[%(asctime)s] [%(levelname)s]: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',  # Date format
                    # Log output handler (console)
                    handlers=[logging.StreamHandler()])

logger = logging.getLogger(__name__)

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

    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    tree = ET.parse(file)

    root = tree.getroot()

    logger.debug("EPC parsed correctlty")

    html_content = '<div class="columns">'

    sections = [
        ('DatosDelCertificador', 'Datos del Certificador'),
        ('IdentificacionEdificio', 'Identificación del Edificio'),
        ('DatosGeneralesyGeometria', 'Datos Generales y Geometría'),
        ('DatosEnvolventeTermica', 'Datos de la Envolvente Térmica')
    ]

    for tag, title in sections:
        element = root.find(tag)
        if element is not None:
            html_content += create_html_section(element, title)

    # imagen_element = root.find('.//Imagen')
    imagen_elements = root.findall('.//Imagen')
    plano_elements = root.findall('.//Plano')
    if len(plano_elements) > 0:
        imagen_elements.append(*plano_elements)

    for imagen_element in imagen_elements:
        if imagen_element is not None and imagen_element.text is not None:
            base64_data = imagen_element.text.strip()
            base64_data_split = base64_data.split(',')
            if len(base64_data_split) > 1:
                base64_data = base64_data_split[1]

            try:
                img_tag = f'<div class="section full-width"><h2>Imagen</h2><img width="400px"; src="data:image/png;base64,{
                    base64_data}" alt="Imagen"></div>'
                html_content += img_tag
            except Exception as e:
                html_content += f'<p>Error al decodificar la imagen: {e}</p>'

    html_content += '</div>'
    return html_content


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6000)
