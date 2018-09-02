import time

class spab_gen(object):
    def __init__(self,n):
        self.n = n
        self.reg = [1] * n
        self.counter = 0
        self.counter_top = 2**n
       
            
         # map the inputs to the function blocks
        self.spab_options = {
                   2 : self.spab_2,
                   3 : self.spab_3,
                   4 : self.spab_4,
                   5 : self.spab_5,
                   6 : self.spab_6,
                   7 : self.spab_7,
                   8 : self.spab_8,
                   9 : self.spab_9,
                   10 : self.spab_10
        }
    def print_reg(self):
        print(self.reg)
        
    # define the function blocks
    def spab_2(self):
        val = (self.reg[1]+self.reg[0]) % 2
        return val

    def spab_3(self):
        val = (self.reg[2]+self.reg[1]) % 2
        return val

    def spab_4(self):
        val = (self.reg[3]+self.reg[2]) % 2
        return val

    def spab_5(self):
        val = (self.reg[4]+self.reg[2]) % 2
        return val

    def spab_6(self):  
        val = (self.reg[5]+self.reg[4]) % 2
        return val
     
    def spab_7(self):       
        val = (self.reg[6]+self.reg[5]) % 2
        return val
     
    def spab_8(self):        
        val = (self.reg[7]+self.reg[5]+self.reg[4]+self.reg[3]) % 2
        return val
     
    def spab_9(self):        
        val = (self.reg[8]+self.reg[4]) % 2
        return val
     
    def spab_10(self):        
        val = (self.reg[9]+self.reg[6]) % 2
        return val
            
    def spab_reg(self):
        n = self.n
        val = self.spab_options[n]()

        spab_out = self.reg[n-1];      
        for i in range(n-1):
##            print i
            self.reg[n-i-1] = self.reg[n-i-2]
                    
        self.reg[0] = val;

        self.counter += 1
        if self.counter == self.counter_top:
            self.counter = 0
        return (self.counter, spab_out)

    def reset(self):
        self.reg = [1] * self.n
        self.counter = 0
        


