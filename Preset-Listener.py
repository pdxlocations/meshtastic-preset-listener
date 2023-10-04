import time
import meshtastic
import meshtastic.serial_interface
from pubsub import pub

# CONFIGURATION
rebootSeconds = 3    # time to wait for reboots
listenSeconds = 5    # time to listen on each preset
scanCycles = 2        # number of cycles through the presets
testing = True        # if true, don't send lora settings to radio (no reboots)
showPackets = True

ignoreFrom = '\'from\': 1439168412' # packets from our node don't count

# PRESET NAME : CHANNEL, FREQUENCY
preset_dict = {'LONG_FAST'      :   ['20','906.875'],
               'LONG_SLOW'      :   ['27','905.3125'],
               'VERY_LONG_SLOW' :   ['49','905.03125'],
               'MEDIUM_SLOW'    :   ['52','914.875'],
               'MEDIUM_FAST'    :   ['45','913.125'],
               'SHORT_SLOW'     :   ['75','920.625'],
               'SHORT_FAST'     :   ['68','918.875'],
               'LONG_MODERATE'  :   ['6','902.6875']}

keys_list = list(preset_dict.keys())

receivedPackets = []

interface = meshtastic.serial_interface.SerialInterface()
ourNode = interface.getNode('^local')

def onReceive(packet, interface):
    if ignoreFrom not in str(packet):
        print ('\n>>>>>>>>>>>>>>>>>>> PACKET RECEIVED <<<<<<<<<<<<<<<<<<<<<<<\n')
        if showPackets: print(packet)
        print('')
        receivedPackets.append(keys_list[ourNode.localConfig.lora.modem_preset])


print (f'\n\nStarting ....  This scan will take {round(((listenSeconds + rebootSeconds) * scanCycles * len(keys_list))/60,2)} minutes\n')


for cycle in range(scanCycles):

    for preset in preset_dict:
        ourNode = interface.getNode('^local')
        print(f'Changing to preset: {preset}')
        ourNode.localConfig.lora.modem_preset = preset

        if not testing:
            ourNode.writeConfig("lora")
            # print ('Command sent..... waiting '+ str(commandDelay) + ' seconds')
            # time.sleep(commandDelay)

        print (f'Disconnected and waiting {str(rebootSeconds)} seconds to reboot')
        interface.close()
        time.sleep(rebootSeconds)

        interface = meshtastic.serial_interface.SerialInterface()

        print(f'Listening >>> {preset} CH{preset_dict[preset][0]} {preset_dict[preset][1]}MHz for {listenSeconds} seconds\n')

        pub.subscribe(onReceive, 'meshtastic.receive')
        time.sleep(listenSeconds) 





print ('')
print ('-------------------------------------------------------------')
print ('Packets received on presets:\n')
for result in receivedPackets:
    print (result)

print ('')

interface.close()