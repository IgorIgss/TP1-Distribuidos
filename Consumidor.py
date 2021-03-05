import os
import Pyro4
import subprocess
import platform
import datetime
import time

SenhaNoLinux = "senhasenha"
IP = "192.168.2.2"

def log(logString):
    log = open("logConsumidor.txt", "a")
    log.write(logString)

def CorrigindoaHora(horaNova):
        logString = "Hora do Servidor:" + str(horaNova) + ";"
        log(logString)
        logString = "Hora do Consumidor:" + str(datetime.datetime.now().strftime("%H:%M:%S")) + ";"
        log(logString)     

        if platform.system() == 'Windows': #Verifica se o sistema operacional é o Windows, se for irá alterar a hora nele
            hora = "@echo off \n" + "if not \"%1\"==\"am_admin\" (powershell start -verb runas '%0' am_admin & exit /b) \n" + \
                    "time " + horaNova
            f = open("time.bat", 'w')
            f.write(hora)
            f.close()
            subprocess.call("time.bat")
            time.sleep ( 5 )
            logString = "Nova Hora Consumidor:" + str(datetime.datetime.now().strftime("%H:%M:%S")) + ";" + ";"
            log(logString)  

        else: #se não for Windows, alterará a hora no outro Sistema operacional, no caso, o Linux
            os.system("echo " + SenhaNoLinux + " | sudo -S date +%T -s " + horaNova)
            time.sleep ( 5 )
            logString = "Nova Hora Consumidor:" +  str(datetime.datetime.now().strftime("%H:%M:%S")) + ";"
            log(logString)  

def contaPalavras(textoArq):

        textoArq.replace("\t", " ")
        textoArq.replace("\n", " ")
        listadePalavras = textoArq.split(" ")

        print("A quantidade de palavras no arquivo é de :", len(listadePalavras)) # len = quantidade de palavras
        logString = "A quantidade de palavras lidas foram: " + str(len(listadePalavras))
        log(logString + "\n")

def main(): #Principal
    try:
        ns = Pyro4.locateNS(host = IP, port = 9090)
        uri = ns.lookup("Servidor")
        print("URI :", uri)
        print("NS :", ns)

        gerenciadorN = Pyro4.Proxy(uri) # Referencia os objetos conectados na rede
        logString = "Gerenciador de Not em Consumidor -> URI:" + str(uri) + "," + " NS" + str(ns) + " ;"
        log(logString + "\n")
        nomeGerenciadorC = str(ns)
        gerenciadorN.addConsumidorGn(nomeGerenciadorC) # Adicionando em uma lista do servidor
        logString = "Gerenciador de Not em Consumidor -> Adicionou na lista do servidor ;"
        log(logString + "\n")

        # corrigindo as horas:
        HoraServidor = gerenciadorN.retornaHora()
        print("Hora do Servidor:", HoraServidor)
        print("Hora do Consumidor:", datetime.datetime.now().strftime("%H:%M:%S"))
        CorrigindoaHora(HoraServidor)
        print("Nova Hora do Consumidor:", datetime.datetime.now().strftime("%H:%M:%S"))

        while True: #Se conectará com o gerenciador
            conectar = gerenciadorN.escolherProdutor()
            time.sleep ( 5 )  #tempo para um consumidor conectar e inicializar servidor
            if conectar :
                logString = "Consumidor conectará em:" + str(conectar) + ";"
                log(logString + "\n")
                ns = Pyro4.locateNS(host = IP, port = 9090)
                uri = ns.lookup(str(conectar))
                print("URI :", uri)
                print("NS :", ns)
                gerenciadorP = Pyro4.Proxy(uri) # Referencia os objetos conectados na rede
                logString = "Consumidor em Produtor -> URI:" + str(uri) + "," + " NS" + str(ns) + ";"
                log(logString + "\n")
                nomeProdC = str(ns)
                gerenciadorP.addConsumidorProdutor(nomeProdC) # Registrando o objeto na rede
                logString = "Produtor Servidor em Consumidor -> Adicionou na lista do servidor ;"
                log(logString + "\n")

                textoArq = gerenciadorP.retornaArquivo()
                contaPalavras(textoArq) #Contador de palavras irá contar
                gerenciadorP.remConsumidorProdutor(nomeProdC) #produtor será removido
                logString = "Produtor Servidor em Consumidor -> Removeu na lista do servidor ;"
                log(logString + "\n")
                gerenciadorN.remConsumidorGn(nomeGerenciadorC) #consumidor será removido após realizar a contagem
                logString = "Gerenciador de Not em Consumidor -> Removeu na lista do servidor ;"
                log(logString + "\n")
                break

    except ValueError:

        print(ValueError)

if __name__ == "__main__":
    main()
