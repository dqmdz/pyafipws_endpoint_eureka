import os
import py_eureka_client.eureka_client as eureka_client

from dotenv import load_dotenv
from flask import Flask, request, jsonify

from app.logger_setup import logger
from app.factura_electronica import facturar

load_dotenv()

production = True if os.getenv('PRODUCTION') == "TRUE" else False
eureka_port = int(os.getenv('EUREKA_PORT', 8761))
instance_port = int(os.getenv('INSTANCE_PORT', 5000))
cert_date = os.getenv('CERT_DATE', '2019-01-01')

logger.info(f'production={production}/{os.getenv("PRODUCTION")}')
logger.info(f'eureka_port={eureka_port}/{os.getenv("EUREKA_PORT")}')
logger.info(f'instance_port={instance_port}/{os.getenv("INSTANCE_PORT")}')
logger.info(f'cert_date={cert_date}/{os.getenv("CERT_DATE")}')

app = Flask(__name__)

eureka_client.init(eureka_server=f'http://eureka-service:{eureka_port}',
                   app_name='pyafipws-service',
                   instance_port=instance_port)

@app.route('/api/afipws/test', methods=['GET'])
def test():
    logger.info("test")
    return jsonify({"test": "ok"})

@app.route('/api/afipws/facturador', methods=['POST'])
def facturador():
    logger.info("facturando ...")
    try:
        # obtiene los datos JSON del cuerpo de la solicitud
        json_data = request.get_json()

        logger.info(f"json_data={json_data}")

        # Verifica si es un JSON válido
        if json_data is None:
            return jsonify({"error": "No se proporcionó un JSON válido"}), 400

        logger.info("llamando a facturar ...")
        json_data = facturar(json_data, production=production)

        logger.info(f"json_data (after)={json_data}")

        return jsonify(json_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)