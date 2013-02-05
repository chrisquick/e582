For python(x,y)

python setup_pythonxy.py build --compiler=mingw32
python setup_pythonxy.py install --user

shold install to a directory like:

C:\Users\phil\AppData\Roaming\Python\Python27\site-packages

which the needs to be added to the python path with

site.addsitedir(r'C:\Users\phil\AppData\Roaming\Python\Python27\site-packages')


For EPD:

python setup.py

