import glob, os, config
from util.FileUtil import FileUtil


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
        from db.BiblesSqlite import BiblesSqlite
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