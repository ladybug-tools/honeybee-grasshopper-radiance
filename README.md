[![Build Status](https://github.com/ladybug-tools/honeybee-grasshopper-radiance/workflows/CI/badge.svg)](https://github.com/ladybug-tools/honeybee-grasshopper-radiance/actions)

[![IronPython](https://img.shields.io/badge/ironpython-2.7-red.svg)](https://github.com/IronLanguages/ironpython2/releases/tag/ipy-2.7.8/)

# honeybee-grasshopper-radiance

:honeybee: :green_book: :zap: Honeybee Radiance plugin for Grasshopper (aka. honeybee[+]).

This repository contains all radiance modeling Grasshopper components for the honeybee
plugin. The package includes both the user objects (`.ghuser`) and the Python
source (`.py`). Note that this library only possesses the Grasshopper components
and, in order to run the plugin, the core libraries must be installed in a way that
they can be found by Rhino (see dependencies).

## Dependencies

The honeybee-grasshopper-radiance plugin has the following dependencies on core libraries:

* [ladybug-core](https://github.com/ladybug-tools/ladybug)
* [ladybug-geometry](https://github.com/ladybug-tools/ladybug-geometry)
* [ladybug-comfort](https://github.com/ladybug-tools/ladybug-comfort)
* [ladybug-rhino](https://github.com/ladybug-tools/ladybug-rhino)
* [honeybee-core](https://github.com/ladybug-tools/honeybee-core)
* [honeybee-radiance](https://github.com/ladybug-tools/honeybee-radiance)
* [honeybee-radiance-folder](https://github.com/ladybug-tools/honeybee-radiance-folder)
* [honeybee-radiance-command](https://github.com/ladybug-tools/honeybee-radiance-command)
* [honeybee-standards](https://github.com/ladybug-tools/honeybee-standards)

## Other Required Components

The honeybee-grasshopper-radiance plugin also requires the Grasshopper components within the
following repositories to be installed in order to work correctly:

* [ladybug-grasshopper](https://github.com/ladybug-tools/ladybug-grasshopper)
* [honeybee-grasshopper-core](https://github.com/ladybug-tools/honeybee-grasshopper-core)

## Installation

See the [Wiki of the lbt-grasshopper repository](https://github.com/ladybug-tools/lbt-grasshopper/wiki)
for the installation instructions for the entire Ladybug Tools Grasshopper plugin
(including this repository).
