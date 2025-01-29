import html

def validation_results_to_html(validation_results: dict) -> str:
    """
    Convierte los resultados de validación en un HTML formateado.

    Args:
        validation_results (dict): Diccionario con los resultados de validación.

    Returns:
        str: HTML formateado como cadena.
    """
    def format_rule(rule):
        """
        Formatea un resultado de regla individual en HTML.
        """
        return f"""
        <div style="margin-bottom: 10px; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
            <p><b>Rule ID:</b> {html.escape(str(rule.get("rule_id", "N/A")))}</p>
            <p><b>Status:</b> <span style="color: {'green' if rule.get('status') == 'success' else 'red'};">
                {html.escape(str(rule.get("status", "unknown")))}</span></p>
            <p><b>Message:</b> {html.escape(str(rule.get("message", "No message provided")))}</p>
            <p><b>Description:</b> {html.escape(str(rule.get("description", "No description provided")))}</p>
            {format_details(rule.get("details", {}))}
        </div>
        """

    def format_details(details):
        """
        Formatea los detalles de una regla (si existen) en HTML.
        """
        if not details:
            return ""
        details_html = "<ul>"
        for key, value in details.items():
            details_html += f"<li><b>{html.escape(str(key))}:</b> {html.escape(str(value))}</li>"
        details_html += "</ul>"
        return f"<p><b>Details:</b></p>{details_html}"

    # Formatear las reglas comunes
    common_rules_html = ""
    for rule in validation_results.get("common_rules", []):
        common_rules_html += format_rule(rule)

    # Formatear las reglas por modelo
    model_rules_html = ""
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
