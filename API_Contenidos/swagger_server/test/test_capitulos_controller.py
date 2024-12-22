# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from ..models.capitulo import Capitulo  # noqa: E501
from ..test import BaseTestCase


class TestCapitulosController(BaseTestCase):
    """CapitulosController integration test stubs"""

    def test_series_id_temporadas_temporada_id_capitulos_get(self):
        """Test case for series_id_temporadas_temporada_id_capitulos_get

        Obtener todos los capítulos de una temporada específica
        """
        response = self.client.open(
            '/series/{id}/temporadas/{temporadaId}/capitulos'.format(id='id_example', temporadaId='temporada_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
