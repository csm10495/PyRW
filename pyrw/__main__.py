
from pyrw.rwe import ReadWriteEverything

rwe = ReadWriteEverything()
header='''
| --------------------------------------------- |
| rwe object has been created for your usage... |
| %-45s |
| --------------------------------------------- |''' % rwe.getRWEVersion()
print(header)

try:
    import IPython
    start_interactive = lambda: IPython.embed(display_banner=False)
except ImportError:
    print("| Install IPython to have a more complete       |")
    print("|     interactive experience.                   |")
    print("| --------------------------------------------- |")
    import code
    start_interactive = lambda: code.interact(banner='', local=dict(rwe=rwe))

start_interactive()
