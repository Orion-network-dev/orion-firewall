setSecurityPollSuffix("")

-- Allow Requests from anywhere
setLocal('0.0.0.0:53');
addACL('0.0.0.0/0');

-- Configure a packet-cache for shared cache across upstreams.
packet_cache = newPacketCache(10000, {
	maxTTL=86400,
	minTTL=0,
	temporaryFailureTTL=60,
	staleTTL=60,
	dontAge=false
});

-- Register our local bind server to resolve our domains recursively.
newServer({ address = "172.80.0.3:53", pool = "resolve_domain" });

-- For each orion member, we add an upstream object
for index=1,254 do

	-- Use lazy checking to avoid traffic across the network
	newServer({
		address = "10.30." .. index.. ".255",
		healthCheckMode='lazy',
		checkInterval=10000,
		lazyHealthCheckFailedInterval=30,
		rise=2,
		maxCheckFailures=3,
		lazyHealthCheckThreshold=30,
		lazyHealthCheckSampleSize=100,
		lazyHealthCheckMinSampleCount=10,
		lazyHealthCheckMode='TimeoutOnly',
		pool=index,
	});
	getPool(index):setCache(packet_cache);
	
	-- Match *.{index}.orionet.re and *.{index}.30.10.in-addr.arpa to our upstream
	suffix_node=newSuffixMatchNode();
	suffix_node:add(index .. ".orionet.re");
	suffix_node:add(index .. ".30.10.in-addr.arpa");

	-- We redirect all requests to the upstream
	-- Except DS records which need to be handled using our local bind
	-- Which stores the DS records for the members.
	addAction(
		AndRule{
			SuffixMatchNodeRule(suffix_node),
			NotRule(QTypeRule(DNSQType.DS))
		},
		PoolAction(index)
	);
end

collectgarbage();


-- Route *.orionet.re to our bind server
suffix_node=newSuffixMatchNode();
suffix_node:add("orionet.re");
getPool("resolve_domain"):setCache(packet_cache);

-- Since this server *can* also be used as a recursive server
-- when used wihin our local address space.
addAction(
	{
		"10.0.0.0/8",
		"192.168.0.0/16",
		"172.16.0.0/12",
		"127.0.0.0/8"
	},
	PoolAction("resolve_domain")
);

addAction(
	SuffixMatchNodeRule(suffix_node),
	PoolAction("resolve_domain")
)