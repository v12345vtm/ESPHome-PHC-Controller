import colorama

from colorama import Fore

colorama.init()

ansi_stm_zegt = Fore.RED
ansi_mod_zegt = Fore.BLUE
ansi_mod_terinfo = Fore.MAGENTA #roze
terugzwartzettenansi = Fore.RESET



print(Fore.BLUE +   "This is the color of the sky"  )
print(Fore.GREEN + "This is the color of grass" )
print(Fore.BLUE + "This is a dimmer version of the sky"  )
print(ansi_stm_zegt + "This is the color of the sun" + terugzwartzettenansi )
print("fzefzefzZWART wil ii ")
print(Fore.YELLOW +f"zefzef" + terugzwartzettenansi)



def checkofdecrcjuistis(ext):

    #we mogen geen spaties voor of achter de data hebben
    ext= ext.lstrip().rstrip()

    tabelcrcberekenen = list()
    tabelcrcberekenen = ext.split(' ')
    if len(tabelcrcberekenen) < 5:
        return False  # dat kan nooit een deftig rs485pakket zijn
    else:
        # de laatste 2 elementen wegdoen uit tabel
        tabelcrcberekenen.pop()
        tabelcrcberekenen.pop()

    tempcrc = int(65535)
    for x in tabelcrcberekenen:
        yy = int(x, 16)
        tempcrc = tempcrc ^ yy  # 65281 dan 4470 dan 5761 dan 38295 dan 57507 dan 38771
        # print(f'tempcrc xor {tempcrc}')
        for r in range(0, 8):  # print("nu 8x schuiven met bytes %d" % (r))
            som = tempcrc & int(1)
            if (som == 1):
                tempcrc = tempcrc >> 1
                tempcrc = tempcrc ^ 33800  # 0x8408 polynoom
            else:
                tempcrc = int(tempcrc / 2)
    tempcrc = tempcrc ^ 65535  # laaste grote berekening
    tempcrc = tempcrc + 65536  # postprocessing ,voorloopnul  ervoor , zorg dat je altijd 5 karkters hebt , waarvan de 4 rechtse de crc zijn
    CRCstring = str(tempcrc)
    crcstring = str(hex(tempcrc)).upper()
    crcdeel1 = crcstring[5] + crcstring[6]
    crcdeel2 = crcstring[3] + crcstring[4]
    tabelcrcberekenen.append(crcdeel1)
    tabelcrcberekenen.append(crcdeel2)
    if ext == " ".join(tabelcrcberekenen):
        # print("checkofdecrcjuistis checked ok  ")
        return True
    else:
        print("checkofdecrcjuistis checked niet ok  MAAR bij dimmers antwoord hij verkeerd als je functie 22 2keer na elkaar doet , \n dus bij dimmers moet je eerst fb vragen door vb 0a 01 01 te doen en dan u commando eens doen   A0 02 01 3E F6 wrong crc en moest zijn  : A0 82 00 01 3E F6 ")




        return False


#####################end functie crc berekenen

