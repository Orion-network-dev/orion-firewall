import toml
from utils import ip_bits_to_str, pairing

def main():
	# Reading the configuration file
	with open('config.toml', 'r') as f:
		config = toml.load(f)
	
	self_id: int = config['id']
	private_key: str = config['private_key']

	assert 0 < self_id <= 253, "Invalid id"

	orion_network_conf: str = ""
	orion_wireguard_conf: str = ""
	orion_wireguard_conf += f"[Interface]\n"
	orion_wireguard_conf += f"Address = 10.30.255.{self_id}/24\n"
	orion_wireguard_conf += f"PrivateKey = {private_key}\n"
	orion_wireguard_conf += f"Table = off\n"

	# If we need to listen, we simply add it to the wireguard config
	if 'listen' in config:
		orion_wireguard_conf += f"ListenPort = {config['listen']}\n"
	
	# For each peer we have
	for peer in config['peers']:
		peer_public_key: str = peer['public_key']
		peer_id: int = peer['id']
		# Name of the interface for the tunnel
		interface_name: str = f"tunnel{peer_id}"
		
		# We compute the interconnect id
		interconnect_id = pairing(peer_id,self_id)

		# All the Orion interconnect networks are in 172.16.0.0/15
		# From (172.10.0.0 - 172.16.255.255). We need a /15 network because the subnet id
		# is 16 bits long and we need anoter bit for two computers (/31 network point-to-point)
		subnet_bits = 172 << 24 | 16 << 16 | interconnect_id << 1

		# To ensure consistency, we choose the peer with the highest id for the higest ip
		self_address = ip_bits_to_str(subnet_bits if peer_id > self_id else subnet_bits + 1)

		mtu = 1456

		orion_network_conf += f"auto {interface_name}\n"
		orion_network_conf += f"iface {interface_name} inet tunnel\n"
		orion_network_conf += f"	mode gre\n"
		orion_network_conf += f"	address {self_address}\n"
		orion_network_conf += f"	netmask 255.255.255.254\n"
		orion_network_conf += f"	local 10.30.255.{self_id}\n"
		orion_network_conf += f"	endpoint 10.30.255.{peer_id}\n"
		orion_network_conf += f"	mtu {mtu}\n"

		orion_wireguard_conf += f"[Peer]\n"
		orion_wireguard_conf += f"PublicKey = {peer_public_key}\n"
		orion_wireguard_conf += f"AllowedIPs = 10.30.255.{peer_id}/32\n"
		orion_wireguard_conf += f"PersistentKeepalive = 25\n"

		if 'endpoint' in peer:
			orion_wireguard_conf += f"Endpoint = {peer['endpoint']}\n"


	with open('/etc/network/interfaces.d/01-orion.conf', 'w') as networkfile:
		networkfile.truncate(0)
		networkfile.write(orion_network_conf)
		networkfile.close()

	print("Network config file written.")

	with open('/etc/wireguard/orion.conf', 'w') as wireguard:
		wireguard.truncate(0)
		wireguard.write(orion_wireguard_conf)
		wireguard.close()

	print("Wireguard sucesfully written.")


if __name__ == "__main__":
	main()
