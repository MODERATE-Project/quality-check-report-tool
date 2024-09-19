from flask import Flask, request
from flask_cors import CORS
import xml.etree.ElementTree as ET



app = Flask(__name__)
CORS(app)

@app.route('/upload', methods=['POST'])
def parse_xml():

    if request.content_type == 'application/xml':
        return "XML Processed", 200
        # Access the raw request data and parse it as XML
        xml_data = request.data
        root = ET.fromstring(xml_data)
        
        value = root.find('TipoDeEdificio').text

        return f"XML Processed. Value of TipoDeEdificio: {value}", 200
    else:
        return "Invalid content type", 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6000)
