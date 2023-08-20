def pairing(x: int, y: int) -> int:
   """
   Szudzik pairing function,
   Efficient pairing of two integers
   """
   if x < y:
      x, y = y,x

   return (x * x) + x + y
