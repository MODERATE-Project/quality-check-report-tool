import xml.etree.ElementTree as ET
from typing import Union

class EpcDto:

    def __init__(self, xml_content: Union[str, ET.Element]):
        """
        Inicializa el EpcDto con contenido XML.

        Args:
            xml_content (Union[str, ET.Element]): Puede ser un contenido XML en texto
                                                  o un objeto ET.Element.
        """
        if isinstance(xml_content, str):
            self.tree = ET.ElementTree(ET.fromstring(xml_content))
            self.root = self.tree.getroot()
        elif isinstance(xml_content, ET.Element):
            self.root = xml_content
            self.tree = ET.ElementTree(self.root)
        else:
            raise TypeError("El argumento xml_content debe ser una cadena XML o un objeto ET.Element.")

    # def get_value_by_xpath(self, xpath: str) -> str:
    #     """
    #     Devuelve el valor del nodo correspondiente al XPath.

    #     Args:
    #         xpath (str): La expresión XPath para buscar el nodo.

    #     Returns:
    #         str: El valor del nodo encontrado o None si no existe.
    #     """
    #     element = self.root.find(xpath)
    #     if element is not None:
    #         return element.text
    #     return None




    # def __init__(self, xml_content: str):
    #     """
    #     Inicializa un objeto EpcDto con el contenido del XML.
        
    #     Args:
    #         xml_content (str): Contenido del archivo XML como cadena.
    #     """
    #     try:
    #         self.tree = ET.ElementTree(ET.fromstring(xml_content))
    #     except ET.ParseError as e:
    #         raise ValueError(f"Error al analizar el XML: {e}")

    def get_value_by_xpath(self, xpath: str):
        """
        Obtiene el valor de un nodo en el XML utilizando un XPath simple.

        Args:
            xpath (str): XPath del nodo (por ejemplo, "//IdentificacionEdificio/Municipio").

        Returns:
            str: Valor del nodo, o None si no se encuentra.
        """
        # Convertir XPath para compatibilidad básica con ElementTree
        path_parts = xpath.strip("/").split("/")
        element = self.tree.getroot()
        for part in path_parts:
            element = element.find(part)
            if element is None:
                return None
        return element.text if element is not None else None