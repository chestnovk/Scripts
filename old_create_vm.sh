#!/bin/bash
#$HOST_NAME - a name of VM
#$HOST_IP - a ip of VM
#$MASK - IP MASK for HOST_IP
#$VAMN_IP - a ip of Virtuozzo Automator
#$STORAGE_UI_IP - a ip of Storage UI
#$VNC_PORT - port which will be used by VM. 
#$VNC_MODE - a mode for VNC port. Can be "--vnc-mode auto" or "--vnc-mode manual" I temporary disable this due to reason that auto is better
#$VNC_PASSWORD - always no
#VA_REGISTER - if you need to register you node in VAMN
#UI_REGISTER - if you need to register your node in STORAGE
#
#
#Set some basic parameters:
#Home dir contains /mounts /iso etc.
BASE_DIR="/root/kchestnov"
#Dir to mount remote ISO
MOUNT_DIR="mounts"
#Dir to store libvirt domain.xml
VM_CONFIG_DIR="vms"
#our DNS and GW
DNS="10.30.0.27"
GW="172.16.56.1"
MASK="255.255.254.0"
VNC_MODE="auto"
#Path to HTTP server and kickstarts for simple node and UI node
UI_KICKSTART='http://172.16.56.80/ks/ui_kickstart.cfg'
COMPUTE_KICKSTART='http://172.16.56.80/ks/compute_kickstart.cfg'

#Check the keys and set the enviroment

while [ -n "$1" ]
do
case "$1" in
--name) HOST_NAME=$2;;
--node-ip) HOST_IP=$2;;
#--mask) MASK=$2;;
#--vnc-mode) VNC_MODE=$2;;
#--vnc-port) VNC_PORT=$2;;
--ui) KS=$UI_KICKSTART;;
--compute) KS=$COMPUTE_KICKSTART;;
--vamn-ip) VAMN_IP=$2;;
--storage-ui-ip) STORAGE_UI_IP=$2;;
--iso) PATH_TO_ISO=$2;;
--va-register) VA_REGISTER="yes";; 
--ui-register) UI_REGISTER="yes";;
--ui-token) UI_TOKEN=$2;;
--disk-number) DISK_NUM=$2;;
--backend-net) BACKEND_NET=$2;;
--) shift
break;;
*) ;;
esac
shift
done


#Simple checking that you have inpute all the parameers and show them to you.
#Actually i don't care that smb can write it in a "for" loop. If you can - go ahead and improve it.

function usage(){
	echo ""
	echo "Path for VMs configs, etc configured by value of BASE_DIR. Current location is BASE_DIR=$BASE_DIR"
	echo "In the BASE_DIR there is a MOUNT_DIR which uses to store mountpoint for different .iso. Current location is $BASE_DIR/$MOUNT_DIR"
	echo "A folder uses to store startup and working configs: $BASE_DIR/$VM_CONFIG_DIR"
	echo ""
	echo "Kickstart files are here: "
	echo "UI_KICKSTART = $UI_KICKSTART"
	echo "COMPUTE_KICKSTART = $COMPUTE_KICKSTART"
	echo ""
	echo "Usage: ${0##*/} keys: --name, --node-ip, --ui/--compute, --vamn-ip, --storage-ui-ip, --va-register, --ui-register, --ui-token, --iso"
}

