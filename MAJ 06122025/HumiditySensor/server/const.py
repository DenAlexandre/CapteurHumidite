import os
from enum import IntEnum, auto, Enum



# ********************************************************************************************
#       Configuration des timers
# ********************************************************************************************
THREAD_API_COMMAND_NAME = "ThreadAPICommand"
THREAD_TOKEN_COMMAND_NAME = "ThreadTokenCommand"
THREAD_SEND_COMMAND_NAME = "ThreadSendCommand"
THREAD_SEND_FILE_COMMAND_NAME = "ThreadSendFileCommand"
THREAD_STATUS_COMMAND_NAME = "ThreadStatusCommand"
THREAD_CONTROL_SERVICE_NAME = "ThreadControlService"
THREAD_GPIO_COMMAND_NAME = "ThreadGPIOCommand"
THREAD_CONTROL_THREAD_NAME = "ThreadControlThread"

THREAD_TOKEN_COMMAND_SLEEP = 43200 #Permet de raffraichier le token - 12 * 60 * 60 = 43200(12 heures)
THREAD_CONTROL_SERVICE_SLEEP = 30 #Demande des mesures, regulation  et ecriture fichier
THREAD_GPIO_COMMAND_SLEEP = 30 #Permet d'envoyer des commandes GPIO en asynchrone

# ********************************************************************************************
#       Configuration du log
# ********************************************************************************************
class LoggerTypeEnum(IntEnum):
    Info = auto()
    Debug = auto()
    Error = auto()



# ********************************************************************************************
#       Configuration du type fichier
# ********************************************************************************************
class TypeLogEnum(Enum):
    LOG_STAT = "temp"
    LOG_ERROR = "error"
