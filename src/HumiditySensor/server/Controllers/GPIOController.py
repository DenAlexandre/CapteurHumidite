import os
import sys
import time
import ctypes
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import const
sys.path.append(os.path.join(os.path.dirname(__file__), '../Util'))
import Util.SusiAPI as SusiAPI


class GPIOController():
    def __new__(self, parent):
        self.controler = parent
        self.initGPIO = False
        print("Creating instance JGPIOController")
        return super(GPIOController, self).__new__(self)

    def __init__(self, parent):
        self.controler = parent
        self.init_gpio()
        print("Init is called")

    def init_gpio(self):
        try:
            # SusiGPIOGetCaps
            # SusiGPIOGetDirection
            # SusiGPIOGetLevel
            # SusiGPIOIntGetEdge
            # SusiGPIOIntGetPin
            # SusiGPIOIntRegister
            # SusiGPIOIntSetEdge
            # SusiGPIOIntSetPin
            # SusiGPIOIntUnRegister
            # SusiGPIOSetDirection
            # SusiGPIOSetLevel
            self.controler.mutexGPIO.lock()

            status: ctypes.c_uint32 = SusiAPI.SusiLib.PySusiLibInitialize()
            hexstatus = self.hexa_conv(status)
            if (hexstatus == self.hexa_conv(SusiAPI.SusiStatus.SUSI_STATUS_ERROR)) \
                    | (hexstatus == self.hexa_conv(SusiAPI.SusiStatus.SUSI_STATUS_NOT_INITIALIZED)):
                raise Exception('L initialisation du port GPIO a échouée !')
            elif hexstatus == self.hexa_conv(SusiAPI.SusiStatus.SUSI_STATUS_SUCCESS):
                self.controler.loggerCtrl.WriteLogger(const.LoggerTypeEnum.Info, "L initialisation du Driver SUSI est ok")

            #permet la remise à 0 de toutes les sorties
            for i in range(const.GPIO_PORT_MAX_NUMBER):
                self.reset_pin(i)

            self.initGPIO = True
        except Exception as exc:
            self.initGPIO = False
            self.controler.loggerCtrl.WriteLogger(const.LoggerTypeEnum.Error, str(exc))
        finally:
            self.controler.mutexGPIO.unlock()

    def send_command_sign_of_life(self, pin):
        try:
            self.send_command_creneau(pin, const.GPIO_TIME_CRENEAU)
            self.controler.loggerCtrl.WriteLogger(const.LoggerTypeEnum.Info, "Envoi du signal signe de vie ok")
        except Exception as exc:
            self.controler.loggerCtrl.WriteLogger(const.LoggerTypeEnum.Error, str(exc))

    def send_command_desactivate(self, pin):
        self.send_command_creneau(pin, const.GPIO_TIME_CRENEAU)
        self.send_command_creneau(pin, const.GPIO_TIME_CRENEAU)

    def send_command_activate(self, pin):
        self.send_command_creneau(pin, const.GPIO_TIME_CRENEAU)

    def send_command_creneau(self, pin, time_creneau):
        try:
            self.controler.mutexGPIO.lock()
            id = pin  # 0 pin 0
            mask = 1  # 1 : mask
            dirinput = 0  # 0 : output
            if self.initGPIO:
                value = 1  # 0 : valeure
                status = SusiAPI.SusiLib.PySusiGPIOSetLevel(id, mask, value)
                if self.hexa_conv(status) == self.hexa_conv(SusiAPI.SusiStatus.SUSI_STATUS_ERROR):
                    raise Exception('Le port n est pas initialisé !')
                #elif self.hexa_conv(status) == self.hexa_conv(SusiAPI.SusiStatus.SUSI_STATUS_SUCCESS):
                #    self.controler.loggerCtrl.WriteLogger(const.LoggerTypeEnum.Info, "Le port " + str(id) + " est à l'état " + str(value))
                # Attente de 50 ms
                time.sleep(time_creneau)
                value = 0  # 0 : valeure
                status = SusiAPI.SusiLib.PySusiGPIOSetLevel(id, mask, value)
                if self.hexa_conv(status) == self.hexa_conv(SusiAPI.SusiStatus.SUSI_STATUS_ERROR):
                    raise Exception('Le port n est pas initialisé !')
                #elif self.hexa_conv(status) == self.hexa_conv(SusiAPI.SusiStatus.SUSI_STATUS_SUCCESS):
                #    self.controler.loggerCtrl.WriteLogger(const.LoggerTypeEnum.Info, "Le port " + str(id) + " est à l'état " + str(value))

                # Attente de 50 ms
                time.sleep(time_creneau)

            else:
                raise Exception('Le port GPIO n est pas initialisé !')

        except Exception as exc:
            self.controler.loggerCtrl.WriteLogger(const.LoggerTypeEnum.Error, str(exc))
        finally:
            self.controler.mutexGPIO.unlock()


    def reset_pin(self, pin):
        id = pin  # 0 pin 0
        mask = 1  # 1 : mask
        dirinput = 0  # 0 : output
        if self.initGPIO:

            status = SusiAPI.SusiLib.PySusiGPIOSetDirection(id, mask, dirinput)
            if self.hexa_conv(status) == self.hexa_conv(SusiAPI.SusiStatus.SUSI_STATUS_NOT_INITIALIZED):
                raise Exception("Le port " + str(id) + "  n est pas initialisé !")
            elif self.hexa_conv(status) == self.hexa_conv(SusiAPI.SusiStatus.SUSI_STATUS_SUCCESS):
                self.controler.loggerCtrl.WriteLogger(const.LoggerTypeEnum.Error,
                                                  "Le port " + str(id) + " est configuré en sortie")

            value = 0  #0:valeure
            status = SusiAPI.SusiLib.PySusiGPIOSetLevel(id, mask, value)
            if self.hexa_conv(status) == self.hexa_conv(SusiAPI.SusiStatus.SUSI_STATUS_ERROR):
                raise Exception('Le port n est pas initialisé !')
            elif self.hexa_conv(status) == self.hexa_conv(SusiAPI.SusiStatus.SUSI_STATUS_SUCCESS):
                self.controler.loggerCtrl.WriteLogger(const.LoggerTypeEnum.Error,
                                                  "Le port " + str(id) + " est à l'état " + str(value))


    @staticmethod
    def hexa_conv(number):
        return "{0:08x}".format(number)

