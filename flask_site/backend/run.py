# -*- coding: utf-8 -*-

"""
"""

__author__ = 'lijingang'

from flask_site.backend import app


if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)


