import config, subprocess, os

subprocess.Popen("{0} {1}".format(config.open, os.path.join(config.marvelData, "docx", "new.dotx")), shell=True)