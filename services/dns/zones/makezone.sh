cp db.orionet.re _ps

for i in `seq 254`
do
cat <<END >> _ps
\$ORIGIN $i.orionet.re.
@   IN  NS  nsx1.orion.matthieu-dev.xyz.
@   IN  NS  nsx2.orion.matthieu-dev.xyz.
END
done

for key in `ls Korionet.re*.key`
do
echo "\$INCLUDE $key">> _ps
done

dnssec-signzone -A -3 $(head -c 1000 /dev/random | sha1sum | cut -b 1-16) -N INCREMENT -o orionet.re -t _ps
rm _ps
mv _ps.signed db.orionet.re.signed
