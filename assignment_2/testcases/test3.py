n = inPut()
i = 0
t = i < n
ans = 0
curr = 2
while(t):
    div = 2
    k = div < curr
    isPrime = True
    while(k):
        rem = (curr%div)
        divi = (rem == 0)
        if(divi):
            isPrime = False
        curr+=1
        k = div < curr
        
    if(isPrime):
        i+=1
        ans = curr
    curr += 1
    t = i < n
    
output(ans)