function check_parameters(){

echo "Checking parameters..."
echo ""

if  [ -z ${HOST_NAME+x} ]; then
	echo "--name is not set"
	usage;
	exit;
fi

if  [ -z ${HOST_IP+x} ]; then
	echo "--node-ip is not set"
	usage;
	exit;
fi

if  [ -z ${MASK+x} ]; then
	echo "--mask is not set"
	usage;
	exit;
fi
#This check still exist but values are set without --vnc-passwd. This may be changed if future
if  [ -z ${VNC_MODE+x} ]; then
	echo "--vnc-mode is not set"
	usage;
	exit;
else 
	if [ "$VNC_MODE" = "auto" ]; then
		VNC_MODE="--vnc-mode auto --vnc-nopasswd"
	elif [ "$VNC_MODE" = "manual" ]; then
		if  [ -z ${VNC_PORT+x} ]; then
			echo "--vnc-port is not set"
			usage;
			exit;
		else 
			[ "$VNC_PORT" -lt 5900 -o "$VNC_PORT" -gt 6900 ] && { echo "VNC port '$VNC_PORT' is out of bounds."; exit 1; }
			VNC_MODE="--vnc-mode manual --vnc-port $VNC_PORT --vnc-nopasswd"
		fi
	else
		echo "--vnc-mode should be set to 'auto' or 'manual'. "; usage;  exit
	fi
fi


if  [ -z ${KS+x} ]; then
	echo "--ui or --compute is not set"
	usage;
	exit;
else 
	#IF KS is set to UI we need to check whether VAMN_IP and STORAGE_UI_IP was specified. The same for --register
	if [ $KS == $UI_KICKSTART ]; then
	
		if  [ -z ${VAMN_IP+x} ]; then
			echo "--vamn-ip is not set"
			usage;
			exit;
		fi

		if  [ -z ${STORAGE_UI_IP+x} ]; then
			echo "--storage-ui-ip is not set"
			usage;
			exit;
		fi
	fi

	#IF KS is set to COMPUTE we need to check whether we need to register it in VA or UI (--va-register, --ui-register) and check if related IP was set.
	if [ $KS == $COMPUTE_KICKSTART ]; then
		
		if [ "$VA_REGISTER" = "yes" ]; then
			
			if  [ -z ${VAMN_IP+x} ]; then
				echo "--vamn-ip is not set."
				usage;
				exit;
			fi
		fi

		if [ "$UI_REGISTER" = "yes" ]; then
				
			if  [ -z ${STORAGE_UI_IP+x} ]; then
				echo "--storage-ui-ip is not set"
				usage;
				exit;
			fi
			
			if [ -z ${UI_TOKEN+x} ]; then
				echo "--token is not set"
				usage;
				exit;
			fi
		fi
		
	fi

fi

#Need to add one more option: --register, if the flag is set we can provide with storage-ui token and VAMN location and password and automatically register the node in a cluster
#Will add later.


if  [ -z ${PATH_TO_ISO+x} ]; then
	echo "--iso is not set"
	usage;
	exit;
fi

if  [ -z ${DISK_NUM+x} ]; then
	echo "--disk-number is not set"
	#usage;
	#exit;
fi

if  [ -z ${BACKEND_NET+x} ]; then
	echo "--backend-net is not set"
	#usage;
	#exit;
fi

echo "##############################"
echo "Parameters which will be used:"
echo "HOST_NAME is set to $HOST_NAME"
echo "HOST_IP is set to $HOST_IP"
echo "MASK is set to $MASK"
echo "VNC_MODE is set to $VNC_MODE"
echo "KS is set to $KS"
echo "VAMN_IP is set to $VAMN_IP"
echo "STORAGE_UI_IP is set to $STORAGE_UI_IP"
echo "ISO is set to $PATH_TO_ISO"
echo "VA_REGISTER is set to $VA_REGISTER"
echo "UI_REGISTER is set to $UI_REGISTER"
echo "UI_TOKEN is set to $UI_TOKEN"
echo "DISK_NUMBER is set to $DISK_NUM"
echo "BACKEND_NET is set to $BACKEND_NET"
echo "##############################"
echo ""

while true ; do
	echo -n "Do you want to proceed? [Y/n]"
	read answer
	if [ "$answer" = "Y" ]; then
		echo "Okay then"
		break
	elif [ "$answer" = "n" ]; then
		echo "Okay, stop right here"
		exit 
	else 
		echo "I am not sure I catch you, try again"
	fi
done
}


