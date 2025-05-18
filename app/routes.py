import json
from flask import Blueprint, jsonify, request, Response
from app.logger_setup import logger
from app.factura_electronica import facturar
from typing import Dict

# Crear el blueprint con el prefijo base
afipws_bp = Blueprint('afipws', __name__, url_prefix='/api/afipws')

def register_routes(config: Dict) -> Blueprint:
    """Configura y retorna el blueprint con todas las rutas."""
    
    @afipws_bp.route('/test', methods=['GET'])
    def test() -> Response:
        """Endpoint de prueba."""
        logger.info("test")
        return jsonify({"test": "ok"})

    @afipws_bp.route('/facturador', methods=['POST'])
    def facturador() -> Response:
        """Endpoint para procesar facturas."""
        logger.info("facturando ...")
        try:
            json_data = request.get_json()
            
            if json_data is None:
                return jsonify({"error": "No se proporcionó un JSON válido"}), 400
            
            logger.info(f"json_data=\n{json.dumps(json_data, indent=2)}")
            logger.info("llamando a facturar ...")
            
            result = facturar(json_data, production=config['production'])
            logger.info(f"json_data (after)={result}")
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f'Error al facturar: {str(e)}')
            return jsonify({"error": str(e)}), 500
    
    return afipws_bp