# -*- coding: utf-8 -*-
"""
SFX Helper – Registrierung des Dockers bei Krita.

Krita lädt dieses Paket anhand der mangasfx.desktop-Datei
(X-KDE-Library=mangasfx) und führt diesen Code beim Start aus.
"""
from krita import Krita, DockWidgetFactory, DockWidgetFactoryBase
from .sfx_docker import MangaSFXDocker

# Eindeutige ID des Dockers (muss innerhalb von Krita einmalig sein)
DOCKER_ID = "mangaSfxDocker"

# Die Dock-Position wird je nach Krita-/sip-Version unterschiedlich
# bereitgestellt – beide Schreibweisen abfangen.
try:
    _DOCK_RIGHT = DockWidgetFactoryBase.DockPosition.DockRight
except AttributeError:
    _DOCK_RIGHT = DockWidgetFactoryBase.DockRight

Krita.instance().addDockWidgetFactory(
    DockWidgetFactory(DOCKER_ID, _DOCK_RIGHT, MangaSFXDocker)
)
