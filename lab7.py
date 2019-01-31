from tkinter import *
from tkinter import ttk
import time
import random
try: #provo a importare il modulo 'serial'
    import serial
    import serial.tools.list_ports
except: #se non installato viene chiesto all'utente se desidera installarlo
    consenso=input("Impossibile importare il modulo 'serial'. Si desidera installarlo [s/n]? ").upper()
    while (consenso!="S" and consenso!="N"):
        consenso=input("Input non valido. Si desidera installarlo [S/N]? ").upper()
    if consenso=="S":
        import os
        import subprocess
        if sys.platform.startswith('win'): #installazione per piattaforma windows
                process=subprocess.call(("pip install pyserial"))
        elif sys.platform.startswith('linux'): #installazione per piattaforma linux
            try:
                process=subprocess.call(("sudo -H -S python3 -m pip install pyserial").split(" "))
                import serial                   
                import serial.tools.list_ports
            except:
                try:
                    process=subprocess.call(("sudo -H -S apt-get install python3-pip").split(" "))
                    process=subprocess.call(("sudo -H -S python3 -m pip install pyserial").split(" "))
                    import serial                   
                    import serial.tools.list_ports
                except:
                    print("Impossibile importare il modulo 'serial'. Installarlo manualmente.")
                    exit()
    elif consenso=="N":
        print("Impossibile proseguire con l'esecuzione.")
        exit()

def calc_avg(new_value): #calcola la media dei tempi di reazione della sessione
    global prove_effettuate, media
    sum=media*prove_effettuate+new_value
    prove_effettuate=prove_effettuate+1
    media=sum/prove_effettuate
    return media

def check_best(new_value): #verifica se e' stato battuto il record della sessione
    global best_time
    if new_value<best_time: best_time=new_value
    return best_time

def send_command(command): #se e' consentito, invia il comando sulla seriale
    global wait_start_flag, last_command, modalita, ser
    #controllo che non sia gia' in corso l'invio di un comando e che il comando da inviare sia diverso dall'ultimo inviato
    if wait_start_flag==False and ser.isOpen() and last_command!=int(command[2]):
        last_command=int(command[2])
        wait_start_flag=True #impedisco che venga inviato un altro comando
        if modalita=="G": #se in modalita' grafica disabilito i pulsanti
            on_button['state']='disabled'
            off_button['state']='disabled'
        time.sleep(random.randint(10,20)) #aspetto un tempo casuale tra 10s e 20s
        ser.write(command.encode()) #invio il comando
        read_time() #avvio la lettura da seriale

def read_time():
    global wait_start_flag, modalita
    try: #aspetta da seriale 5 caratteri, se non arrivano entro i 70s impostati da timeout, va in except
        elapsed_time=ser.read(5).decode('ascii')    
        if elapsed_time[0]=="T": #controlla che il primo carattere sia una T
            elapsed_time=float(int(elapsed_time[1:5],16)/1000) #converte la stringa HEX (ms) in DEC (s)
            avg=calc_avg(elapsed_time) #aggiorno la media
            best=check_best(elapsed_time) #verifico il record
            #stampa dei risultati
            if modalita=="G":
                time_gui.set("{:6.3f}".format(elapsed_time))
                avg_time_gui.set("{:6.3f}".format(avg))
                best_time_gui.set("{:6.3f}".format(best))
            elif modalita=="T":
                print("Tempo di reazione (s):",elapsed_time)
                print("Tempo di reazione medio (s): %5.3f" % (avg))
                print("Tempo di reazione migliore (s): %5.3f \n" % (best))
        else:
            msg="Errore nella stringa ricevuta."
            if modalita=="G": status_log.set(msg) 
            elif modalita=="T": print(msg) 
    except:
        msg="Comando non valido. Timeout lettura."
        if modalita=="G": status_log.set(msg) 
        elif modalita=="T": print(msg) 
    wait_start_flag=False #puo' avvenire un nuovo invio
    #riabilita il pulsante non premuto in precedenza
    if last_command==0 and modalita=="G": on_button['state']='normal'
    elif last_command==1 and modalita=="G": off_button['state']='normal'

def inizializza_seriale(port): #apre la comunicazione seriale
    global ser
    if modalita=="G":
        port=port_select.get()
    #configurazione della porta seriale
    ser.port=port
    ser.baudrate=115200
    ser.parity=serial.PARITY_NONE
    ser.stopbits=serial.STOPBITS_ONE
    ser.bytesize=serial.EIGHTBITS
    ser.timeout=70
    if not ser.isOpen():
        try: #se non e' gia' aperta la porta tenta di aprirla
            ser.open()
        except serial.SerialException: #se non riesce ad aprirla stampa un errore e arresta l'esecuzione
            msg="Impossibile connetersi a "+port+".Provare a ricollegare la scheda."
            if modalita=="G": status_log.set(msg) 
            elif modalita=="T": print(msg)
            exit()

#*********************************************************************************************************************************

