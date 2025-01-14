from abc import ABC, abstractmethod
from typing import Dict
# from epc_dto import EpcDto
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
import logging

logger = logging.getLogger(__name__)

class InputLayer(ABC):

    def process_input(self, file) -> Dict:
        epc_parsed = self.parse_dto_epc(file)
        return epc_parsed

    @abstractmethod
    def parse_dto_epc(self, file) -> Dict:
        pass


class XmlInputLayer(InputLayer):
    
    def parse_dto_epc(self, file) -> Element:

        tree = ET.parse(file)

        root = tree.getroot()

        logger.debug("EPC parsed correctlty")

        return root

        # html_content = '<div class="columns">'

        # sections = [
        #     ('DatosDelCertificador', 'Datos del Certificador'),
        #     ('IdentificacionEdificio', 'Identificación del Edificio'),
        #     ('DatosGeneralesyGeometria', 'Datos Generales y Geometría'),
        #     ('DatosEnvolventeTermica', 'Datos de la Envolvente Térmica')
        # ]

        # for tag, title in sections:
        #     element = root.find(tag)
        #     if element is not None:
        #         html_content += create_html_section(element, title)

        # imagen_element = root.find('.//Imagen')
        # imagen_elements = root.findall('.//Imagen')
        # plano_elements = root.findall('.//Plano')
        # if len(plano_elements) > 0:
        #     imagen_elements.append(*plano_elements)

        # for imagen_element in imagen_elements:
        #     if imagen_element is not None and imagen_element.text is not None:
        #         base64_data = imagen_element.text.strip()
        #         base64_data_split = base64_data.split(',')
        #         if len(base64_data_split) > 1:
        #             base64_data = base64_data_split[1]

        #         try:
        #             img_tag = f'<div class="section full-width"><h2>Imagen</h2><img width="400px"; src="data:image/png;base64,{
        #                 base64_data}" alt="Imagen"></div>'
        #             html_content += img_tag
        #         except Exception as e:
        #             html_content += f'<p>Error al decodificar la imagen: {e}</p>'

        # html_content += '</div>'

