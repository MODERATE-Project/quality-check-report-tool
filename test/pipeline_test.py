import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/back')))

from core.pipeline_manager import PipelineManager

if __name__ == "__main__":
    # Ruta al archivo XML local
    xml_file_path = "epcs/1 Bloque de viviendas.xml"  # Cambia esto por la ruta real de tu archivo XML

    # Crear una instancia de PipelineManager
    pipeline_manager = PipelineManager()

    # Ejecutar el procesamiento
    try:
        result = pipeline_manager.process_request(xml_file_path)
        print("Processed Data:")
        print(result)
    except Exception as e:
        print(f"Error while processing the file: {e}")
