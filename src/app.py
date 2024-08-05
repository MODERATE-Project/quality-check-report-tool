from flask import Flask, request, render_template_string
from flask_cors import CORS

import xml.etree.ElementTree as ET

app = Flask(__name__)
CORS(app)

def create_html_section(element, section_title, is_full_width=False):
    class_name = "full-width" if is_full_width else "column"
    section_html = f'<div class="section {class_name}"><h2>{section_title}</h2>'
    for child in element:
        section_html += f'<div class="item"><strong>{child.tag}:</strong> {child.text}</div>'
    section_html += '</div>'
    return section_html


@app.route('/')
def index():
    return render_template_string(open('index.html').read())


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    tree = ET.parse(file)
    root = tree.getroot()

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

    imagen_element = root.find('.//Imagen')
    if imagen_element is not None and imagen_element.text is not None:
        base64_data = imagen_element.text.strip()
        base64_data = base64_data.split(',')[1]

        try:
            img_tag = f'<div class="section full-width"><h2>Imagen</h2><img src="data:image/png;base64,{base64_data}" alt="Imagen"></div>'
            html_content += img_tag
        except Exception as e:
            html_content += f'<p>Error al decodificar la imagen: {e}</p>'

    html_content += '</div>'
    return html_content


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
