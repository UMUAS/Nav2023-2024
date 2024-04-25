[loggers]
keys=root

[handlers]
keys=fileHandler,consoleHandler

[formatters]
keys=standardFormatter

[logger_root]
level=DEBUG
handlers=fileHandler,consoleHandler

[handler_fileHandler]
class=FileHandler
level=DEBUG
formatter=standardFormatter
args=("{{ log_file_path }}", "a")

[handler_consoleHandler]
class=StreamHandler
level=DEBUG
args=(sys.stdout,)

[formatter_standardFormatter]
format=%(asctime)s - %(levelname)s - %(message)s
datefmt=%b-%d-%y %H:%M:%S
