from decimal import Decimal

print(0.1+0.2)


print((Decimal(0.1).quantize()+Decimal(0.2).quantize()))