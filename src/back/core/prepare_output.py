import html
import requests
import logging
from typing import Dict, Any
from flask import send_file

logger = logging.getLogger(__name__)

def format_rule(rule: Dict[str, Any]) -> str:
    """
    Formatea una regla individual para su visualización en HTML
    """
    return f"""
    <div class="rule">
        <p><b>Regla ID:</b> {html.escape(rule.get('rule_id', ''))}</p>
        <p><b>Estado:</b> <span style="color: {'green' if rule.get('status') == 'success' else 'red'}">{html.escape(rule.get('status', ''))}</span></p>
        <p><b>Mensaje:</b> {html.escape(rule.get('message', ''))}</p>
        <p><b>Descripción:</b> {html.escape(rule.get('description', ''))}</p>
    </div>
    """

def validation_results_to_html(validation_results: dict) -> str:
    """
    Convierte los resultados de validación a formato HTML
    """
    common_rules_html = ""
    model_rules_html = ""

    # Procesar reglas comunes
    for rule in validation_results.get("common_rules", []):
        common_rules_html += format_rule(rule)

    # Procesar reglas por modelo
    for model_name, rules in validation_results.get("model_rules", {}).items():
        model_rules_html += f"<h3>Model: {html.escape(model_name)}</h3>"
        for rule in rules:
            model_rules_html += format_rule(rule)

    # Estructura final del HTML
    html_output = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Validation Results</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 20px;
            }}
            h2 {{
                color: #2c3e50;
            }}
            h3 {{
                color: #34495e;
                margin-top: 20px;
            }}
            .rule {{
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        <h2>Validation Results</h2>
        <h3>Common Rules</h3>
        {common_rules_html}
        <h3>Model Rules</h3>
        {model_rules_html}
    </body>
    </html>
    """
    return html_output

def generate_pdf_report(validation_results: dict, pdf_path: str) -> bytes:
    """
    Genera un PDF a partir de los resultados de validación usando el servicio docx-to-pdf
    """
    try:
        # Generar el HTML a partir de los resultados de validación
        html_content = validation_results_to_html(validation_results)

        # Enviar el HTML al servicio de conversión
        response = requests.post(
            "http://docx-to-pdf:8080/pdf",
            files={"document": html_content}
        )

        if response.ok:
            with open(pdf_path, 'wb') as result_file:
                result_file.write(response.content)

            return response.content
            # return send_file(
            #     pdf_path,
            #     as_attachment=True,
            #     download_name="report.pdf",
            #     mimetype='application/pdf'
            # )
        else:
            logger.error(f"Error in processing: {response.status_code}", exc_info=True)
            raise Exception(f"Error in processing: {response.status_code}")

    except Exception as e:
        logger.error(f"Error en la generación del PDF: {str(e)}")
        raise
