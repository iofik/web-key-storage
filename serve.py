#!/usr/bin/env python

from weks.app import app

from bottle import debug
debug(True)
app.run()
