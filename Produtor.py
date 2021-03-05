import platform
import Pyro4
import datetime
import multiprocessing
import subprocess
import os
import random

SenhaNoLinux = "senhasenha"

manager = multiprocessing.Manager()
consumidores = manager.list()
IP = "192.168.2.2"

def log(logString):
    log = open("logProdutor.txt", "a")
    log.write(logString)

@Pyro4.expose #A exposição de classes, métodos e propriedades é feita usando esse comando. Ele permite que os itens fiquem disponíveis para o acesso remoto.
class Produtor:


    @property
    def arq(self):  #Para pegar o arquivo (get)
        return self.__arq
    @arq.setter
    def arquivo(self, novo_arquivo):
        self.__arq = novo_arquivo

    def __init__(self): #Construtor da classe produtor que também já realiza o carregamento do arquivo

        NomedoArquivo = str(random.randrange(1, 5)) + ".txt" #arquivo que será carregado
        print(f"O arquivo que será carregado pelo produtor é: {NomedoArquivo}")
        #Abrindo e lendo o arquivo
        file = open(NomedoArquivo, "r")
        read = file.read()
        self.__arq = read
        logString = "Nome do Arquivo Lido: " + NomedoArquivo + ";"
        log(logString + "\n")

    def adicionarConsumidorNProdutor(self, cons): #Os consumidores serão adicionados em uma lista
        consumidores.append(cons)
        print("ADD C no P:", cons)
        logString = "ADD Consumidor no Produtor: " + str(cons) + ";"
        log(logString + "\n")


    def removerConsumidorNProdutor(self, cons): #Os consumidores serão removidos da lista
        if cons in consumidores:
            consumidores.remove(cons)
            print("Remove consumidor no produtor: ", cons)
            logString = "Remove consumidor no produtor: " + str(cons) + ";"
            log(logString + "\n")

    def CorrigindoaHora(self, horaNova):

        logString = "Hora do servidor: " + str(horaNova) + ";"
        log(logString + "\n")
        logString = "Hora do Produtor: " + str(datetime.datetime.now().strftime("%H:%M:%S")) + ";"
        log(logString + "\n")

        if platform.system() == 'Windows': #Verifica se o sistema operacional é o Windows, se for irá alterar a hora nele
            hora = "@echo off \n" + "if not \"%1\"==\"am_admin\" (powershell start -verb runas '%0' am_admin & exit /b) \n" + \
                    "time " + horaNova
            f = open("time.bat", 'w')
            f.write(hora)
            f.close()
            subprocess.call("time.bat")
            logString = "Nova Hora no Produtor: " + str(datetime.datetime.now().strftime("%H:%M:%S")) + ";" + ";"
            log(logString + "\n")
        else: #se não for Windows, alterará a hora no outro Sistema operacional, no caso, o Linux
            os.system("echo " + SenhaNoLinux + " | sudo -S date +%T -s " + horaNova)
            logString = "Nova Hora no Produtor: " +  str(datetime.datetime.now().strftime("%H:%M:%S")) + ";"
            log(logString + "\n")

    def retornaroArq(self): #retornará o arquivo
        return self.arq

def main(): #Principal

    try: #Fazendo a conexão no Gerenciador de Notificações
        prod = Produtor()
        ns = Pyro4.locateNS(host = IP, port = 9090) #atributo do objeto na rede

        uri = ns.lookup("Servidor") #identificador de objetos na rede
        print("URI :", uri)
        print("NS :", ns)

        logString = "Gerenciador de Not em Produtor -> URI:" + str(uri) + "," + " NS" + str(ns) + " ;" #log
        log(logString + "\n")

        produtorGerenciadordeNot = Pyro4.Proxy(uri) # Referencia os objetos conectados na rede
        nomeSp = str(ns)
        produtorGerenciadordeNot.adicionarProdutor(nomeSp) #O produtor será adicionado em uma lista do servidor
        logString = "Gerenciador de Not em Produtor -> Adicionou na lista do servidor ;"
        log(logString + "\n")

        #corrigindo as horas:
        HoraServidor = produtorGerenciadordeNot.retornaHora()
        print("Hora do Servidor:", HoraServidor)
        print("Hora do Produtor:", datetime.datetime.now().strftime("%H:%M:%S"))
        prod.CorrigindoaHora(HoraServidor)
        print("Nova Hora do Produtor:", datetime.datetime.now().strftime("%H:%M:%S"))
    
    except:
        print(ValueError)
        exit(0)

    try: # Criando um objeto exposto

        daemon = Pyro4.Daemon(host = IP)
        uri = daemon.register(Produtor)
        ns = Pyro4.locateNS()
        # Registrando o objetoProdutor na rede
        ns.register(nomeSp, uri)
        logString = "Servidor Produtor Inicializado -> URI:" + str(uri) + "," + " NS" + str(ns) + ";" #log
        log(logString + "\n")
        print("\"REDE\" que o consumidor se conectará \n", nomeSp)
        logString = "Rede que o consumidor conectará:" + str(nomeSp) + ";"
        log(logString + "\n")
        daemon.requestLoop() # O servidor seguirá ativado!

    except ValueError:
        print(ValueError)
        print("Erro!")
        exit(0)
if __name__ == '__main__':
    main()
