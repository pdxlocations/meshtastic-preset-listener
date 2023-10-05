import time
import meshtastic
import meshtastic.serial_interface
from pubsub import pub

# CONFIGURATION
ignoreFrom = '\'from\': 1342589710' # !!! SET YOUR NODE NUMBER HERE - packets from our node don't count
rebootSeconds = 10     # time to wait for reboots
listenSeconds = 900    # time to listen on each preset
scanCycles = 1         # number of cycles through the presets
showPackets = True     # if true, display the received packets as they arrive
skipLongFast = True    # if true, skip the LongFast preset
testing = False        # if true, don't send lora settings to radio (no reboots)


# PRESET NAME : CHANNEL, FREQUENCY (CH and FREQ are currently only for informational purposes)
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
        if showPackets:
            print(packet)
        print('')
        receivedPackets.append(keys_list[ourNode.localConfig.lora.modem_preset])

if skipLongFast:
    presetsToScan = len(keys_list)-1
else:
    presetsToScan = len(keys_list)
totalTime = round(((listenSeconds + rebootSeconds) * scanCycles * presetsToScan)/60,2)

print (f'\n\nStarting ....  This scan will take {totalTime} minutes\n')

for _ in range(scanCycles):
    for preset in preset_dict:
        if skipLongFast and preset == "LONG_FAST":
            continue
        ourNode = interface.getNode('^local')
        print(f'Changing to preset: {preset}')
        ourNode.localConfig.lora.modem_preset = preset

        if not testing:
            ourNode.writeConfig("lora")

        print (f'Disconnected and waiting {str(rebootSeconds)} seconds to reboot')
        interface.close()
        time.sleep(rebootSeconds)

        interface = meshtastic.serial_interface.SerialInterface()

        print(f'Listening >>> {preset} CH{preset_dict[preset][0]} {preset_dict[preset][1]}MHz for {listenSeconds} seconds\n')

        pub.subscribe(onReceive, 'meshtastic.receive')
        time.sleep(listenSeconds) 

# Print results
print ('')
print ('-------------------------------------------------------------')
if len(receivedPackets) > 0:
    print ('Packets received on presets:\n')
else:
    print ('No packets heard\n')
for result in receivedPackets:
    print (result)
print ('')
interface.close()
