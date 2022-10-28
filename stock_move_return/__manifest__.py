# Copyright 2022 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

{
    "name": "Stock Move Return",
    "summary": """
        This Module can return the Stock Moves and update the Sale Order Line""",
    "version": "15.0.1.0.0",
    "category": "Uncategorized",
    "website": "http://sodexis.com/",
    "author": "Sodexis",
    "license": "OPL-1",
    "installable": True,
    "application": False,
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_move_return_views.xml",
    ],
}
