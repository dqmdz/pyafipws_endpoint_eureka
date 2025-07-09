#!/usr/bin/python
# -*- coding: utf8 -*-
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTIBILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
from pyafipws.wsaa import WSAA
from pyafipws.wsfev1 import WSFEv1

from app.logger_setup import logger

"Ejemplo completo para WSFEv1 de AFIP (Factura Electrónica Mercado Interno)"

__author__ = "Daniel Quinteros from Mariano Reingart <reingart@gmail.com>"
__copyright__ = "Copyright (C) 2010 - 2019 Mariano Reingart"
__license__ = "GPL 3.0"

import os
import datetime
import warnings
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List
from decimal import Decimal
import http.client as http_client
import logging

http_client.HTTPConnection.debuglevel = 1
logging.getLogger('urllib3').setLevel(logging.DEBUG)

load_dotenv()

URL_WSAA_HOMO = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms?wsdl"
URL_WSAA_PROD = "https://wsaa.afip.gov.ar/ws/services/LoginCms?wsdl"
URL_WSFEv1_HOMO = "https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL"
URL_WSFEv1_PROD = "https://servicios1.afip.gov.ar/wsfev1/service.asmx?WSDL"
CUIT = os.getenv("CUIT")
logger.info(f'cuit={CUIT}')
CERT = os.getenv("CERT")
logger.info(f'cert={CERT}')
PRIVATEKEY = os.getenv("PRIVATEKEY")
logger.info(f'privatekey={PRIVATEKEY}')
CACHE = ""
# CACHE = "cache"


def facturar(json_data: Dict[str, Any], production: bool = False) -> Dict[str, Any]:
    """
    Emite facturas electrónicas con CAE AFIP Argentina
    
    Args:
        json_data: Datos de la factura
        production: Si es True usa ambiente de producción, sino homologación
        
    Returns:
        Dict con los datos de la factura autorizada
    
    Raises:
        ValueError: Si faltan datos requeridos
        RuntimeError: Si hay error en la comunicación con AFIP
    """
    logger.debug(f"Iniciando facturación con datos: {json_data}")

    # Validar datos requeridos
    required_fields = ['tipo_afip', 
                       'punto_venta', 
                       'tipo_documento', 
                       'documento', 
                       'total',
                       'id_condicion_iva']
    if not all(field in json_data for field in required_fields):
        missing_fields = [field for field in required_fields if field not in json_data]
        logger.error(f"Faltan campos requeridos: {missing_fields}")
        raise ValueError(f"Faltan campos requeridos: {missing_fields}")

    try:
        URL_WSAA = URL_WSAA_PROD if production else URL_WSAA_HOMO
        URL_WSFEv1 = URL_WSFEv1_PROD if production else URL_WSFEv1_HOMO
        logger.info(f"Usando URLs - WSAA: {URL_WSAA}, WSFEv1: {URL_WSFEv1}")
        
        # inicialización AFIP:
        wsaa = WSAA()
        wsfev1 = WSFEv1()
        logger.info("autenticando ...")

        # Agregar más logging para debug
        try:
            ta = wsaa.Autenticar(
                "wsfe", CERT, PRIVATEKEY, wsdl=URL_WSAA, cache=CACHE, debug=True
            )
            logger.info(f"Token de acceso obtenido: {ta}")
        except Exception as auth_error:
            logger.error(f"Error en autenticación: {str(auth_error)}")
            raise

        logger.info("asignando cuit ... ")
        wsfev1.Cuit = CUIT
        logger.info("asignando ticket de acceso ...")
        wsfev1.SetTicketAcceso(ta)
        logger.info("conectando ...")
        wsfev1.Conectar(CACHE, URL_WSFEv1)
        logger.info("... conectado")

        # recorrer los json_data a facturar, solicitar CAE y generar el PDF:
        hoy = datetime.date.today().strftime("%Y%m%d")
        logger.info("creando comprobante ...")
        cbte = Comprobante(
            tipo_cbte=json_data.get("tipo_afip"),
            punto_vta=json_data.get("punto_venta"),
            fecha_cbte=hoy,
            cbte_nro=json_data.get("nro"),
            tipo_doc=json_data.get("tipo_documento"),
            nro_doc=json_data.get("documento"),
            imp_total=json_data.get("total"),
            imp_neto=round(json_data.get("neto", 0) + json_data.get("neto105", 0), 2),
            imp_iva=round(json_data.get("iva", 0) + json_data.get("iva105", 0), 2),
            asociado_tipo_afip=json_data.get("asociado_tipo_afip", None),
            asociado_punto_venta=json_data.get("asociado_punto_venta", None),
            asociado_numero_comprobante=json_data.get("asociado_numero_comprobante", None),
            asociado_fecha_comprobante=json_data.get("asociado_fecha_comprobante", None),
            condicion_iva_receptor_id=json_data.get("id_condicion_iva", None),
        )
        neto = json_data.get("neto")
        iva = json_data.get("iva")
        neto105 = json_data.get("neto105")
        iva105 = json_data.get("iva105")
        if iva > 0:
            logger.info("agregando iva 21 ...")
            cbte.agregar_iva(5, neto, iva)
        if iva105 > 0:
            logger.info("agregando iva 10.5 ...")
            cbte.agregar_iva(4, neto105, iva105)
        if not cbte.encabezado["asociado_numero_comprobante"] is None:
            cbte.agregar_asociado()
        logger.info("autorizando comprobante ...")
        ok = cbte.autorizar(wsfev1)
        nro = cbte.encabezado["cbte_nro"]
        logger.info(f"factura autorizada={nro} cae={cbte.encabezado['cae']}")
        json_data["cae"] = cbte.encabezado["cae"]
        json_data["vencimiento_cae"] = cbte.encabezado["fch_venc_cae"]
        json_data["resultado"] = cbte.encabezado["resultado"]
        json_data["numero_comprobante"] = cbte.encabezado["cbte_nro"]
        json_data["fecha_comprobante"] = cbte.encabezado["fecha_cbte"]
        
        # Logging detallado para debug
        logger.info(f"Resultado final antes de devolver: {json_data}")
        logger.info(f"Tipos de datos: tipo_documento={type(json_data.get('tipo_documento'))}, documento={type(json_data.get('documento'))}, total={type(json_data.get('total'))}")
        
        return json_data

    except Exception as e:
        logger.exception("Error inesperado durante la facturación")
        raise


