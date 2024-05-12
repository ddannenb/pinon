Conda env: pinon-py3-11:

Versions:
conda: 24.4.4
python: 3.11.9
notebook: 7.0.8 with jupyter-server: 2.1.0, jupyter-core: 5.5.0
pandas: 2.2.1
numpy: 1.26.4
scipy: 1.13.0
openpyxl: 3.1.2
pytest: 7.4.0


Issue with python debugger crashing when debugging auto reload module from Jupyter notebook.  This a version issue with debugpy.  pip uninstall/install debugpy to co
rrect.