prove_effettuate=0
media=0
best_time=70
ser = serial.Serial() #istanzio un oggeto della classe 'serial'
wait_start_flag=False #impedisce di inviare un comando mentre sto ancora attendendo l'invio di un altro
last_command=-1 #all'avvio, l'ultimo comando e' incognito, inizializzo quindi ad un valore stabilito, diverso da 0 e da 1
modalita=input("eseguire con interfaccia grafica o testuale? [G/T]: ").upper() #scelta dell'interfaccia
while (modalita!= "T" and modalita!="G"):
    modalita=input("Comando non valido. Eseguire con interfaccia grafica o testuale? [G/T]: ").upper()
i=0
comlist=[]
comport=serial.tools.list_ports.comports()
if len(comport)>0:
    for el in comport: #elenco tutte le porte COM disponibili
        comlist.append(el.device)
        if modalita=="T":
            print("[%d]:" % (i),el.device)
            i=i+1
else:
    print("Non ci sono porte seriali disponibili. Connettere la NUCLEO e riavviare il programma.")
    exit()

if modalita=="T":
    port_select=input("Selezionare una delle porte elencate [N]: ") #selezione della porta seriale
    while (not port_select.isdigit() or int(port_select)<0 or int(port_select)>=i):
        port_select=input("Porta non disponibile. Selezionare una delle porte elencate [N]: ")
    inizializza_seriale(comlist[int(port_select)]) #apre la porta seriale
    while 1:
        comando=input("scrivere comando da inviare [L 0/L 1]\no scrivere q per uscire\n") #chiede comando all'utente
        if comando=="q":
            ser.close()
            exit()
        elif (comando=="L 0" or comando=="L 1"): send_command(comando)
        else: print("Comando non valido")
            
elif modalita=="G":
    def clear_log(*args): #funzione per pulire il messaggio di log sulla GUI
        status_log.set("") 
    #GUI    
    root=Tk() 
    root.title("Misuratore di riflessi")
    mainframe=ttk.Frame(root,padding="12 12 12 12")
    mainframe.grid(column=0, row=0, sticky=(N,W,E,S))
    # Pulsante L0
    off_button=ttk.Button(mainframe, text="L 0", command=lambda: send_command("L 0"))
    off_button.grid(column=0, row=0, sticky=(W, E))
    off_button.bind("<Button-1>", clear_log)
    # Pulsante L1
    on_button=ttk.Button(mainframe, text="L 1", command=lambda: send_command("L 1"))
    on_button.grid(column=1, row=0, sticky=(W, E))
    on_button.bind("<Button-1>", clear_log)
    # Indicatore tempo di reazione
    time_gui=StringVar()
    reaction_time=ttk.Label(mainframe,width=30, textvariable=time_gui)
    reaction_time.grid(column=1, row=1, sticky=(W, E))
    # Etichetta tempo di reazione
    time_label=ttk.Label(mainframe,text="Tempo di reazione (s):", width=30, anchor="e")
    time_label.grid(column=0,row=1, sticky=(W, E))
    # Indicatore tempo di reazione medio
    avg_time_gui=StringVar()
    reaction_time=ttk.Label(mainframe,width=30, textvariable=avg_time_gui)
    reaction_time.grid(column=1, row=2, sticky=(W, E))
    # Etichetta tempo di reazione medio
    time_label=ttk.Label(mainframe,text="Tempo di reazione medio (s):", width=30, anchor="e")
    time_label.grid(column=0,row=2, sticky=(W, E))
    # Indicatore tempo di reazione migliore
    best_time_gui=StringVar()
    reaction_time=ttk.Label(mainframe,width=30, textvariable=best_time_gui)
    reaction_time.grid(column=1, row=3, sticky=(W, E))
    # Etichetta tempo di reazione migliore
    time_label=ttk.Label(mainframe,text="Tempo di reazione migliore (s):", width=30, anchor="e")
    time_label.grid(column=0,row=3, sticky=(W, E))
    #selettore porta
    port_select=StringVar()
    port_box=ttk.Combobox(mainframe, textvariable=port_select)
    port_box.grid(row=4, sticky=(W, E), column=1)
    port_box['values']=tuple(comlist)
    port_box.bind("<<ComboboxSelected>>", inizializza_seriale) #apre la porta seriale selezionata
    #etichetta porta
    port_label=ttk.Label(mainframe, text="Porta selezionata:", anchor="e", width=30)
    port_label.grid(row=4, sticky=(W, E), column=0)
    # log stato
    status_log=StringVar()
    status=ttk.Label(mainframe, textvariable=status_log, anchor="center", width=25)
    status.grid(row=5, sticky=(W, E), column=0, columnspan=2)
    #faccio in modo che la GUI si adatti dinamicamente con la dimensione della finestra
    root.columnconfigure(0,weight=4)
    root.rowconfigure(0, weight=4)
    for j in range(2): mainframe.columnconfigure(j,weight=1)
    for j in range(6): mainframe.rowconfigure(j, weight=1)
    for child in mainframe.winfo_children(): child.grid_configure(padx=3, pady=3)
    root.mainloop()