def respons_analyser(rs485data):
    global starttijd,stoptijd , ansi_stm_zegt , ansi_mod_zegt , ansi_mod_terinfo , terugzwartzettenansi
    print(f"\n rs485pakket:   {rs485data} :")
    responsintextvorm = ""


    try:
        crcisgeldig = checkofdecrcjuistis(rs485data)
    except Exception as e:
        print(e)
        print("checkofdecrcjuistis(rs485data) is foutgegaan mss inputcontrole ??")

    if crcisgeldig == False:
        print("ongeldige crc , we gaan niet ontleden in de respons_analyser")
    else:
        tabel = rs485data.split()
        fromadres = int(tabel[0], 16)
        temp = bin(int(tabel[1], 16))[2:].zfill(8)  # str2binair
        aantalbytesdievolgen = int(temp[4:8], 2)
        str2bin = bin(int(tabel[1], 16))[2:].zfill(8)
        togglebit = str2bin[0]

        # print(f"\t togglebit:{togglebit} ")
        # print(f"\t aantlbytesdievolgen:{aantalbytesdievolgen} ")

        ###########################################
        if 0 <= int(fromadres) <= 31:

            if aantalbytesdievolgen == 1:
                channel = int(tabel[2][0], 16)  # welke knop in de inputmodule
                functie = int(tabel[2][1], 16)  # frunctie2 = aan<1sec ofzo
                uitleg = ""
                if functie == 0:
                    uitleg = " STM zegt ack, gebruik straks maar deze togglebit ==> "
                    if togglebit =="0":
                        gebruikstraksdezetogglebit = "1"
                    else:
                        gebruikstraksdezetogglebit = "0"

                    print(ansi_stm_zegt + f"\t  inputmodule:{fromadres}   {uitleg} ,===>{gebruikstraksdezetogglebit}"    + terugzwartzettenansi)
                    responsintextvorm = (f"\t  inputmodule:{fromadres}   {uitleg} ,===>{gebruikstraksdezetogglebit}"  )
                else:
                    if functie == 1:
                        uitleg = "ze vroegen mijn feedback"
                        print(ansi_stm_zegt + f"\t inputmodule:{fromadres} ..{uitleg} ..togglebit:{togglebit}"  + terugzwartzettenansi)
                        responsintextvorm = (f"\t inputmodule:{fromadres} ..{uitleg} ..togglebit:{togglebit}"  )
                    else:
                        if functie == 0: uitleg = "knop is weer vrij"
                        if functie == 2: uitleg = "in>0s"
                        if functie == 3: uitleg = "uit<1s"
                        if functie == 4: uitleg = "in>1s"
                        if functie == 5: uitleg = "uit>1s"
                        if functie == 6: uitleg = "in>2s"
                        #starttijd = time.time() * 1000
                        print(ansi_mod_zegt + f"\t iemand drukt knop van inputmodule:{fromadres}.{channel} en met functie {functie} ..{uitleg} ..togglebit:{togglebit}"   +terugzwartzettenansi)
                        responsintextvorm = (f"\t iemand drukt knop van inputmodule:{fromadres}.{channel} en met functie {functie} ..{uitleg} ..togglebit:{togglebit}" )


            if aantalbytesdievolgen == 3:
                print(ansi_stm_zegt + f"\t inputmodule:{fromadres}   {tabel[2]}=acknowlede   zet leduitgangenlow op {tabel[3]}   en  zet leduitgangenhigh op {tabel[4]}"   + terugzwartzettenansi)
                responsintextvorm = ( f"\t inputmodule:{fromadres}   {tabel[2]}=acknowlede   zet leduitgangenlow op {tabel[3]}   en  zet leduitgangenhigh op {tabel[4]}" )

            if aantalbytesdievolgen == 4:
                # print(f"\t {tabel[3]}=leduit0-7")
                # print(f"\t {tabel[4]}=knop0-7")
                # print(f"\t {tabel[5]}=knop8-15")
                temph = bin(int(tabel[5], 16))[2:].zfill(8)  # str2binair
                templ = bin(int(tabel[4], 16))[2:].zfill(8)  # str2binair
                ledl = bin(int(tabel[3], 16))[2:].zfill(8)[::-1]  # str2binair achterstevoren
                print(ansi_mod_zegt +
                    f"\t inputmodule:{fromadres} + {templ} {temph}   =inputs0.0-0.15   en {ledl}  =leds0.0-0.7 ook te testen togglebit:{togglebit}"   + terugzwartzettenansi)
                responsintextvorm = ( f"\t inputmodule:{fromadres} + {templ} {temph}   =inputs0.0-0.15   en {ledl}  =leds0.0-0.7 ook te testen togglebit:{togglebit}" )

            if aantalbytesdievolgen == 5:
                # print(f"\t {tabel[3]}=led  ")
                # print(f"\t {tabel[6]}=led ")
                # print(f"\t {tabel[4]}=knop ")
                # print(f"\t {tabel[5]}=knop ")
                temph = bin(int(tabel[5], 16))[2:].zfill(8)[::-1]  # str2binair achterstevoren ::-1
                templ = bin(int(tabel[4], 16))[2:].zfill(8)[::-1]  # str2binair
                ledl = bin(int(tabel[3], 16))[2:].zfill(8)[::-1]  # str2binair
                ledh = bin(int(tabel[6], 16))[2:].zfill(8)[::-1]  # str2binair
                print(ansi_mod_zegt + f"\t inputmodule:{fromadres} + {templ} {temph}   =inputs0.0-0.15  en  {ledl} {ledh}  =leds0.0 -0.15 ok togglebit:{togglebit}"   +terugzwartzettenansi)
                responsintextvorm = (f"\t inputmodule:{fromadres} + {templ} {temph}   =inputs0.0-0.15  en  {ledl} {ledh}  =leds0.0 -0.15 ok togglebit:{togglebit}" )
        ##########################
        if 32 <= int(fromadres) <= 63:
            print(f"\t mmc/ir/busschak mod:{fromadres-32}   .togglebit:{togglebit}")

            if aantalbytesdievolgen == 1:
                print(ansi_mod_zegt + f"\t mmc/ir/busschak mod:{fromadres-32}=iemand drukt op een knop ..togglebit:{togglebit}"  +terugzwartzettenansi)
                responsintextvorm = ( f"\t mmc/ir/busschak mod:{fromadres-32}=iemand drukt op een knop ..togglebit:{togglebit}" )

            if aantalbytesdievolgen == 9:
                # print(f"\t {fromadres}=iemand  vroeg welke fw ik heb")
                print(ansi_mod_zegt  + f"\t mmc/ir/busschak mod:{fromadres-32}ik heb fw-versie {tabel[2]}.{tabel[5]} .togglebit:{togglebit}"  +terugzwartzettenansi)
                responsintextvorm = (f"\t mmc/ir/busschak mod:{fromadres-32}ik heb fw-versie {tabel[2]}.{tabel[5]} .togglebit:{togglebit}" )

            if aantalbytesdievolgen == 10:
                print(f"\t {tabel[2]}=knop0-7")
                print(f"\t {tabel[3]}=led naastknop")
                print(f"\t {tabel[4]}=leduit0-7")
                print(f"\t {tabel[6]}=byte veldverlichting is 0of1")
                print(f"\t {tabel[5]}=todo")
                print(f"\t {tabel[7]}=knop8-15")
                print(f"\t {tabel[8]}=terugmelding?todo_")
                print(f"\t {tabel[9]}=terugmelding?todo a")
                print(f"\t {tabel[10]}=terugmelding?todo b")
                print(f"\t {tabel[11]}=terugmelding?todo c")
                templ = bin(int(tabel[4], 16))[2:].zfill(8)  # str2binair
                ledl = bin(int(tabel[3], 16))[2:].zfill(8)  # str2binair
                veldverlichting = bin(int(tabel[6], 16))[2:].zfill(8)  # str2binair
                print(ansi_mod_zegt +
                    f"\t mmc/ir/busschak mod:{fromadres-32}  +{templ}   =inputs0.7-0.0   // {ledl}  =leds0.7 -0.0  // {veldverlichting} centraallichtvlak .togglebit:{togglebit}"  +terugzwartzettenansi)
                responsintextvorm = ( f"\t mmc/ir/busschak mod:{fromadres-32}  +{templ}   =inputs0.7-0.0   // {ledl}  =leds0.7 -0.0  // {veldverlichting} centraallichtvlak .togglebit:{togglebit}" )

        ###################################
        if 64 <= int(fromadres) <= 95:
            # print(f" \t {fromadres-64}=uitg mod")

            if aantalbytesdievolgen == 1:
                # print(f"\t we vragen me mijn feedback of geven me een taakje")
                str2bin = bin(int(tabel[2], 16))[2:].zfill(8)
                tempkanaal = str2bin[0:3]  # 3linkse bits
                channel = int(tempkanaal, 2)  # 3linkse bits in binaire vorm naar decimaal vb 111 = 7
                tempfunctie = str2bin[3: 8]  # de 5 rechtse bits  functie2 = inschakekelen ofzo
                functie = int(tempfunctie, 2)  #
                uitleg = ""
                if functie == 1:
                    uitleg = "ze vroegen mijn feedback"
                    print(        ansi_stm_zegt + f"\t  uitgmod:{fromadres - 64}.{channel}   en met functie{functie} met opdracht {uitleg} .togglebit:{togglebit}" + terugzwartzettenansi)
                    responsintextvorm = (f"\t  uitgmod:{fromadres - 64}.{channel}   en met functie{functie} met opdracht {uitleg} .togglebit:{togglebit}")
                else:
                    if functie == 0: uitleg = "beste STM , de opdracht heb ik mooi uitvoerd"
                    if functie == 1: uitleg = "ze vragen mijn feedback"
                    if functie == 2: uitleg = "inschakelen"
                    if functie == 3: uitleg = "uitschakelen"
                    if functie == 4: uitleg = "inschakelen vergrendelde"
                    if functie == 5: uitleg = "uitschakelen vergrendelde"
                    if functie == 6: uitleg = "omschakelen"
                    if functie == 7: uitleg = "ontgrendelen"
                    if functie == 18: uitleg = "tijd onderbreken"
                    if functie == 14: uitleg = "vast vergrendelen"
                    if functie == 15: uitleg = "vergrendelen voor de lopende tijd"
                    if functie == 22: uitleg = "jrm tijdsfunctie onderbroken"
                    print(ansi_stm_zegt + f"\t  uitgmod:{fromadres - 64}.{channel}   en met functie{functie} met opdracht {uitleg} .togglebit:{togglebit}"  +terugzwartzettenansi)
                    responsintextvorm = ( f"\t  uitgmod:{fromadres - 64}.{channel}   en met functie{functie} met opdracht {uitleg} .togglebit:{togglebit}")

            if aantalbytesdievolgen == 2:
                # print(f"\t oude fw ik zeg mijn standen")
                standerelais = bin(int(tabel[3], 16))[2:].zfill(8)[::-1]
                # print(f"\t {str2bin}={tabel[3]} =relais0.7 -0.0")
                str2bin = bin(int(tabel[2], 16))[2:].zfill(8)
                tempkanaal = str2bin[0:3]  # 3linkse bits
                channel = int(tempkanaal, 2)  # 3linkse bits in binaire vorm naar decimaal vb 111 = 7
                tempfunctie = str2bin[3: 8]  # de 5 rechtse bits  functie2 = inschakekelen ofzo
                functie = int(tempfunctie, 2)  #extracted uit tabel[2]
                uitleg = ""
                if functie == 2: uitleg = "jrm loopstoppen ok"
                if functie == 9: uitleg = "jrm pririteitenlagen vergrendelen"
                if functie == 10: uitleg = "jrm pririteitenlagen ontgrendelen"
                if functie == 13: uitleg = "jrm pririteitenlagen instellen"
                if functie == 14: uitleg = "jrm pririteitenlagen wissen"
                if functie == 3: uitleg = "jrm loop stoppen"
                if functie == 1:
                    uitleg = "ik zeg mijn relaisstand"
                    channel = "nietvtoepassing"
                if functie == 0: uitleg = "ik(jrmmodule) kreeg opdracht van tijdsding \nen ik geef responsdaarop "
                if functie == 178: uitleg = "fghn"
                if functie == 145: uitleg = "fglen"
                if functie == 1785: uitleg = "fijd"
                #42is channel2 loop
                #62 is channel3 loopstoppen
                print(ansi_mod_zegt + f"\t ****uitgmod:{fromadres - 64} en met stand {standerelais}  00.00 - 00.07  functie{functie}  channel{channel}  {uitleg}.togglebit:{togglebit}"  +terugzwartzettenansi)
                responsintextvorm = ( f"\t ****uitgmod:{fromadres - 64} en met stand {standerelais}  00.00 - 00.07  functie{functie}  channel{channel}  {uitleg}.togglebit:{togglebit}" )

            if aantalbytesdievolgen == 4:
                # print(f"\t  nieuwe fw ik zeg mijn standen")
                standerelais = bin(int(tabel[1], 16))[2:].zfill(8)
                str2bin = bin(int(tabel[2], 16))[2:].zfill(8)
                tempkanaal = str2bin[0:3]  # 3linkse bits
                channel = int(tempkanaal, 2)  # 3linkse bits in binaire vorm naar decimaal vb 111 = 7
                tempfunctie = str2bin[3: 8]  # de 5 rechtse bits  functie2 = inschakekelen ofzo
                functie = int(tempfunctie, 2)  #
                uitleg = ""
                if functie == 7: uitleg = "jrm tipbedrijf omhoog"
                if functie == 8: uitleg = "jrm tipbedrijf omlaag"
                if functie == 6: uitleg = "jrm inschakelen omlaag"
                if functie == 5: uitleg = "jrm inschakelen omhoog"
                if functie == 3: uitleg = "jrm omschak omhoog uit"
                if functie == 4: uitleg = "jrm omschak omlaag uit"
                print(f"\t {tabel[0]}=relaisstand todo")
                print(f"\t {tabel[0]}=terugmeldingenstand todo")
                print(f"\t {tabel[0]}=bedrijfsuren todo")
                print(ansi_mod_zegt + f"\t uitgmod:{fromadres - 64} en met stand {standerelais}  00.00 - 00.07  *functie{functie}  channel{channel}  en met opdracht {uitleg} .togglebit:{togglebit}"  +terugzwartzettenansi)
                responsintextvorm = ( f"\t uitgmod:{fromadres - 64} en met stand {standerelais}  00.00 - 00.07  *functie{functie}  channel{channel}  en met opdracht {uitleg} .togglebit:{togglebit}" )

            if aantalbytesdievolgen == 3:
                print(f"\t  rolluikmod/uitgmod")
                str2bin = bin(int(tabel[2], 16))[2:].zfill(8)
                # erezr =int(tabel[2][0], 16)  # welke relais presies?
                tempkanaal = str2bin[0:3]  # 3linkse bits
                channel = int(tempkanaal, 2)  # 3linkse bits in binaire vorm naar decimaal vb 111 = 7
                tempfunctie = str2bin[3: 8]  # de 5 rechtse bits  functie2 = inschakekelen ofzo
                functie = int(tempfunctie, 2)  #
                databyteongekendwathetis = tabel[3]
                databyteongekendwathetis2 = tabel[4]
                uitleg = ""
                if functie == 19: uitleg = "jrm tijdsmeting vertraagd aan"
                if functie == 20: uitleg = "jrm tijdsmeting vertraagd uit"
                if functie == 21: uitleg = "jrm tijdsmeting aan met tijd"
                if functie == 1:
                    uitleg = "ze vroegen mijn fb\njrm 3gelijkedataopdrachten voor : \nTERUGMELDING-tijdsmetingstatusflagaan &tijdsmetingstatusflaguit & tijdsmetingonderbreken \n(ist weer 00 15 ?)" + databyteongekendwathetis + "enof"+databyteongekendwathetis2
                    print(ansi_mod_zegt + f"\t ???uitgmod/rolluikmod:{fromadres - 64}.{channel}  \nen met functie:{functie} en met opdracht {uitleg} togglebit:{togglebit}"  +terugzwartzettenansi)
                    responsintextvorm = ( f"\t ???uitgmod/rolluikmod:{fromadres - 64}.{channel}  \nen met functie:{functie} en met opdracht {uitleg} togglebit:{togglebit}" )
                else:

                    if functie == 40: uitleg = "inschakelvertraging ok"
                    if functie == 41: uitleg = "uitschakelvertraging ok"
                    if functie == 42: uitleg = "inschakelen met timer" + "tijd : " + tabel[4] + " " + tabel[3] + "sec"
                    if functie == 43: uitleg = "uitschakelen met timer  " + "tijd : " + tabel[4] + " " + tabel[3] + "sec"
                    if functie == 44: uitleg = "vertraagd omschakelen tijdsvergrendeld ok"
                    if functie == 45: uitleg = "omschakelen met timer tijdsvergrendeld ok"
                    if functie == 48: uitleg = "tijdaanvullingop actuele tijd ok"
                    if functie == 49: uitleg = "set de tijd opnieuw ok"
                    # print(f"\t {tabel[4]}=tijdbyte1")
                    # print(f"\t {tabel[3]}=tijdbyte0")
                    print(ansi_stm_zegt + f"\t ???uitgmod/rolluikmod:{fromadres - 64}.{channel}  \nen met functie:{functie} en met opdracht {uitleg} togglebit:{togglebit}"  +terugzwartzettenansi)
                    responsintextvorm = (f"\t ???uitgmod/rolluikmod:{fromadres - 64}.{channel}  \nen met functie:{functie} en met opdracht {uitleg} togglebit:{togglebit}" )


            if aantalbytesdievolgen == 5:
                # print(f"\t {fromadres}=iemand  vroeg welke fw ik heb")
                # print(f"\t versie {tabel[8]}.{tabel[9]} togglebit:{togglebit}")
                print(ansi_mod_zegt +
                    f"\t uitgmod:{fromadres - 64}  is weer iets zoals ? 44 85 44 00 00 00 00 17 D9"  +terugzwartzettenansi)
                responsintextvorm =  f"\t uitgmod:{fromadres - 64}  is weer iets zoals ? 44 85 44 00 00 00 00 17 D9"



            if aantalbytesdievolgen == 6:
                # print(f"\t oude fw ik zeg mijn standen")
                standerelais = bin(int(tabel[3], 16))[2:].zfill(8)[::-1]
                # print(f"\t {str2bin}={tabel[3]} =relais0.7 -0.0")
                str2bin = bin(int(tabel[2], 16))[2:].zfill(8)
                tempkanaal = str2bin[0:3]  # 3linkse bits
                channel = int(tempkanaal, 2)  # 3linkse bits in binaire vorm naar decimaal vb 111 = 7
                tempfunctie = str2bin[3: 8]  # de 5 rechtse bits  functie2 = inschakekelen ofzo
                functie = int(tempfunctie, 2)  #
                uitleg = ""
                #if functie == 992: uitleg = "jrm sensoriek "  #43 06 6F 01 00 00 1E 00 62 8A
                if functie == 15: uitleg = "jrm sensoriek rolluik omhoog"
                if functie == 17: uitleg = "jrm sensoriek rolluik laag"
                print(ansi_mod_zegt + f"\t uitgmod/rolluikmod:{fromadres - 64}.{channel} en met functie{functie} sensoriekopdracht {uitleg} togglebit:{togglebit}"  +terugzwartzettenansi)
                responsintextvorm = (f"\t uitgmod/rolluikmod:{fromadres - 64}.{channel} en met functie{functie} sensoriekopdracht {uitleg} togglebit:{togglebit}")

            if aantalbytesdievolgen == 8:
                #fb van een uitgmod nieuwe fw : 44 08 01 00 80 00 00 01 01 20 4E 1B
                #  jrm sensoriek jaloeiz omlaag 43 88 52 01 00 00 1E 00 01 00 7F 23
                # jrm omhoog jaloezie           43 88 70 01 00 00 1E 00 01 00 E0 9E
                print(f"\t nieuwe fw of rolluikmod die jaloezie doet")
                # str2bin = bin(int(tabel[1], 16))[2:].zfill(8)
                # print(f"\t {tabel[4]}=relaisstand")
                relaisl = bin(int(tabel[4], 16))[2:].zfill(8)[::-1]  # str2binair
                # print(f"\t {relaisl} =relais0.0 -0.7")
                print(f"\t {tabel[8]}=terugmeldingenstand todo")
                print(f"\t {tabel[9]}=bedrijfsuren todo")
                str2bin = bin(int(tabel[2], 16))[2:].zfill(8)
                tempkanaal = str2bin[0:3]  # 3linkse bits
                channel = int(tempkanaal, 2)  # 3linkse bits in binaire vorm naar decimaal vb 111 = 7
                tempfunctie = str2bin[3: 8]  # de 5 rechtse bits  functie2 = inschakekelen ofzo
                functie = int(tempfunctie, 2)  #
                uitleg = ""
                #if functie == 992: uitleg = "jrm sensoriek "  #43 06 6F 01 00 00 1E 00 62 8A
                if functie == 16: uitleg = "jrm sensoriek jaloezie omhoog"
                if functie == 18: uitleg = "jrm sensoriek jaloezie laag"
                #print(f"\t uitgmod:{fromadres - 64} status met  {relaisl} =relais0.0 -0.7 togglebit:{togglebit}")
                print(ansi_mod_zegt + f"\t uitgmod nieuwe fw/rolluikmod:{fromadres - 64}.{channel} en met functie{functie} sensoriekopdracht {uitleg}  //   {relaisl}=relais0.0 -0.7togglebit:{togglebit}"  +terugzwartzettenansi)
                responsintextvorm = ( f"\t uitgmod nieuwe fw/rolluikmod:{fromadres - 64}.{channel} en met functie{functie} sensoriekopdracht {uitleg}  //   {relaisl}=relais0.0 -0.7togglebit:{togglebit}")

            if aantalbytesdievolgen == 9:
                # print(f"\t {fromadres}=iemand  vroeg welke fw ik heb")
                # print(f"\t versie {tabel[8]}.{tabel[9]} togglebit:{togglebit}")
                print(ansi_mod_zegt +
                    f"\t uitgmod:{fromadres - 64}  is met fw versie:{tabel[8]}.{tabel[9]} togglebit:{togglebit}"  +terugzwartzettenansi)
                responsintextvorm = ( f"\t uitgmod:{fromadres - 64}  is met fw versie:{tabel[8]}.{tabel[9]} togglebit:{togglebit}" )

        ##################################
        if 96 <= int(fromadres) <= 127:
            print(f"\t anal mod:{fromadres}    togglebit:{togglebit}")
            responsintextvorm = (f"\t anal mod:{fromadres}    togglebit:{togglebit}")

        ###########################
        if 128 <= int(fromadres) <= 159:
            print(f"\t =multimod:{fromadres}    togglebit    :{togglebit}")
            responsintextvorm = (f"\t =multimod:{fromadres}    togglebit    :{togglebit}")

        ######################################
        if 160 <= int(fromadres) <= 191:
            # print(f"\t {fromadres}=dimmermod")

            if aantalbytesdievolgen == 1:
                str2bin = bin(int(tabel[2], 16))[2:].zfill(8)
                tempkanaal = str2bin[0:3]  # 3linkse bits
                channel = int(tempkanaal, 2)  # 3linkse bits in binaire vorm naar decimaal vb 111 = 7
                tempfunctie = str2bin[3: 8]  # de 5 rechtse bits  functie2 = inschakekelen ofzo
                functie = int(tempfunctie, 2)  #
                uitleg = ""
                if functie == 1:
                    uitleg = "ze vroegen mijn feedback"
                    print(ansi_stm_zegt +
                        f"\t  dimmer:{fromadres - 160}.{channel}  taak en met functie {uitleg} togglebit:{togglebit}" + terugzwartzettenansi)
                    responsintextvorm = ( f"dimmer:{fromadres - 160}.{channel}  taak en met functie {uitleg} togglebit:{togglebit}")

                else:
                    if functie == 2: uitleg = "inschakelen op max helderheid met geheugen"
                    if functie == 3: uitleg = "inschakelen op max helderheid zonder geheugen"








                    if functie == 4: uitleg = "uitschakelen"
                    if functie == 5: uitleg = "omschakelen op max helderheid AAN/UIT"
                    if functie == 6: uitleg = "omschakelen op max helderheid AAN/UIT zonder geheugen"
                    if functie == 10: uitleg = "opslaan in Memory"
                    if functie == 14: uitleg = "omschakelen Memory AAN/UIT"
                    if functie == 12: uitleg = "inschakelen verlichtingsniveau Memory"
                    if functie == 13: uitleg = "opslaan Memory1"
                    if functie == 14: uitleg = "omschakelen Memory1 AAN/UIT"
                    if functie == 15: uitleg = "inschakelen Memory1"
                    if functie == 16: uitleg = "opslaan Memory2"
                    if functie == 17: uitleg = "omschakelen Memory2 AAN/UIT"
                    if functie == 18: uitleg = "inschakelen Memory2"
                    if functie == 19: uitleg = "opslaan Memory3"
                    if functie == 20: uitleg = "omschakelen Memory3 AAN/UIT"
                    if functie == 21: uitleg = "inschakelen Memory3"
                    if functie == 0: uitleg = "opdracht niet uigevoerd wegens ongeldige togglebit"


                    print(ansi_mod_zegt + f"\t  dimmer:{fromadres - 160}.{channel}  taak en met functie{functie} {uitleg} togglebit:{togglebit}"  +terugzwartzettenansi)
                    responsintextvorm = ( f"\t  dimmer:{fromadres - 160}.{channel}  taak en met functie{functie} {uitleg} togglebit:{togglebit}" )

            if aantalbytesdievolgen == 2:
                str2bin = bin(int(tabel[2], 16))[2:].zfill(8)
                tempkanaal = str2bin[0:3]  # 3linkse bits
                channel = int(tempkanaal, 2)  # 3linkse bits in binaire vorm naar decimaal vb 111 = 7
                tempfunctie = str2bin[3: 8]  # de 5 rechtse bits  functie2 = inschakekelen ofzo
                functie = int(tempfunctie, 2)  #
                uitleg = ""
                print(ansi_stm_zegt + f"dimmer:{fromadres - 160}.{channel} ack van dimmer.. dimmer gehoorzaamde todo {uitleg} togglebit:{togglebit}"  +terugzwartzettenansi)
                #print(f"\t {tabel[2]}=dim   {tabel[3]}=dim  geen idee to do")
                responsintextvorm = ( f"dimmer:{fromadres - 160}.{channel} ack van dimmer..  dimmer gehoorzaamde todo {uitleg} togglebit:{togglebit}" )

            if aantalbytesdievolgen == 3:
                str2bin = bin(int(tabel[2], 16))[2:].zfill(8)
                tempkanaal = str2bin[0:3]  # 3linkse bits
                channel = int(tempkanaal, 2)  # 3linkse bits in binaire vorm naar decimaal vb 111 = 7
                tempfunctie = str2bin[3: 8]  # de 5 rechtse bits  functie2 = inschakekelen ofzo
                functie = int(tempfunctie, 2)  #
                stm_hextellerwaardegemaptvanpeha = tabel[3]
                dec = int(tabel[3], 16)
                tussen1en160 = int(  (int(tabel[3], 16) - 1) * (160 - 1) / (250 - 1) + 1)  # arduino map functie ;van pehapehapakket naar 0-160 waarde
                uitleg = ""
                if functie == 1:
                    uitleg = "ze vroegen mijn feedback"
                    print(ansi_stm_zegt +
                          f"\t  dimmer:{fromadres - 160}.{channel}  taak en met functie {uitleg} togglebit:{togglebit}" + terugzwartzettenansi)
                    responsintextvorm = (  f"dimmer:{fromadres - 160}.{channel}  taak en met functie {uitleg} togglebit:{togglebit}")

                else:
                    if functie == 8: uitleg = "dim op" + "(tijdparameter=" + str(int(  (int(tabel[3], 16) - 1) * (160 - 1) / (250 - 1) + 1))+ ")"
                    if functie == 9: uitleg = "dim neer" + "(tijdparameter=" + str(int(  (int(tabel[3], 16) - 1) * (160 - 1) / (250 - 1) + 1))+ ")"
                    if functie == 22: uitleg = "dimwaarde en tijd zetten (dimwaarde=" +  str(int(tabel[3], 16)) + " acceleratietijd="   + str(int(  (int(tabel[4], 16) - 1) * (160 - 1) / (250 - 1) + 1)) + ")"
                    if functie == 7: uitleg = "dimmen in tegenovergestelde richting (met tijdwaarde= "+ str(int(  (int(tabel[3], 16) - 1) * (160 - 1) / (250 - 1) + 1))+ ")"
                    print(
                        ansi_mod_zegt + f"\t  verified dimmer:{fromadres - 160}.{channel}  taak en met functie{functie} {uitleg} togglebit:{togglebit}" + terugzwartzettenansi)
                    responsintextvorm = ( f" verified dimmer:{fromadres - 160}.{channel}  taak en met functie{functie} {uitleg} togglebit:{togglebit}")

            if aantalbytesdievolgen == 5:
                str2bin = bin(int(tabel[1], 16))[2:].zfill(8)
                # print(f"\t  ik zeg mijn standen")
                # print(f"\t  nieuwe fw")
                # print(f"\t {tabel[3]}=dim0stand ")
                # print(f"\t {tabel[4]}=dim1stand ")
                # print(f"\t {tabel[5]}=dim0terugmeld")
                # print(f"\t {tabel[6]}=dim1terugmeld")
                dim0decimaal = int(tabel[3], 16)  # int("0xff", 16)
                dim1decimaal = int(tabel[4], 16)  #
                print(ansi_mod_zegt + f"\t dimmer:{fromadres - 160}.0={dim0decimaal}  en  dimmer:{fromadres - 160}.1={dim1decimaal} en {tabel[5]}=dim0terugmeld + {tabel[6]}=dim1terugmeld  togglebit:{togglebit}"  +terugzwartzettenansi)
                responsintextvorm = ( f" dimmer:{fromadres - 160}.0={dim0decimaal}  en  dimmer:{fromadres - 160}.1={dim1decimaal} en {tabel[5]}=dim0terugmeld + {tabel[6]}=dim1terugmeld  togglebit:{togglebit}")

        ###########################
        if 192 <= int(fromadres) <= 223:
            print(f"\t mod:{fromadres}=ongekend togglebit:{togglebit}"  +terugzwartzettenansi)
            responsintextvorm = (f"\t mod:{fromadres}=ongekend togglebit:{togglebit}")

        #######################
        if 224 <= int(fromadres) <= 255:
            print(f"\t mod:{fromadres}=systeembox togglebit:{togglebit}"  +terugzwartzettenansi)
            responsintextvorm = (f"mod:{fromadres}=systeembox togglebit:{togglebit}")
            pass

    ###########################################
    return responsintextvorm

#print(checkofdecrcjuistis("46 01 A2 A3 89"))
print(respons_analyser("46 02 00 20 49 35"))


