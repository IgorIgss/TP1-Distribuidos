import datetime
import multiprocessing
import Pyro4
import random

manager = multiprocessing.Manager()
produtorGerenciadordeNot = manager.list()
consumidorGerenciadordeNot = manager.list()
IP = "192.168.2.2"


def log(logString):
    log = open("logGerenciadorDeNotificacao.txt", "a")
    log.write(logString)

@Pyro4.expose #A exposição de classes, métodos e propriedades é feita usando esse comando. Ele permite que os itens fiquem disponíveis para o acesso remoto.
@Pyro4.behavior(instance_mode="single") #O controle do modo de instância e da criação é feito decorando sua classe
#Single significa que uma única instância será criada e usada para todas as chamadas de método

class Servidor(object):

    def __init__(self): #Método contrutor do servidor
        print("----- O gerenciador de notificações está ativado -----")
        logString = "Gerenciador Ativo (SERVIDOR PRINCIPAL)"
        log(logString + "\n")


    def adicionarProdutor(self, ns): #função que adiciona um produtor
        produtorGerenciadordeNot.append(ns)
        print("ADD P:", ns)
        logString = "ADD Produtor em GN -> NS:" + str(ns) + " ;"
        log(logString + "\n")

    def removerProdutor(self, ns): #função que remove produtor
        produtorGerenciadordeNot.remove(ns)
        print("REMOVE P:", ns)
        logString = "Remover Produtor em GN -> NS:" + str(ns) + " ;"
        log(logString + "\n")

    def adicionarConsumidor(self, ns): #função que adiciona um consumidor
        consumidorGerenciadordeNot.append(ns)
        print("ADD C:", ns)
        logString = "ADD Consumidor em GN -> NS:" + str(ns) + " ;"
        log(logString + "\n")

    def removerConsumidor(self, ns): #função que remove um consumidor
        consumidorGerenciadordeNot.append(ns)
        print("REM C:", ns)
        logString = "REM Consumidor em GN -> NS:" + str(ns) + " ;"
        log(logString + "\n")

    def CorrigindoaHora(self):
        logString = "Hora no GN:" + str(datetime.datetime.now().strftime("%H:%M:%S")) + " ;"
        log(logString + "\n")
        return (datetime.datetime.now().strftime("%H:%M:%S"))

    def escolherProdutor(self):
        if len(produtorGerenciadordeNot) == 0:
            return False
        else:
            qualProdConect = random.choice(produtorGerenciadordeNot) #O produtor que o consumidor irá conectar será escolhido aleatoriamente
            if qualProdConect not in produtorGerenciadordeNot:
                produtorGerenciadordeNot.remove(qualProdConect)
            logString = "Produtor escolhido foi: " + qualProdConect
            log(logString + "\n")
            return qualProdConect


def main(): #Principal
    try:
        Pyro4.config.HOST = IP
        daemon = Pyro4.Daemon(IP)
        uri = daemon.register(Servidor) #Identificador de objetos
        print("URI Servidor:", uri)
        ns = Pyro4.locateNS() #Localizando o objeto do produtor
        print("NS: Servidor", ns)
        ns.register("Servidor", uri) #registrando o objeto "Servidor"
        daemon.requestLoop() # O servidor seguirá ativado!

    except ValueError:
        print("Erro!")
        exit(0)
if __name__ == "__main__":
    main()

