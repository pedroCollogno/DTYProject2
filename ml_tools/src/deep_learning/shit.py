import math

n=100
p=1000

sum=0

for k in range(n+1):
    binomial=math.factorial(n)//(math.factorial(n-k)*math.factorial(k))
    print("binomial")
    print(binomial)
    total=((-1)**(n-k))*binomial*(k**p)
    print('total')
    print(total)
    sum+=total

print(sum)
app=n**p
print(sum/app)