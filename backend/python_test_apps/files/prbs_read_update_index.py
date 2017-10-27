file = open('prbs.txt', 'r')

n = int(file.readline())
a = [0]*n

for i,line in enumerate(file):
    a[i] = int(line)

file.close()
file = open('index.txt','r')
i=int(file.readline())
print i,a[i]

file.close()

i+=1
if (i==n):
    i=0
    
file = open('index.txt','w')
file.write(str(i))
file.close()