def consultar_comprobante(tipo_cbte: int, punto_vta: int, cbte_nro: int, production: bool = False) -> Dict[str, Any]:
    """
    Consulta un comprobante emitido en AFIP.

    Args:
        tipo_cbte: Tipo de comprobante.
        punto_vta: Punto de venta.
        cbte_nro: Número de comprobante.
        production: Si es True usa ambiente de producción, sino homologación.

    Returns:
        Dict con los datos del comprobante consultado y el mensaje de AFIP.

    Raises:
        RuntimeError: Si hay un error inesperado en la comunicación con AFIP.
    """
    logger.debug(f"Iniciando consulta de comprobante: tipo={tipo_cbte}, pto_vta={punto_vta}, nro={cbte_nro}")

    try:
        URL_WSAA = URL_WSAA_PROD if production else URL_WSAA_HOMO
        URL_WSFEv1 = URL_WSFEv1_PROD if production else URL_WSFEv1_HOMO
        logger.info(f"Usando URLs - WSAA: {URL_WSAA}, WSFEv1: {URL_WSFEv1}")

        # inicialización AFIP:
        wsaa = WSAA()
        wsfev1 = WSFEv1()
        logger.info("autenticando ...")

        try:
            ta = wsaa.Autenticar(
                "wsfe", CERT, PRIVATEKEY, wsdl=URL_WSAA, cache=CACHE, debug=True
            )
            logger.info(f"Token de acceso obtenido: {ta}")
        except Exception as auth_error:
            logger.error(f"Error en autenticación: {str(auth_error)}")
            raise

        logger.info("asignando cuit ... ")
        wsfev1.Cuit = CUIT
        logger.info("asignando ticket de acceso ...")
        wsfev1.SetTicketAcceso(ta)
        logger.info("conectando ...")
        wsfev1.Conectar(CACHE, URL_WSFEv1)
        logger.info("... conectado")

        logger.info("consultando comprobante ...")
        wsfev1.CompConsultar(tipo_cbte, punto_vta, cbte_nro)

        if wsfev1.ErrMsg:
            # Si el error es que no existe, lo manejamos como un caso de negocio, no un error del sistema.
            if "602:" in wsfev1.ErrMsg:
                logger.warning(f"Comprobante no encontrado en AFIP: {wsfev1.ErrMsg}")
                return {"mensaje": wsfev1.ErrMsg, "factura": None}
            else:
                logger.error(f"Error de AFIP al consultar: {wsfev1.ErrMsg}")
                raise RuntimeError(wsfev1.ErrMsg)

        mensaje_afip = "Comprobante encontrado."
        if wsfev1.Obs:
            mensaje_afip += f" Observaciones: {wsfev1.Obs}"

        logger.info(f"Consulta exitosa: {wsfev1.factura}")
        return {"mensaje": mensaje_afip, "factura": wsfev1.factura}

    except Exception as e:
        logger.exception("Error inesperado durante la consulta del comprobante")
        raise


