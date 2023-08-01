def pairing(x: int, y: int) -> int:
   """
   Szudzik pairing function,
   Efficient pairing of two integers
   """
   if x < y:
      x, y = y,x

   return (x * x) + x + y

def ip_bits_to_str(ip_bits: int) -> str:
   """
   Convert a binary ip address to it's text representation
   """
   p1 = (ip_bits >> 24)
   p2 = (ip_bits >> 16) & 0b11111111
   p3 = (ip_bits >> 8)  & 0b11111111
   p4 = ip_bits & 0b11111111
   return f"{p1}.{p2}.{p3}.{p4}"
