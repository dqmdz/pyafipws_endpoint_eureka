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
CACHE = "cache"


def facturar(json_data: dict, production: bool = False):
    """Rutina para emitir facturas electrónicas en PDF c/CAE AFIP Argentina"""

    URL_WSAA = URL_WSAA_PROD if production else URL_WSAA_HOMO
    logger.info(f'url_wsaa={URL_WSAA}')
    URL_WSFEv1 = URL_WSFEv1_PROD if production else URL_WSFEv1_HOMO
    logger.info(f'url_wsfev1={URL_WSFEv1}')

    # inicialización AFIP:
    wsaa = WSAA()
    wsfev1 = WSFEv1()
    logger.info("autenticando ...")

    # obtener ticket de acceso (token y sign):
    ta = wsaa.Autenticar(
        "wsfe", CERT, PRIVATEKEY, wsdl=URL_WSAA, cache=CACHE, debug=True
    )
    logger.info("... autenticado")
    wsfev1.Cuit = CUIT
    wsfev1.SetTicketAcceso(ta)
    wsfev1.Conectar(CACHE, URL_WSFEv1)

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
    return json_data


class Comprobante:
    def __init__(self, **kwargs):
        self.encabezado = dict(
            tipo_doc=99,
            nro_doc=0,
            tipo_cbte=0,
            cbte_nro=None,
            punto_vta=0,
            fecha_cbte=None,
            imp_total=0.00,
            imp_tot_conc=0.00,
            imp_neto=0.00,
            imp_trib=0.00,
            imp_op_ex=0.00,
            imp_iva=0.00,
            moneda_id="PES",
            moneda_ctz=1.000,
            obs="",
            concepto=1,
            fecha_serv_desde=None,
            fecha_serv_hasta=None,
            fecha_venc_pago=None,
            nombre_cliente="",
            domicilio_cliente="",
            localidad="",
            provincia="",
            pais_dst_cmp=0,
            id_impositivo="",
            forma_pago="",
            obs_generales="",
            obs_comerciales="",
            motivo_obs="",
            cae="",
            resultado="",
            fch_venc_cae="",
            asociado_tipo_afip=None,
            asociado_punto_venta=None,
            asociado_numero_comprobante=None,
            asociado_fecha_comprobante=None,
        )
        self.encabezado.update(kwargs)
        if self.encabezado["fecha_serv_desde"] or self.encabezado["fecha_serv_hasta"]:
            self.encabezado["concepto"] = 3  # servicios
        self.cmp_asocs = []
        self.ivas = {}

    def agregar_iva(self, iva_id, base_imp, importe):
        iva = self.ivas.setdefault(
            iva_id, dict(iva_id=iva_id, base_imp=0.0, importe=0.0)
        )
        iva["base_imp"] += base_imp
        iva["importe"] += importe
        logger.info(self.ivas)

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

        # datos generales del comprobante:
        logger.info("buscando número ...")
        if not self.encabezado["cbte_nro"]:
            # si no se especifíca nro de comprobante, autonumerar:
            ult = wsfev1.CompUltimoAutorizado(
                self.encabezado["tipo_cbte"], self.encabezado["punto_vta"]
            )
            self.encabezado["cbte_nro"] = int(ult) + 1

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
            logger.info(wsfev1.ErrMsg)
            raise RuntimeError(wsfev1.ErrMsg)

        for obs in wsfev1.Observaciones:
            warnings.warn(obs)

        assert wsfev1.Resultado == "A"  # Aprobado!
        assert wsfev1.CAE
        assert wsfev1.Vencimiento

        self.encabezado["resultado"] = wsfev1.Resultado
        self.encabezado["cae"] = wsfev1.CAE
        self.encabezado["fch_venc_cae"] = wsfev1.Vencimiento
        return True


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