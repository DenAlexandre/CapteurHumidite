from scapy.layers.l2 import ARP, Ether
from scapy.sendrecv import srp


adrIP = ""
url = "http://192.168.1.212?"
adrMAC = "2c:f4:32:54:a2:87"


class lanUtility:

	def get_ip_by_mac(mac_address):
		# Créer un paquet ARP pour demander l'adresse IP correspondant à l'adresse MAC donnée
		arp = ARP(pdst='2c:f4:32:54:a2:87')
		ether = Ether(dst="ff:ff:ff:ff:ff:ff")
		packet = ether/arp

		# Envoyer le paquet sur le réseau local et attendre une réponse
		result = srp(packet, timeout=3, verbose=0)[0]
		print (str(result))
		# Extraire l'adresse IP de la réponse
		return result[0][1].psrc

	def get_ip_address(mac_address):
		for host in socket.gethostbyname_ex(socket.gethostname())[2]:
			try:
				s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				s.connect((host, 9))
				arp = struct.pack('Hs4s4s', 1, b'\x00'*6, socket.inet_aton(host), mac_address)
				s.sendall(arp)
				ip_address = s.recv(20).strip()[20:24]
				return socket.inet_ntoa(ip_address)
			except Exception as exc:
				#self.controler.loggerCtrl.WriteLogger(const.LoggerTypeEnum.Error, str(exc))
				WriteFile(str(exc))

	def getip(mac_address):
		print(mac_address)
		arp_result = os.popen("arp -a " + mac_address).read()
		print(arp_result)
		ip_address = arp_result.split(" ")[1]
		print(ip_address)
		return ip_address


	#adrIP = get_ip_by_mac(adrMAC)
	ipaddress = get_ip_address(adrMAC)
	print(ipaddress)