#Need to find the ISO file according to the --iso and mount it to $MOUNT_DIR
function mount_iso(){
	echo "Start locating of vmlinuz and initrd"
	#Parse the path and get filename
	ISO_NAME=${PATH_TO_ISO##*/}
	
	#Remove .iso
	MOUNT_POINT_NAME=${ISO_NAME%.*}

	#Check if DIR exist if yes tell about it, if no then create one.

	#echo "initrd should be here: $BASE_DIR/$MOUNT_DIR/$MOUNT_POINT_NAME/images/pxeboot/initrd.img"
	#echo "vmlinuz should be  here: $BASE_DIR/$MOUNT_DIR/$MOUNT_POINT_NAME/images/pxeboot/vmlinuz"
	
	[ -e $BASE_DIR/$MOUNT_DIR/$MOUNT_POINT_NAME ] && echo $BASE_DIR/$MOUNT_DIR/$MOUNT_POINT_NAME already exists || mkdir $BASE_DIR/$MOUNT_DIR/$MOUNT_POINT_NAME
	
	#Check if initrd and vmlinuz available
	if [ -e $BASE_DIR/$MOUNT_DIR/$MOUNT_POINT_NAME/images/pxeboot/initrd.img ] && [ -e $BASE_DIR/$MOUNT_DIR/$MOUNT_POINT_NAME/images/pxeboot/vmlinuz ]; then
		echo "ISO was already mounted and initrd located here: $BASE_DIR/$MOUNT_DIR/$MOUNT_POINT_NAME/images/pxeboot/initrd.img"
		echo "ISO was already mounted and vzlinuz located here: $BASE_DIR/$MOUNT_DIR/$MOUNT_POINT_NAME/images/pxeboot/vmlinuz"
	else
		mount -o loop $PATH_TO_ISO $BASE_DIR/$MOUNT_DIR/$MOUNT_POINT_NAME;
		if [ $? != 0 ]; then
                       	echo "MOUNT CODE IS : $? AHTUNG_PANIC_!11"
               		exit
		else
			if [ -e $BASE_DIR/$MOUNT_DIR/$MOUNT_POINT_NAME/images/pxeboot/initrd.img ] && [ -e $BASE_DIR/$MOUNT_DIR/$MOUNT_POINT_NAME/images/pxeboot/vmlinuz ]; then
                		echo "ISO was mounted and initrd located here: $BASE_DIR/$MOUNT_DIR/$MOUNT_POINT_NAME/images/pxeboot/initrd.img"
                		echo "ISO was mounted vzlinuz located here: $BASE_DIR/$MOUNT_DIR/$MOUNT_POINT_NAME/images/pxeboot/vmlinuz"
			else 
				echo "Mounted ISO does not contain initrd or vzlinuz, please check manually"
				echo "ISO name is $ISO"
				echo "Mountpoint dir is $BASE_DIR/$MOUNT_DIR/$MOUNT_POINT"							
               		fi
			
		fi
	fi

	INITRD=$BASE_DIR/$MOUNT_DIR/$MOUNT_POINT_NAME/images/pxeboot/initrd.img
	KERNEL=$BASE_DIR/$MOUNT_DIR/$MOUNT_POINT_NAME/images/pxeboot/vmlinuz
}

#Main part, creating VM
function create_vm(){
	echo "Creating VM..."

	#CHECK IF THE VM EXISTS
	prlctl list -a $HOST_NAME >> /dev/null
	if [ $? == 0  ]; then
		echo "VM with the same name already exist"
		exit
	fi
	
	echo "prlctl create $HOST_NAME --vmtype vm --distribution vzlinux7"
	prlctl create $HOST_NAME --vmtype vm --distribution vzlinux7 >> /dev/null
	
	#Add IPs to the Description
	if [ $KS == $UI_KICKSTART ]; then
		echo "prlctl set $HOST_NAME --description "extip:[$HOST_IP $VAMN_IP $STORAGE_UI_IP]""
		prlctl set $HOST_NAME --description "extip:[$HOST_IP $VAMN_IP $STORAGE_UI_IP]" >> /dev/null
	else 
		echo "prlctl set $HOST_NAME --description "extip:[$HOST_IP]""
		prlctl set $HOST_NAME --description "extip:[$HOST_IP]" >> /dev/null
	fi

	#Disable filters
	echo "prlctl set $HOST_NAME --device-set net0 --ipfilter no --macfilter no --preventpromisc no"
	prlctl set $HOST_NAME --device-set net0 --ipfilter no --macfilter no --preventpromisc no >> /dev/null

	#If you have choosen "auto its ok. if manually, $VNC_PORT becomes like --vnc-mode manual --vnc-port 5901 VNC_PASSWORD not used"
	
	echo "prlctl set $HOST_NAME $VNC_MODE"
	prlctl set $HOST_NAME $VNC_MODE >> /dev/null

	#Assign cdrom
	echo "prlctl set $HOST_NAME --device-set cdrom0 --connect --image $PATH_TO_ISO"	
	prlctl set $HOST_NAME --device-set cdrom0 --connect --image $PATH_TO_ISO >> /dev/null
	
	echo "prlctl set $HOST_NAME --nested-virt on"
	prlctl set $HOST_NAME --nested-virt on >> /dev/null
	echo "Configuration finised"


	for i in $(seq 1 $DISK_NUM)
        do
                echo "prlctl set $HOST_NAME --device-add hdd --size 100G"
                prlctl set $HOST_NAME --device-add hdd --size 100G >> /dev/null
                echo "Configuration for hdd${i} finised"
        done

	echo "prlctl set $HOST_NAME --device-add net --network $BACKEND_NET"
	prlctl set $HOST_NAME --device-add net --network $BACKEND_NET >> /dev/null
	echo "Configuration finised"
}

function append_qemu_commandline(){
	LABEL=$MOUNT_POINT_NAME
	#I used STORAGE_UI_IP and VAMN_IP. Now I gonna not to use them
	APPEND="inst.stage2=hd:LABEL=$LABEL ui ksdevice=eth0 ip=$HOST_IP netmask=$MASK ks=$KS netmask=$MASK vamn=$VAMN_IP uiip=$STORAGE_UI_IP hostname=$HOST_NAME va_register=$VA_REGISTER ui_register=$UI_REGISTER token=$UI_TOKEN"
	
	# here we will put VM's dumpxml file to "vms" folder to somehow change it
	#touch $BASE_DIR/$VM_CONFIG_DIR/$HOST_NAME
	#VM_BASE_CONFIG="$BASE_DIR/$VM_CONFIG_DIR/$HOST_NAME"
	#VM_CONFIG="$BASE_DIR/$VM_CONFIG_DIR/$HOST_NAME'_temp'"

	#Copy file to modify it
	VM_BASE_CONFIG="$BASE_DIR/$VM_CONFIG_DIR/$HOST_NAME"
	VM_CONFIG="${VM_BASE_CONFIG}_temp"

	touch $VM_BASE_CONFIG
	touch $VM_CONFIG
	
	virsh dumpxml $HOST_NAME > $VM_BASE_CONFIG
	virsh dumpxml $HOST_NAME > $VM_CONFIG
	

	# we should add "-kernel", "-initdr" and "-append" parameters to the <qemu:commandline>
	# firstly, let's find the string number
	num=`sed -n "/<qemu:commandline>/=" $VM_CONFIG`
	# add this strings in <qemu:commandline> container 
	sed -i "$num a\    <qemu:arg value='$KERNEL'/>" $VM_CONFIG
	sed -i "$num a\    <qemu:arg value='-kernel'/>" $VM_CONFIG
	sed -i "$num a\    <qemu:arg value='$APPEND'/>" $VM_CONFIG
	sed -i "$num a\    <qemu:arg value='-append'/>" $VM_CONFIG
	sed -i "$num a\    <qemu:arg value='$INITRD'/>" $VM_CONFIG
	sed -i "$num a\    <qemu:arg value='-initrd'/>" $VM_CONFIG

	#Some of values are dublicate. Just to simplify kickstart, temp added to APPEND
	#sed -i "$num a\    <qemu:arg value='$HOST_IP'/>" $VM_CONFIG
	#sed -i "$num a\    <qemu:env name='HOST_IP'/>" $VM_CONFIG
	#sed -i "$num a\    <qemu:arg value='$MASK'/>" $VM_CONFIG
	#sed -i "$num a\    <qemu:env name='MASK'/>" $VM_CONFIG
	#sed -i "$num a\    <qemu:arg value='$VAMN_IP'/>" $VM_CONFIG
	#sed -i "$num a\    <qemu:env name='VAMN_IP'/>" $VM_CONFIG
	#sed -i "$num a\    <qemu:arg value='$STORAGE_UI_IP'/>" $VM_CONFIG
	#sed -i "$num a\    <qemu:env name='STORAGE_UI_IP'/>" $VM_CONFIG
}

function start_vm(){
	
	echo "Starting the VM"
	echo ""
	#We need first define _temp config then wait until the VM will be in stopped state, then define original config and start VM
	virsh define "$BASE_DIR/$VM_CONFIG_DIR/${HOST_NAME}_temp"
	virsh start $HOST_NAME

	echo "Checking VNC"
	#Waiting for finishing
	sleep 20

	echo "VM started. VNC config:"
	prlctl list -if $HOST_NAME | egrep "Name|Description|Remote"	

	while [ true ]
	do
   		echo "Checking"      #Executed as long as condition is true and/or, up to a disaster-condition if any.
   		OUT=$(prlctl list -a $HOST_NAME | awk '{print $2}' | tail -n 1)
  		
		if [ $OUT == "stopped" ]
  		then

		break       	   #Abandon the while loop.
  		fi
		echo "Waiting for additional 120 seconds"
		echo "The $HOST_NAME is in $OUT state"          #While good and, no disaster-condition.
  		sleep 120
	done

	
	virsh define "$BASE_DIR/$VM_CONFIG_DIR/$HOST_NAME"
	prlctl start  $HOST_NAME
	echo "Last check"
	sleep 10
	echo "You can now login to the VM:"
	prlctl list -if $HOST_NAME | egrep "Name|Description|Remote"

}



check_parameters
mount_iso
create_vm
append_qemu_commandline
start_vm
#!/bin/bash
#If there is a several VM then for i in $NUM; do (generate parameters for VM  $HOST_NAME_$NUM and $HOST_IP) append command line , start 
create_vm
append_qemu_commandline
start_vm

#And finish here
check_config
