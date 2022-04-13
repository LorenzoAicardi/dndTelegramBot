class Wealth:

    def __init__(self):
        self.cp = 0
        self.sp = 0
        self.ep = 0
        self.gp = 0
        self.pp = 0

    # def convert(self):

    def addCp(self, cp):
        self.cp = self.cp + cp

    def addSp(self, sp):
        self.sp = self.sp + sp

    def addEp(self, ep):
        self.ep = self.ep + ep

    def addGp(self, gp):
        self.gp = self.gp + gp

    def addPp(self, pp):
        self.pp = self.pp + pp

    def rmCp(self, cp):
        self.cp = self.cp - cp

    def rmSp(self, sp):
        self.sp = self.sp - sp

    def rmEp(self, ep):
        self.ep = self.ep - ep

    def rmGp(self, gp):
        self.gp = self.gp - gp

    def rmPp(self, pp):
        self.pp = self.pp - pp