class Comprobante:
    def __init__(self, **kwargs: Any) -> None:
        logger.debug(f"Inicializando comprobante con kwargs: {kwargs}")
        self.encabezado: Dict[str, Any] = {
            "tipo_doc": 99,
            "nro_doc": 0,
            "tipo_cbte": 0,
            "cbte_nro": None,
            "punto_vta": 0,
            "fecha_cbte": None,
            "imp_total": 0.00,
            "imp_tot_conc": 0.00,
            "imp_neto": 0.00,
            "imp_trib": 0.00,
            "imp_op_ex": 0.00,
            "imp_iva": 0.00,
            "moneda_id": "PES",
            "moneda_ctz": 1.000,
            "obs": "",
            "concepto": 1,
            "fecha_serv_desde": None,
            "fecha_serv_hasta": None,
            "fecha_venc_pago": None,
            "nombre_cliente": "",
            "domicilio_cliente": "",
            "localidad": "",
            "provincia": "",
            "pais_dst_cmp": 0,
            "id_impositivo": "",
            "forma_pago": "",
            "obs_generales": "",
            "obs_comerciales": "",
            "motivo_obs": "",
            "cae": "",
            "resultado": "",
            "fch_venc_cae": "",
            "asociado_tipo_afip": None,
            "asociado_punto_venta": None,
            "asociado_numero_comprobante": None,
            "asociado_fecha_comprobante": None,
            "condicion_iva_receptor_id": 5,
        }
        self.encabezado.update(kwargs)
        if self.encabezado["fecha_serv_desde"] or self.encabezado["fecha_serv_hasta"]:
            self.encabezado["concepto"] = 3  # servicios
        self.cmp_asocs: List[Dict[str, Any]] = []
        self.ivas: Dict[int, Dict[str, Any]] = {}
        
        # Validar valores críticos
        self._validate_encabezado()
        
    def _validate_encabezado(self) -> None:
        """Valida los datos críticos del encabezado"""
        if self.encabezado['imp_total'] <= 0:
            raise ValueError("El importe total debe ser mayor a 0")

    def agregar_iva(self, iva_id: int, base_imp: Decimal, importe: Decimal) -> None:
        logger.info(f"Agregando IVA - ID: {iva_id}, Base: {base_imp}, Importe: {importe}")
        try:
            # Asegurarse que los valores sean Decimal
            base_imp = Decimal(str(base_imp)) if not isinstance(base_imp, Decimal) else base_imp
            importe = Decimal(str(importe)) if not isinstance(importe, Decimal) else importe
            
            iva = self.ivas.setdefault(
                iva_id,
                {'iva_id': iva_id, 'base_imp': Decimal('0'), 'importe': Decimal('0')}
            )
            iva['base_imp'] += base_imp
            iva['importe'] += importe
            logger.info(f"IVA agregado exitosamente. Estado actual: {self.ivas}")
        except Exception as e:
            logger.error(f"Error al agregar IVA: {str(e)}")
            raise

    def agregar_asociado(self):
        self.cmp_asocs.append(
            {
                "tipo": self.encabezado["asociado_tipo_afip"],
                "pto_vta": self.encabezado["asociado_punto_venta"],
                "nro": self.encabezado["asociado_numero_comprobante"],
                "cuit": CUIT,
                "fecha": self.encabezado["asociado_fecha_comprobante"],
            }
        )

    def autorizar(self, wsfev1):
        logger.info("Iniciando proceso de autorización")
        try:
            # datos generales del comprobante:
            if not self.encabezado["cbte_nro"]:
                # si no se especifíca nro de comprobante, autonumerar:
                ult = wsfev1.CompUltimoAutorizado(
                    self.encabezado["tipo_cbte"], 
                    self.encabezado["punto_vta"]
                )
                self.encabezado["cbte_nro"] = int(ult) + 1
                logger.info(f"Número de comprobante asignado: {self.encabezado['cbte_nro']}")

            self.encabezado["cbt_desde"] = self.encabezado["cbte_nro"]
            self.encabezado["cbt_hasta"] = self.encabezado["cbte_nro"]
            logger.info("creando factura ...")
            wsfev1.CrearFactura(**self.encabezado)

            # agrego un comprobante asociado (solo notas de crédito / débito)
            logger.info("agregando asociados ...")
            for cmp_asoc in self.cmp_asocs:
                wsfev1.AgregarCmpAsoc(**cmp_asoc)

            # agrego el subtotal por tasa de IVA (iva_id 5: 21%):
            logger.info("agregandos ivas ...")
            for iva in self.ivas.values():
                wsfev1.AgregarIva(**iva)

            # llamo al websevice para obtener el CAE:
            logger.info("solicitando ...")
            wsfev1.CAESolicitar()

            if wsfev1.ErrMsg:
                logger.error(f"Error de AFIP: {wsfev1.ErrMsg}")
                raise RuntimeError(wsfev1.ErrMsg)

            if wsfev1.Observaciones:
                logger.warning(f"Observaciones de AFIP: {wsfev1.Observaciones}")

            assert wsfev1.Resultado == "A"  # Aprobado!
            assert wsfev1.CAE
            assert wsfev1.Vencimiento

            self.encabezado["resultado"] = wsfev1.Resultado
            self.encabezado["cae"] = wsfev1.CAE
            self.encabezado["fch_venc_cae"] = wsfev1.Vencimiento
            
            logger.info(f"Autorización exitosa - CAE: {wsfev1.CAE}, Vencimiento: {wsfev1.Vencimiento}")
            return True
            
        except Exception as e:
            logger.exception("Error durante la autorización del comprobante")
            raise


if __name__ == "__main__":
    json_data = {
        "tipo_documento": 96,
        "documento": "22222222",
        "tipo_afip": 6,
        "punto_venta": 4000,
        "total": 121.0,
        "exento": 0,
        "neto": 100.0,
        "neto105": 0,
        "iva": 21.0,
        "iva105": 0,
    }
    facturar(json_data, production=False)