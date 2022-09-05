#!/bin/bash
python setup.py install
scp {path/to/Factorio/mods} "C:/Users/{user}/AppData/Local/Programs/Python/Python{version}/Lib/site-packages/factorio_draftsman-{factorio.draftsman.version}-py{python.version}.egg/draftsman/factorio-mods/"
python up_script.py
