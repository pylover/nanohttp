CLI
===


.. code-block:: text

    usage: nanohttp [-h] [-c CONFIG_FILE] [-d CONFIG_DIRECTORY] [-b {HOST:}PORT]
                    [-C DIRECTORY] [-V]
                    [{MODULE{.py}}{:CLASS}]

    positional arguments:
      {MODULE{.py}}{:CLASS}
                            The python module and controller class to launch.
                            default is python built-in's : `demo_app`, And the
                            default value for `:CLASS` is `:Root` if omitted.

    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG_FILE, --config-file CONFIG_FILE
                            This option may be passed multiple times.
      -d CONFIG_DIRECTORY, --config-directory CONFIG_DIRECTORY
                            This option may be passed multiple times.
      -b {HOST:}PORT, --bind {HOST:}PORT
                            Bind Address. default: 8080
      -C DIRECTORY, --directory DIRECTORY
                            Change to this path before starting the server default
                            is: `.`
      -V, --version         Show the version.
