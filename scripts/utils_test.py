import unittest

from utils import pairing

class TestPairingFunction(unittest.TestCase):
    def test_pairing_function_valid(self):
        counter = {}
        for i in range(1,253):
            for j in range(1,253):
                uq = pairing(i,j)
                # Must be symetric u(a,b) = u(b,a)
                assert uq == pairing(j,i)
                # Count the number of time the pairing number appeared
                counter[uq] = (counter[uq] if uq in counter else 0) + 1
                # Verify our number if not 
                assert counter[uq] < 3, f"Duplicate pairing number {uq} for tuple=({i}, {j}) count={counter[uq]}"
                # Our number must bits in 16 bits
                assert uq < 0xffff
