import glob, os, sys, logging
from uniquebible import config
import logging.handlers as handlers
from uniquebible.util.FileUtil import FileUtil


def cleanupTempFiles():
    files = glob.glob(os.path.join("htmlResources", "main-*.html"))
    for file in files:
        os.remove(file)

# Run startup plugins
def runStartupPlugins():
    if config.enablePlugins:
        for plugin in FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "startup"), "py"):
            if not plugin in config.excludeStartupPlugins:
                script = os.path.join(os.getcwd(), "plugins", "startup", "{0}.py".format(plugin))
                config.mainWindow.execPythonFile(script)

# Check if database migration is needed
def checkMigration():
    if config.version >= 0.56 and not config.databaseConvertedOnStartup:
        from uniquebible.db.BiblesSqlite import BiblesSqlite
        try:
            print("Updating database ... please wait ...")
            biblesSqlite = BiblesSqlite()
            biblesWithBothVersions = biblesSqlite.migratePlainFormattedBibles()
            if biblesWithBothVersions:
                biblesSqlite.proceedMigration(biblesWithBothVersions)
            if config.migrateDatabaseBibleNameToDetailsTable:
                biblesSqlite.migrateDatabaseContent()
            del biblesSqlite
            config.databaseConvertedOnStartup = True
            print("Updated!")
        except:
            pass

def printContentOnConsole(text):
    if not "html-text" in sys.modules:
        import html_text
    print(html_text.extract_text(text))
    #subprocess.Popen(["echo", html_text.extract_text(text)])
    #sys.stdout.flush()
    return text


# clean up
cleanupTempFiles()

# Setup logging
logger = logging.getLogger('uba')
if config.enableLogging:
    logger.setLevel(logging.DEBUG)
    logHandler = handlers.TimedRotatingFileHandler('uba.log', when='D', interval=1, backupCount=0)
    logHandler.setLevel(logging.DEBUG)
    logger.addHandler(logHandler)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
else:
    logger.addHandler(logging.NullHandler())

def global_excepthook(type, value, traceback):
    logger.error("Uncaught exception", exc_info=(type, value, traceback))
    print(traceback.format_exc())

sys.excepthook = global_excepthook